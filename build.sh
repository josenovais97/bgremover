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
#   Environment vars:     none required — see PRODUCTION_SITE_URL below
set -euo pipefail

# The canonical production origin, committed rather than configured.
#
# This started life as a required environment variable, on the reasoning that
# baking the wrong origin into 320 pages of canonical tags is a bad failure. That
# reasoning was right about the stakes and wrong about the fix: the origin is not
# a secret, it does not vary between builds, and it is already published in the
# sitemap of every page we ship. Making it a dashboard variable bought no safety
# and added a way for the build to fail on a value that was never in doubt.
#
# So: committed default, still overridable by the environment (a fork or a staging
# origin just sets SITE_URL), and verified below rather than merely required.
PRODUCTION_SITE_URL="https://clearbg.pt"

export DJANGO_SETTINGS_MODULE="config.settings.production"

# Django refuses to start without a SECRET_KEY, but nothing it signs can reach
# this build's output: `staticfiles` is the only contrib app (no sessions, no
# auth, no messages) and no template renders {% csrf_token %}. So a throwaway key
# per build is not a compromise, it is the honest description of what the key
# does here — and it means one less variable to get wrong in the dashboard.
export SECRET_KEY="${SECRET_KEY:-$(python -c 'import secrets; print(secrets.token_urlsafe(50))')}"

export SITE_URL="${SITE_URL:-$PRODUCTION_SITE_URL}"
# ALLOWED_HOSTS only has to satisfy Django's host check while prerendering; the
# prerender command adds SITE_URL's own host to it anyway. Deriving it from
# SITE_URL keeps the two from disagreeing.
_host="${SITE_URL#*://}"; _host="${_host%%/*}"
export ALLOWED_HOSTS="${ALLOWED_HOSTS:-$_host,www.$_host}"

# The failure this guards against is shipping a localhost origin to production —
# canonical tags, hreflang and every sitemap <loc> would point at a machine that
# is not the internet, and nothing about the pages would *look* wrong.
case "$SITE_URL" in
  https://*) ;;
  *) echo "ERROR: SITE_URL must be an https:// origin, got '$SITE_URL'." >&2; exit 1 ;;
esac

echo "Building $SITE_URL  (hosts: $ALLOWED_HOSTS)"
[ -n "${CLOUDFLARE_ANALYTICS_TOKEN:-}" ] \
  && echo "Cloudflare Web Analytics: enabled" \
  || echo "Cloudflare Web Analytics: off (set CLOUDFLARE_ANALYTICS_TOKEN to enable)"

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
