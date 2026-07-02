#!/usr/bin/env bash
# Vercel static build step: install deps and collect static assets into
# `staticfiles/`, which is served directly per the routes in vercel.json.
set -euo pipefail

export DJANGO_SETTINGS_MODULE="config.settings.production"

# The build image may expose Python as python3.12 / python3 / python.
PY="$(command -v python3.12 || command -v python3 || command -v python)"

# Vercel's build image Python is managed by uv (PEP 668), so pip refuses to
# install into it without this override. We only need Django available here so
# `collectstatic` can run; the runtime function installs deps separately.
"$PY" -m pip install --break-system-packages -r requirements.txt
"$PY" manage.py collectstatic --noinput --clear
