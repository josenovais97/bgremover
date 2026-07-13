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

# Google AdSense hosts. Ads only run on non-isolated marketing pages (the loader
# is gated in the template), but the CSP is global, so these allowances are
# listed once here; they load nothing on their own.
ADS_SCRIPT = "https://pagead2.googlesyndication.com https://*.googlesyndication.com https://adservice.google.com https://*.googleadservices.com"
# AdSense renders creatives inside frames from these hosts (the wildcard covers
# pagead2 / tpc.googlesyndication.com).
ADS_FRAME = "https://*.googlesyndication.com https://googleads.g.doubleclick.net https://www.google.com"

CSP = "; ".join(
    [
        "default-src 'self'",
        "base-uri 'self'",
        "object-src 'none'",
        "frame-ancestors 'none'",
        "form-action 'self'",
        # https: lets AdSense creatives (served from many hosts) load their images.
        "img-src 'self' data: blob: https:",
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com",
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com",
        # 'unsafe-eval' + 'wasm-unsafe-eval': required by the onnxruntime-web WASM
        # backend that powers in-browser background removal. blob: lets it spin up
        # its worker. Tighten these if you later self-host a stricter runtime.
        f"script-src 'self' 'wasm-unsafe-eval' 'unsafe-eval' blob: {JS_CDN} {MODEL_CDN} {ADS_SCRIPT}",
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
#   * The upscaler is intentionally excluded — it runs on the WebGL/GPU backend,
#     which needs no isolation, and COEP would only add a failure surface for its
#     third-party model-weight fetches.
#   * The marketing / SEO landing pages are excluded so they stay embeddable and
#     third-party ad scripts (which COEP would otherwise block) can run there.
ISOLATED_VIEWS = {"index", "instagram", "sticker", "passport", "ecommerce", "blur"}

COOP = "same-origin"
# 'credentialless' keeps the existing cross-origin CDN assets (Google Fonts,
# Font Awesome, the model weights) loading on isolated pages without requiring
# each response to send a CORP header — they are simply fetched without
# credentials, which is fine for public assets. Safari, which does not support
# 'credentialless', silently skips isolation and falls back to the (still
# working) single-threaded path.
COEP = "credentialless"


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
