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
SITE_URL = env("SITE_URL", default="http://localhost:8000")

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
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# No database: all state (history, stats, theme) lives in the browser. Django
# defaults DATABASES to empty, which is exactly what we want here.

# --- Internationalization ----------------------------------------------------
LANGUAGE_CODE = "en-us"
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
