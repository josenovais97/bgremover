"""Template context processors."""
from django.conf import settings
from django.urls import reverse, translate_url
from django.utils.translation import get_language

from config.middleware import ISOLATED_VIEWS

from .translations import t as tr
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
    {"name": "ecommerce", "icon": "fa-solid fa-store", "label": "eCommerce"},
    {"name": "blur", "icon": "fa-solid fa-camera", "label": "Blur"},
    {"name": "portrait", "icon": "fa-solid fa-image-portrait", "label": "Portrait"},
    {"name": "favicon", "icon": "fa-solid fa-star", "label": "Favicon"},
]


def _alternate_urls(request):
    """Absolute English + Portuguese URLs for the current page (for hreflang)."""
    try:
        return {
            "en": request.build_absolute_uri(translate_url(request.path, "en")),
            "pt": request.build_absolute_uri(translate_url(request.path, "pt")),
        }
    except Exception:
        return {}


def seo(request):
    """Expose SEO verification tokens and shared nav/ad/i18n data to templates."""
    # Ads run on the marketing / SEO landing pages ONLY — the interactive tool
    # pages stay ad-free and fast (and the cross-origin-isolated ones would block
    # ad frames via COEP anyway). `ISOLATED_VIEWS` is imported so this decision
    # stays visibly tied to the middleware's isolation logic.
    match = getattr(request, "resolver_match", None)
    url_name = match.url_name if match is not None else None
    ads_allowed = url_name == "use_case" and url_name not in ISOLATED_VIEWS
    alternates = _alternate_urls(request)
    return {
        "google_site_verification": settings.GOOGLE_SITE_VERIFICATION,
        "bing_site_verification": settings.BING_SITE_VERIFICATION,
        # Landing pages are surfaced in the footer of every page; the nav label is
        # translated so the footer localises too.
        "use_cases": [{"slug": c["slug"], "nav": tr(c["nav"])} for c in USE_CASES],
        # Header tool switcher (URL + translated label resolved here).
        "tool_nav": [{**item, "label": tr(item["label"]), "url": reverse(f"remover:{item['name']}")} for item in TOOL_NAV],
        # Monetization: expose the AdSense config only where ads are allowed.
        "adsense_client": settings.ADSENSE_CLIENT if ads_allowed else "",
        "adsense_slot_landing": settings.ADSENSE_SLOT_LANDING,
        # i18n
        "LANGUAGE_CODE": get_language() or "en",
        "alt_en": alternates.get("en"),
        "alt_pt": alternates.get("pt"),
    }
