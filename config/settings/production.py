"""Production settings: hardened security headers and HTTPS enforcement."""
from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False

# Content-hash static asset names, which is what
# lets WhiteNoise serve them `immutable` instead of re-validating every file 60
# seconds after the last visit. The non-manifest storage was used
# here before because a strict manifest 500s the whole site if staticfiles.json
# does not ship with the serverless function; see config/storage.py, which keeps
# the hashing but degrades to unhashed URLs instead of raising.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "config.storage.LenientManifestStaticFilesStorage"},
}

# ALLOWED_HOSTS / CSRF_TRUSTED_ORIGINS must be supplied via the environment.
# Example: ALLOWED_HOSTS=example.com,www.example.com
#          CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com

# --- HTTPS / transport security ---------------------------------------------
# Behind a proxy (Nginx, Vercel, Railway...) trust the forwarded-proto header.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HTTP Strict Transport Security (opt in gradually; 1 year once verified).
SECURE_HSTS_SECONDS = env("SECURE_HSTS_SECONDS", default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# --- Content / clickjacking hardening ---------------------------------------
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
