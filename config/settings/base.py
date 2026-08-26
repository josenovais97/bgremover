"""
Base settings shared across every environment.

Environment-specific overrides live in ``development.py`` and ``production.py``.
The active module is chosen via the ``DJANGO_SETTINGS_MODULE`` environment
variable (defaults to ``config.settings.development`` in ``manage.py``).

Because background removal runs entirely in the visitor's browser
(``@imgly/background-removal``), the server never receives, stores, or
processes uploaded images. That keeps this app stateless and easy to host on
serverless platforms such as Vercel.
"""
from pathlib import Path

import environ

# BASE_DIR points at the repository root (three parents up from this file:
# base.py -> settings/ -> config/ -> repo root).
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
)

# Read a local .env file when present (never committed to source control).
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)

# --- Core security -----------------------------------------------------------
SECRET_KEY = env("SECRET_KEY", default="django-insecure-change-me-in-production")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

# The canonical site URL is used for absolute URLs in SEO tags / sitemap.
# Guard against a scheme-less value (e.g. "example.com") slipping in from the
# environment: without "https://" the sitemap emits invalid <loc> URLs that
# search engines reject. Trailing slashes are stripped by the SEO views.
SITE_URL = env("SITE_URL", default="http://localhost:8000")
if SITE_URL and "://" not in SITE_URL:
    SITE_URL = f"https://{SITE_URL}"

# Search-engine ownership verification tokens (rendered as <meta> tags when set).
GOOGLE_SITE_VERIFICATION = env("GOOGLE_SITE_VERIFICATION", default="")
BING_SITE_VERIFICATION = env("BING_SITE_VERIFICATION", default="")

# Cloudflare Web Analytics token. Replaces Vercel Web Analytics, which was tied
# to the old host (its script lived at the Vercel-injected /_vercel/insights/
# path and 404s anywhere else). Cookie-less and free; paste the token from the
# Cloudflare dashboard into the Pages environment. Unset renders nothing.
CLOUDFLARE_ANALYTICS_TOKEN = env("CLOUDFLARE_ANALYTICS_TOKEN", default="")

# IndexNow: ping Bing and Yandex the moment a URL changes instead of waiting for
# them to come back on their own. The key is NOT a secret — the protocol works by
# publishing it at https://<host>/<key>.txt so the receiving engine can verify the
# ping came from someone who controls the domain. It therefore ships as a default
# rather than as another Vercel variable to remember; override it only to rotate.
#
# Google does not participate in IndexNow, so this speeds up Bing (and the engines
# it feeds: DuckDuckGo, Ecosia, Yahoo) and Yandex, and does nothing for Google.
INDEXNOW_KEY = env("INDEXNOW_KEY", default="a7f3c1e94b8d42a6905e17bc3d6f8e20")

# --- Monetization ------------------------------------------------------------
# Google AdSense publisher ID (ca-pub-…). When set, the AdSense loader is
# injected on the marketing / SEO pages ONLY — never on the cross-origin-isolated
# tool pages, whose COEP would block the ad frames (and which we keep ad-free and
# fast on purpose). Ads are opt-out by clearing this env var.
ADSENSE_CLIENT = env("ADSENSE_CLIENT", default="ca-pub-9381565116085110")
# Optional explicit ad-unit slot for the in-content unit on landing pages. Leave
# blank to rely on AdSense Auto ads (enabled in the AdSense dashboard) instead.
ADSENSE_SLOT_LANDING = env("ADSENSE_SLOT_LANDING", default="")

# --- Social-proof counter ----------------------------------------------------
# A global "images processed" counter backed by Upstash Redis (REST API), which
# works from serverless functions. When these env vars are unset the counter is
# simply disabled (the badge stays hidden) — no fake numbers are ever shown.
#
# Accept either naming scheme so it works no matter how the store is added:
#   * Vercel Storage ("Vercel KV", Upstash-backed) → KV_REST_API_URL / _TOKEN

# --- Applications ------------------------------------------------------------
# The app is deliberately stateless: no models, no auth, no admin, no DB.
# This keeps it fast, secure by minimal surface area, and serverless-friendly.
INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    # Local apps
    "remover.apps.RemoverConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # Sits above LocaleMiddleware so it can strip the `Vary: Accept-Language` that
    # Locale adds on the way out (responses unwind in reverse).
    "config.middleware.EdgeCacheMiddleware",
    # LocaleMiddleware activates the language from the URL prefix (/pt/…). It must
    # sit before CommonMiddleware so URL handling sees the active language.
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "config.middleware.SecurityHeadersMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "remover.context_processors.seo",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# No database: all state (history, stats, theme) lives in the browser. Django
# defaults DATABASES to empty, which is exactly what we want here.

# --- Internationalization ----------------------------------------------------
# English is the default (served without a URL prefix); every other language is
# served under /<code>/. Translations are provided by lightweight in-code
# catalogues (remover.locale_data) rather than gettext .mo files, so no gettext
# build tooling is needed at deploy time. i18n_patterns still handles the routing
# and language activation. See config/urls.py.
#
# This list is duplicated in remover.translations.CATALOGUES, which is the one
# that actually holds the strings. Settings cannot import from the app (the app
# registry isn't ready yet), so the two are kept in step by
# `LanguageRegistryTests` rather than by derivation — a language listed here with
# no catalogue would render an entirely English site under a prefix that claims
# otherwise, which is exactly the failure the noindex rules exist to prevent.
LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English"),
    ("pt", "Português"),
    ("es", "Español"),
]
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Static files ------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Let WhiteNoise serve static files straight from the source dirs via Django's
# finders — no collectstatic needed at runtime. This makes static serving work
# reliably on serverless hosts (Vercel), where the app can't rely on a
# collectstatic step running inside the function.
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

# Plain static storage in dev/tests. Production overrides this with WhiteNoise's
# compressed storage (see settings/production.py).
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Logging -----------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": env("LOG_LEVEL", default="INFO"),
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": env("DJANGO_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
    },
}
