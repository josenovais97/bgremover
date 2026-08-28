"""
Custom security-header middleware.

Adds a Content-Security-Policy and a Permissions-Policy that Django doesn't set
out of the box. The CSP is tuned for this app's dependencies:

* Scripts load from the same origin plus jsdelivr (the AI model library + JSZip)
  and need ``wasm-unsafe-eval`` because background removal runs a WASM model.
* The model spins up a Web Worker (``worker-src blob:``) and fetches its weights
  over HTTPS (``connect-src``), so those are permitted.
* Styles allow ``unsafe-inline`` because Tailwind uses inline ``style`` attributes
  for dynamic values (progress bars, clip-path); style injection is low risk.

Headers are only applied on HTML responses to avoid overhead on static assets.
"""

# Host that serves the AI model weights + WASM runtime (@imgly default).
MODEL_CDN = "https://staticimgly.com"
JS_CDN = "https://cdn.jsdelivr.net"

# Cloudflare Web Analytics beacon. Only loads when CLOUDFLARE_ANALYTICS_TOKEN is
# set (see base.html); listing it here costs nothing when it is not. `connect-src`
# already allows https:, so the beacon's own POST needs no extra entry.
ANALYTICS_SCRIPT = "https://static.cloudflareinsights.com"

# Umami cloud. Same deal: the loader is gated on UMAMI_WEBSITE_ID in base.html,
# and its /api/send beacon is already covered by `connect-src https:`. A self-
# hosted instance (UMAMI_SCRIPT_URL) needs its own host added here.
UMAMI_SCRIPT = "https://cloud.umami.is"

# Google AdSense hosts. Ads only run on non-isolated marketing pages (the loader
# is gated in the template), but the CSP is global, so these allowances are
# listed once here; they load nothing on their own.
#
# adtrafficquality.google serves Sodar, the invalid-traffic verification script
# AdSense loads alongside every unit. It was missing here, so the browser blocked
# it and each ad-bearing page threw an uncaught rejection — meaning Google could
# not run the traffic-quality check it expects to run on an ad-serving site.
ADS_SCRIPT = (
    "https://pagead2.googlesyndication.com https://*.googlesyndication.com "
    "https://adservice.google.com https://*.googleadservices.com "
    "https://*.adtrafficquality.google"
)
# AdSense renders creatives inside frames from these hosts (the wildcard covers
# pagead2 / tpc.googlesyndication.com). Sodar renders into a frame of its own.
ADS_FRAME = (
    "https://*.googlesyndication.com https://googleads.g.doubleclick.net "
    "https://www.google.com https://*.adtrafficquality.google"
)

CSP = "; ".join(
    [
        "default-src 'self'",
        "base-uri 'self'",
        "object-src 'none'",
        "frame-ancestors 'none'",
        "form-action 'self'",
        # https: lets AdSense creatives (served from many hosts) load their images.
        "img-src 'self' data: blob: https:",
        # blob: lets the video → GIF tool load a user-picked clip into a <video>
        # element (an object URL). Without this, default-src blocks it and the
        # video reports MEDIA_ERR_SRC_NOT_SUPPORTED as if the codec were bad.
        "media-src 'self' blob:",
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com",
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com",
        # 'unsafe-eval' + 'wasm-unsafe-eval': required by the onnxruntime-web WASM
        # backend that powers in-browser background removal. blob: lets it spin up
        # its worker. Tighten these if you later self-host a stricter runtime.
        f"script-src 'self' 'wasm-unsafe-eval' 'unsafe-eval' blob: {JS_CDN} {MODEL_CDN} "
        f"{ANALYTICS_SCRIPT} {UMAMI_SCRIPT} {ADS_SCRIPT}",
        f"worker-src 'self' blob: {JS_CDN} {MODEL_CDN}",
        f"frame-src 'self' blob: {ADS_FRAME}",
        "child-src 'self' blob:",
        # Model weights are fetched over HTTPS; allow HTTPS + blob/data URLs.
        "connect-src 'self' https: data: blob:",
    ]
)

PERMISSIONS_POLICY = "camera=(), microphone=(), geolocation=(), interest-cohort=()"

# Views that run in-browser background removal (onnxruntime-web WASM). Cross-
# origin isolation (COOP + COEP) unlocks SharedArrayBuffer, so the runtime can
# use its multi-threaded + SIMD backend — a 2-4× speed-up that also lets us run
# the full-quality model without stalling the main thread and tripping the
# browser's "page unresponsive" prompt.
#
# Isolation is scoped to *just* these tool pages on purpose:
#   * The marketing / SEO landing pages are excluded so they stay embeddable and
#     third-party ad scripts (which COEP would otherwise block) can run there.
ISOLATED_VIEWS = {"index", "instagram", "sticker", "passport", "ecommerce", "blur", "text_behind"}

COOP = "same-origin"
# 'credentialless' keeps the existing cross-origin CDN assets (Google Fonts,
# Font Awesome, the model weights) loading on isolated pages without requiring
# each response to send a CORP header — they are simply fetched without
# credentials, which is fine for public assets. Safari, which does not support
# 'credentialless', silently skips isolation and falls back to the (still
# working) single-threaded path.
COEP = "credentialless"


# --- Edge caching for page HTML ----------------------------------------------
# Every page here is anonymous and identical for all visitors: there is no
# SessionMiddleware, no template renders {% csrf_token %}, nothing sets a cookie,
# and nothing on a page varies per visitor (the usage counter stats.js talks to
# is write-only now — it has no display). Yet the pages sent no Cache-Control at
# all, so a CDN could
# not touch them and EVERY view — including the 33 tool pages and ~40 SEO pages —
# booted the Python function, cold start included.
#
# `max-age=0` keeps browsers revalidating (so a visitor never sees yesterday's
# page), while `s-maxage` lets the shared cache serve it outright. The content
# only changes when the site is redeployed, and Vercel invalidates its edge cache
# on deploy, so a day is conservative; `stale-while-revalidate` then covers the
# refresh without making anyone wait for it.
#
# Views that opt out (the stats API's `no-store`, sw.js's `no-cache`, the manifest
# and robots/sitemap `max-age`) set Cache-Control themselves and are left alone.
PAGE_CACHE_CONTROL = "public, max-age=0, s-maxage=86400, stale-while-revalidate=604800"


class EdgeCacheMiddleware:
    """Make anonymous page HTML cacheable by a shared cache.

    Must sit BEFORE LocaleMiddleware in MIDDLEWARE: responses unwind in reverse,
    so this runs after Locale has added its `Vary: Accept-Language` — which is
    what lets us drop it (see below).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            request.method not in ("GET", "HEAD")
            or response.status_code != 200
            or not response.get("Content-Type", "").startswith("text/html")
            or response.has_header("Cache-Control")  # the view knows better
            or response.cookies  # never mark a personalised response public
        ):
            return response

        response["Cache-Control"] = PAGE_CACHE_CONTROL

        # LocaleMiddleware stamps `Vary: Accept-Language` on every response, but
        # the language here comes from the URL prefix alone (/pt/…) — the body is
        # byte-identical whatever the header says, which CacheHeaderTests asserts.
        # Left in place it splits the CDN's cache across every Accept-Language
        # string in the wild, which is most of the benefit above thrown away.
        vary = response.get("Vary")
        if vary:
            kept = [v for v in (p.strip() for p in vary.split(",")) if v.lower() != "accept-language"]
            if kept:
                response["Vary"] = ", ".join(kept)
            else:
                del response["Vary"]
        return response


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get("Content-Type", "")
        if content_type.startswith("text/html"):
            response.setdefault("Content-Security-Policy", CSP)
            response.setdefault("Permissions-Policy", PERMISSIONS_POLICY)
            match = getattr(request, "resolver_match", None)
            if match is not None and match.url_name in ISOLATED_VIEWS:
                response.setdefault("Cross-Origin-Opener-Policy", COOP)
                response.setdefault("Cross-Origin-Embedder-Policy", COEP)
        return response
