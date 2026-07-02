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

CSP = "; ".join(
    [
        "default-src 'self'",
        "base-uri 'self'",
        "object-src 'none'",
        "frame-ancestors 'none'",
        "form-action 'self'",
        "img-src 'self' data: blob:",
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com",
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com",
        # 'unsafe-eval' + 'wasm-unsafe-eval': required by the onnxruntime-web WASM
        # backend that powers in-browser background removal. blob: lets it spin up
        # its worker. Tighten these if you later self-host a stricter runtime.
        f"script-src 'self' 'wasm-unsafe-eval' 'unsafe-eval' blob: {JS_CDN} {MODEL_CDN}",
        f"worker-src 'self' blob: {JS_CDN} {MODEL_CDN}",
        "child-src 'self' blob:",
        # Model weights are fetched over HTTPS; allow HTTPS + blob/data URLs.
        "connect-src 'self' https: data: blob:",
    ]
)

PERMISSIONS_POLICY = "camera=(), microphone=(), geolocation=(), interest-cohort=()"


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get("Content-Type", "")
        if content_type.startswith("text/html"):
            response.setdefault("Content-Security-Policy", CSP)
            response.setdefault("Permissions-Policy", PERMISSIONS_POLICY)
        return response
