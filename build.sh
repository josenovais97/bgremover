#!/usr/bin/env bash
# Static build for Cloudflare Pages.
#
# The app is Django, but nothing it serves is dynamic — no models, no session,
# no forms, and the image processing runs in the browser. So Django is the build
# tool here, not the runtime: this renders every URL to a file and hands the
# result to a CDN. See remover/management/commands/prerender.py.
#
# Cloudflare Pages settings that go with this script:
#   Build command:        ./build.sh
#   Build output dir:     _site
#   Environment vars:     SECRET_KEY, SITE_URL, ALLOWED_HOSTS (see below)
set -euo pipefail

export DJANGO_SETTINGS_MODULE="config.settings.production"

# SECRET_KEY is required for Django to start, but nothing signed at build time
# outlives the build: there are no sessions, no cookies and no CSRF tokens in the
# output. Set it in the Pages dashboard anyway so the value is not in the repo.
: "${SECRET_KEY:?set SECRET_KEY in the Cloudflare Pages environment}"
# SITE_URL is NOT optional in the same sense — it is baked into every canonical
# tag, hreflang alternate and sitemap <loc> in the output. Getting it wrong ships
# a site that tells Google it lives somewhere else.
: "${SITE_URL:?set SITE_URL (e.g. https://clearbg.pt) in the Cloudflare Pages environment}"

# --break-system-packages is needed on build images whose Python is externally
# managed (PEP 668). Not every image is, and older pip does not know the flag, so
# fall back rather than fail the build on it.
python -m pip install --quiet --break-system-packages -r requirements.txt \
  || python -m pip install --quiet -r requirements.txt

# Tailwind's output is committed, but rebuilding it here means a newly-used class
# can never silently no-op because someone forgot to run the compiler. npm ci
# pins the exact version from package-lock.json, so this is reproducible.
npm ci --silent
npm run build:css

python manage.py collectstatic --noinput --clear
python manage.py prerender --output _site
