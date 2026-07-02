# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source.
COPY . .

# Collect static assets at build time (SECRET_KEY has a build-safe default).
RUN python manage.py collectstatic --noinput --clear

# Run as an unprivileged user.
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# Gunicorn: workers scale with CPUs; tune via env if needed.
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
