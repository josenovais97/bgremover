"""Submit this site's URLs to IndexNow, so Bing and Yandex crawl them now.

Why this exists: Search Console showed ~34 real pages sitting in "Discovered —
currently not indexed", i.e. found and then deprioritised, which is what a crawler
does to a domain with no authority. IndexNow sidesteps the queue for the engines
that support it by pushing the URLs instead of waiting to be pulled.

Google does NOT participate. This helps Bing (and DuckDuckGo, Ecosia and Yahoo,
which it feeds) and Yandex. Nothing here changes anything about Google.

Usage::

    python manage.py indexnow                  # every URL in the sitemap
    python manage.py indexnow /sticker-maker/  # just these paths
    python manage.py indexnow --dry-run        # show the payload, send nothing
"""
import json
import urllib.error
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

# One endpoint is enough: participating engines share submissions with each other,
# so pinging api.indexnow.org reaches Bing and Yandex both. Submitting the same
# URL set to several endpoints is explicitly discouraged by the spec.
ENDPOINT = "https://api.indexnow.org/IndexNow"

# The spec's own ceiling for a single request.
MAX_URLS = 10_000


class Command(BaseCommand):
    help = "Submit URLs to IndexNow (Bing + Yandex). Defaults to the whole sitemap."

    def add_arguments(self, parser):
        parser.add_argument(
            "paths", nargs="*",
            help="Site-relative paths to submit (default: every path in the sitemap).",
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Print what would be sent without contacting the API.",
        )

    def handle(self, *args, **options):
        from remover.views import SITEMAP_PATHS, translated_languages

        site_url = settings.SITE_URL.rstrip("/")
        if not site_url.startswith("https://"):
            # IndexNow verifies ownership by fetching the key file over the same
            # host it was given. A localhost default would fail that fetch, and a
            # failed submission is reported as success by the API, so refuse here
            # rather than let it look like it worked.
            raise CommandError(
                f"SITE_URL is {site_url!r}; IndexNow needs the real https:// host. "
                "Run this against production settings."
            )

        if options["paths"]:
            paths = [p if p.startswith("/") else f"/{p}" for p in options["paths"]]
        else:
            # The same expansion the sitemap does: a path plus one prefixed URL
            # per language that really translates it. Untranslated prefixes are
            # noindex, so submitting them would ask a crawler to spend budget on
            # pages we have told it to ignore.
            paths = []
            for path in SITEMAP_PATHS:
                paths.append(path)
                paths.extend(f"/{lang}{path}" for lang in translated_languages(path))

        urls = [f"{site_url}{p}" for p in paths][:MAX_URLS]
        payload = {
            "host": site_url.removeprefix("https://"),
            "key": settings.INDEXNOW_KEY,
            "keyLocation": f"{site_url}/{settings.INDEXNOW_KEY}.txt",
            "urlList": urls,
        }

        if options["dry_run"]:
            self.stdout.write(f"{len(urls)} URLs would go to {ENDPOINT}")
            self.stdout.write(f"  key file: {payload['keyLocation']}")
            for u in urls[:5]:
                self.stdout.write(f"  {u}")
            if len(urls) > 5:
                self.stdout.write(f"  … and {len(urls) - 5} more")
            return

        body = json.dumps(payload).encode()
        request = urllib.request.Request(
            ENDPOINT, data=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                status = response.status
        except urllib.error.HTTPError as exc:
            # 403 almost always means the key file did not verify — the most
            # common failure, and worth naming rather than printing a bare code.
            hint = (
                f" — check that {payload['keyLocation']} returns exactly the key"
                if exc.code == 403 else ""
            )
            raise CommandError(f"IndexNow rejected the submission: {exc.code} {exc.reason}{hint}")
        except urllib.error.URLError as exc:
            raise CommandError(f"Could not reach IndexNow: {exc.reason}")

        # 200 = accepted, 202 = accepted but the key is still being validated.
        self.stdout.write(self.style.SUCCESS(f"Submitted {len(urls)} URLs — HTTP {status}"))
