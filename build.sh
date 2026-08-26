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

# Django refuses to start without a SECRET_KEY, but nothing it signs can reach
# this build's output: `staticfiles` is the only contrib app (no sessions, no
# auth, no messages) and no template renders {% csrf_token %}. So a throwaway key
# per build is not a compromise, it is the honest description of what the key
# does here — and it means one less variable to get wrong in the dashboard.
export SECRET_KEY="${SECRET_KEY:-$(python -c 'import secrets; print(secrets.token_urlsafe(50))')}"

# SITE_URL is genuinely required: it is baked into every canonical tag, hreflang
# alternate and sitemap <loc>. Getting it wrong ships a site that tells Google it
# lives somewhere else, which is why this fails loudly instead of defaulting.
if [ -z "${SITE_URL:-}" ]; then
  echo "ERROR: SITE_URL is not set (expected e.g. https://clearbg.pt)." >&2
  echo "" >&2
  echo "In Cloudflare Pages this must be a BUILD variable, not a runtime one." >&2
  echo "  Settings -> Build -> Variables and secrets  (NOT 'Variables and Secrets'" >&2
  echo "  under Runtime, which is only exposed to Functions at request time)." >&2
  echo "  Add it to the Production environment, then Retry deployment." >&2
  exit 1
fi

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
