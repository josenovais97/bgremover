"""
WSGI config.

Exposes the WSGI callable as ``application`` (Django convention) and as ``app``,
which is the entry-point name Vercel's Python runtime looks for.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_wsgi_application()

# Alias for serverless platforms (Vercel) that import ``app``.
app = application
