"""Static files storage.

Content-hashed filenames exist for one reason: they let WhiteNoise serve every
asset with ``Cache-Control: max-age=315360000, public, immutable`` (ten years —
its own default for a name it recognises as versioned). Without them it can only
send ``max-age=60`` — a name like ``app.js`` may mean something different after
the next deploy, so it has to keep asking. That was measurably costing us:
a repeat visitor re-validated *every* file a minute after their last visit, and
the homepage alone carries ~50 images plus the JS and CSS. Bytes were saved by
the ETags; the round-trips were not.

The reason this app did not already hash was a real one. It runs on a serverless
host where static files are built in a separate step from the Python function,
so a strict manifest storage would raise ``ValueError: Missing staticfiles
manifest entry`` at render time — a 500 on every page — if ``staticfiles.json``
ever failed to ship with the function.

``manifest_strict = False`` removes that failure mode: a name the manifest does
not know is hashed on the spot from the file itself rather than raising, so a
missing manifest costs some per-request work on a page that still renders and
still gets correct URLs.

The one path that leaves is the file being missing too — Django then raises
``ValueError: The file could not be found``, which would be a 500 where the old
non-manifest storage simply emitted a URL that 404s. That is a worse failure for
no benefit (the site is unusable either way if the static build did not ship), so
``hashed_name`` below degrades that case to the plain name as well.

``support_js_module_import_aggregation`` matters here because the tool modules
import shared code as siblings (``import { removalConfig } from './accel.js'``).
Django does not rewrite those specifiers unless asked to, so the hashed
``app.<hash>.js`` would import the *unhashed* ``accel.js``: still a working URL —
``collectstatic`` keeps the originals — but served ``max-age=60``, and absent from
the service worker's precache list (which names the hashed URLs), so an offline
first visit would fail to import it. With the flag on, every sibling import
resolves to the hashed name the shell already caches.

Net: hashing is a pure win. Correct and fast with a manifest, correct and slower
without one, and no worse than the previous behaviour if static files are absent
entirely.
"""
import logging

from whitenoise.storage import CompressedManifestStaticFilesStorage

logger = logging.getLogger(__name__)


class LenientManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """Manifest hashing that degrades to plain URLs instead of erroring."""

    manifest_strict = False
    # The fallback below is all-or-nothing in practice — if the static build did
    # not ship, EVERY url on the page takes it — so warn once per process rather
    # than ~50 times per request.
    _warned = False
    # Rewrite relative `import ... from './x.js'` / `import('./x.js')` to the
    # hashed name, so a module's dependencies are cached as aggressively — and
    # precached by the service worker as reliably — as its entry point.
    support_js_module_import_aggregation = True

    def hashed_name(self, name, content=None, filename=None):
        try:
            return super().hashed_name(name, content, filename)
        except ValueError:
            # Raised when the source file cannot be found — i.e. the static build
            # did not ship. Serve the plain name so templates still render.
            if not type(self)._warned:
                type(self)._warned = True
                logger.warning(
                    "static file %r missing: serving unhashed URLs (no immutable "
                    "caching). Did collectstatic run and ship with the app?",
                    name,
                )
            return name
