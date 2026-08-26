"""Render the whole site to static files for a static host.

Every page here is anonymous and identical for all visitors: there are no models,
no session, no forms and no ``{% csrf_token %}``, and the image processing runs
entirely in the browser. ``EdgeCacheMiddleware`` already says as much by marking
each response ``s-maxage=86400``. So the Python process is only ever rendering
templates that could equally well have been rendered once, at build time.

This command does exactly that: it walks the site with Django's test client and
writes the result as a directory of files. What it emits is a drop-in for what
the WSGI app used to serve, including the parts that normally arrive as response
*headers* rather than bodies:

* ``_headers`` carries the CSP, the Permissions-Policy and — the reason this
  cannot just be a blanket rule — the per-page ``COOP``/``COEP`` isolation that
  ``SecurityHeadersMiddleware`` applies to ``ISOLATED_VIEWS`` only. It is
  generated *from* that same set, so the two cannot drift apart.
* ``_redirects`` carries the permanent redirects declared in ``urls.py``.

Deliberately NOT emitted: ``/api/stats/``. It is the site's only endpoint that
does real work per request, and it is inert anyway (Upstash is unconfigured, so
it answers ``{"enabled": false}``). ``stats.js`` posts to it fire-and-forget
behind a ``.catch()``, so its absence is invisible. Restoring it on a static host
means porting it to a host function; nothing else here needs one.

Usage::

    DJANGO_SETTINGS_MODULE=config.settings.production python manage.py prerender
    python manage.py prerender --output _site
"""
import shutil
from pathlib import Path
from urllib.parse import urlsplit

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.templatetags.static import static
from django.test import Client
from django.urls import reverse
from django.utils import translation

from config.middleware import COEP, COOP, CSP, ISOLATED_VIEWS, PERMISSIONS_POLICY
from remover.translations import LANGUAGES

# Routes that answer with a file rather than a page. These are not in the
# sitemap (they are not content), but every one of them is fetched by something
# — a crawler, the browser, a search-console verification check — so they have to
# exist on disk. The two verification files are the ones worth naming: losing
# either silently un-verifies the site with that engine.
ROOT_FILES = [
    "/robots.txt",
    "/sitemap.xml",
    "/llms.txt",
    "/ads.txt",
    "/sw.js",
    "/healthz",
    "/yandex_ee6a725348d1a333.html",
]

# The one root file that base.html links with `{% url %}`, which is language
# aware — so every Portuguese page asks for /pt/manifest.webmanifest and every
# Spanish one for /es/manifest.webmanifest. Those resolve under i18n_patterns
# today; emit them, or two thirds of the site links a 404 and loses its PWA
# install prompt. The rest of ROOT_FILES stay root-only: robots.txt and
# sitemap.xml are read at the root by spec, and shipping prefixed copies would
# just offer crawlers a duplicate sitemap.
LOCALIZED_ROOT_FILES = ["/manifest.webmanifest"]

# WhiteNoise pre-compresses everything at collectstatic time. That was the right
# trade when Python served the bytes; a CDN compresses on its own and charges us
# a file for each of these, so they are dead weight in the upload. staticfiles.json
# is build-time-only state and has no business being public either.
STATIC_SKIP_SUFFIXES = (".gz", ".br")
STATIC_SKIP_NAMES = {"staticfiles.json"}


class Command(BaseCommand):
    help = "Render every URL to static files for a static host (default: ./_site)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output", default="_site",
            help="Directory to write into. Emptied first. Default: ./_site",
        )
        parser.add_argument(
            "--skip-static", action="store_true",
            help="Do not copy STATIC_ROOT (useful when iterating on templates).",
        )

    def handle(self, *args, **options):
        # Imported here, not at module scope: remover.views pulls in the page
        # content modules, and a management command that merely fails to parse
        # should not need all of them loaded.
        from remover.views import SITEMAP_PATHS

        out = Path(options["output"]).resolve()
        if out == Path(settings.BASE_DIR).resolve():
            raise CommandError(f"--output {out} is the project root; refusing to empty it.")

        # The test client defaults to `testserver`, which production ALLOWED_HOSTS
        # will not have. Using the real host instead keeps this working against
        # production settings with no special-casing, and `secure=True` matters
        # just as much: SECURE_SSL_REDIRECT would otherwise turn every render
        # into a 301 and we would write ~300 redirect stubs.
        host = urlsplit(settings.SITE_URL).hostname or "testserver"
        if host not in settings.ALLOWED_HOSTS and "*" not in settings.ALLOWED_HOSTS:
            settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + [host]
        client = Client(SERVER_NAME=host, headers={"accept-language": "en"})

        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)

        paths = self._paths(SITEMAP_PATHS)
        written = self._render(client, paths, out)
        self._render_404(client, out)
        self._write_headers(out)
        self._write_redirects(out)
        copied = 0 if options["skip_static"] else self._copy_static(out)

        self.stdout.write(self.style.SUCCESS(
            f"Wrote {written} pages + {copied} static files to {out}"
        ))

    def _paths(self, sitemap_paths):
        """Every URL to render: each path unprefixed, then once per language.

        Note this renders the language-prefixed twin of a page even where that
        language has no translation for it. Those URLs are `noindex` and nothing
        links to them (the footer switcher sends an untranslated language to its
        home page instead), but they resolve and return 200 on the current host,
        and some are already in Google's index as crawled-and-discarded. A host
        migration should not turn a 200 into a 404; the cost is a few hundred KB.
        """
        paths = list(sitemap_paths)
        for lang in LANGUAGES:
            paths.extend(f"/{lang}{p}" for p in sitemap_paths)
        paths.extend(ROOT_FILES)
        paths.extend(LOCALIZED_ROOT_FILES)
        for lang in LANGUAGES:
            paths.extend(f"/{lang}{p}" for p in LOCALIZED_ROOT_FILES)
        # The IndexNow key file's URL is derived from the key, so it moves when
        # the key is rotated. Build it the same way urls.py does.
        paths.append(f"/{settings.INDEXNOW_KEY}.txt")
        return paths

    def _render(self, client, paths, out):
        written = 0
        for path in paths:
            response = client.get(path, secure=True)
            if response.status_code != 200:
                raise CommandError(
                    f"{path} returned {response.status_code}; expected 200. "
                    "Prerender aborted rather than shipping a hole in the site."
                )
            self._write(out, path, response.content)
            written += 1
        return written

    def _render_404(self, client, out):
        """Cloudflare Pages serves /404.html for an unmatched path.

        Rendered rather than written by hand so it stays whatever Django's 404 is
        today; if a branded 404.html template is added later this picks it up for
        free.
        """
        response = client.get("/this-path-does-not-exist/", secure=True)
        if response.status_code != 404:
            raise CommandError(
                f"Expected a 404 probe to 404, got {response.status_code}."
            )
        (out / "404.html").write_bytes(response.content)

    def _write(self, out, path, content):
        """Map a URL to a file. `/convert/` -> `convert/index.html`."""
        rel = path.lstrip("/")
        target = out / "index.html" if not rel else (
            out / rel / "index.html" if rel.endswith("/") else out / rel
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    # --- headers -------------------------------------------------------------

    def _isolated_paths(self):
        """The URLs that must be cross-origin isolated, in every language.

        Read straight off `ISOLATED_VIEWS` so this file cannot fall out of step
        with the middleware: adding a tool to that set is still the only edit
        needed to isolate it. Getting this wrong is not a visible error — the
        page still works, it just silently loses SharedArrayBuffer and drops to
        the single-threaded WASM backend, i.e. the 2-4x slowdown we bought the
        isolation to avoid.
        """
        with translation.override("en"):
            base = sorted(reverse(f"remover:{name}") for name in ISOLATED_VIEWS)
        return base + [f"/{lang}{p}" for lang in LANGUAGES for p in base]

    def _write_headers(self, out):
        lines = [
            "# Generated by `manage.py prerender` — do not edit by hand.",
            "# Mirrors config/middleware.py (CSP, Permissions-Policy, COOP/COEP)",
            "# and the security settings Django applies in production.",
            "",
            "/*",
            f"  Content-Security-Policy: {CSP}",
            f"  Permissions-Policy: {PERMISSIONS_POLICY}",
            f"  X-Frame-Options: {settings.X_FRAME_OPTIONS}",
            "  X-Content-Type-Options: nosniff",
            f"  Referrer-Policy: {settings.SECURE_REFERRER_POLICY}",
            f"  Strict-Transport-Security: max-age={settings.SECURE_HSTS_SECONDS};"
            " includeSubDomains; preload",
            "",
        ]

        lines += [
            "# Cross-origin isolation: unlocks SharedArrayBuffer so onnxruntime-web",
            "# can use its threaded + SIMD backend. Scoped to the tool pages only —",
            "# COEP would block the AdSense frames on the landing pages.",
            "",
        ]
        for path in self._isolated_paths():
            lines += [path, f"  Cross-Origin-Opener-Policy: {COOP}",
                      f"  Cross-Origin-Embedder-Policy: {COEP}", ""]

        static_url = settings.STATIC_URL.strip("/")
        lines += [
            "# Content-hashed names (see config/storage.py) — safe to pin forever.",
            "# This is the job WhiteNoise used to do.",
            "",
            f"/{static_url}/*",
            "  Cache-Control: public, max-age=31536000, immutable",
            "",
            "# The worker must never be served stale or a deploy cannot roll out.",
            "",
            "/sw.js",
            "  Cache-Control: no-cache",
            "",
        ]
        (out / "_headers").write_text("\n".join(lines))

    def _write_redirects(self, out):
        """The redirects urls.py declares, restated for the host.

        `/portrait-mode/` is a merged tool whose URL is still indexed, so its 301
        carries real link equity and must survive the move.
        """
        lines = [
            "# Generated by `manage.py prerender` — do not edit by hand.",
            "",
        ]
        merged = "/portrait-mode/"
        with translation.override("en"):
            blur = reverse("remover:blur")
        for prefix in ("",) + tuple(f"/{lang}" for lang in LANGUAGES):
            lines.append(f"{prefix}{merged}  {prefix}{blur}  301")
        # urls.py answers /favicon.ico with a redirect to the hashed static file;
        # resolve it here so the target matches the build we are shipping.
        lines.append(f"/favicon.ico  {static('img/favicon.ico')}  302")
        lines.append("")
        (out / "_redirects").write_text("\n".join(lines))

    # --- static assets -------------------------------------------------------

    def _copy_static(self, out):
        source = Path(settings.STATIC_ROOT)
        if not source.is_dir():
            raise CommandError(
                f"STATIC_ROOT ({source}) does not exist. Run collectstatic first."
            )
        target = out / settings.STATIC_URL.strip("/")
        copied = 0
        for path in source.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix in STATIC_SKIP_SUFFIXES or path.name in STATIC_SKIP_NAMES:
                continue
            destination = target / path.relative_to(source)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
            copied += 1
        return copied
