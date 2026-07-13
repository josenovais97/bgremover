"""Template context processors."""
from django.conf import settings
from django.urls import reverse

from config.middleware import ISOLATED_VIEWS

from .views import USE_CASES

# The tool switcher in the header. Defined once here so every item renders with
# identical markup (no per-link drift in sizing/wrapping) and adding a tool is a
# one-line change. `name` matches the URL name (used for the active state).
TOOL_NAV = [
    {"name": "index", "icon": "fa-solid fa-wand-magic-sparkles", "label": "Remove BG"},
    {"name": "convert", "icon": "fa-solid fa-arrow-right-arrow-left", "label": "Convert"},
    {"name": "compress", "icon": "fa-solid fa-compress", "label": "Compress"},
    {"name": "instagram", "icon": "fa-brands fa-instagram", "label": "Instagram"},
    {"name": "crop", "icon": "fa-solid fa-crop-simple", "label": "Crop"},
    {"name": "sticker", "icon": "fa-solid fa-note-sticky", "label": "Stickers"},
    {"name": "meme", "icon": "fa-solid fa-face-laugh", "label": "Meme"},
    {"name": "passport", "icon": "fa-solid fa-passport", "label": "Passport"},
    {"name": "upscaler", "icon": "fa-solid fa-up-right-and-down-left-from-center", "label": "Upscale"},
    {"name": "favicon", "icon": "fa-solid fa-star", "label": "Favicon"},
]


def seo(request):
    """Expose SEO verification tokens and shared nav/ad data to all templates."""
    # Ads run on the marketing / SEO landing pages ONLY — the interactive tool
    # pages stay ad-free and fast (and the cross-origin-isolated ones would block
    # ad frames via COEP anyway). `ISOLATED_VIEWS` is imported so this decision
    # stays visibly tied to the middleware's isolation logic.
    match = getattr(request, "resolver_match", None)
    url_name = match.url_name if match is not None else None
    ads_allowed = url_name == "use_case" and url_name not in ISOLATED_VIEWS
    return {
        "google_site_verification": settings.GOOGLE_SITE_VERIFICATION,
        "bing_site_verification": settings.BING_SITE_VERIFICATION,
        # Landing pages are surfaced in the footer of every page so internal
        # links reach them from anywhere on the site.
        "use_cases": USE_CASES,
        # Header tool switcher (URL resolved here so the template just loops).
        "tool_nav": [{**t, "url": reverse(f"remover:{t['name']}")} for t in TOOL_NAV],
        # Monetization: expose the AdSense config only where ads are allowed.
        "adsense_client": settings.ADSENSE_CLIENT if ads_allowed else "",
        "adsense_slot_landing": settings.ADSENSE_SLOT_LANDING,
    }
