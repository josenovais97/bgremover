"""Template context processors."""
from django.conf import settings
from django.urls import reverse, translate_url
from django.utils.translation import get_language

from config.middleware import ISOLATED_VIEWS

from .translations import t as tr
from .views import USE_CASES

# The tool switcher in the header. Defined once here so every item renders with
# identical markup (no per-link drift in sizing/wrapping) and adding a tool is a
# one-line change. `name` matches the URL name (used for the active state);
# `group` keys into TOOL_GROUPS so the "All tools" mega-menu can categorise it.
# The list order is also the pill-row order (most-used first).
TOOL_NAV = [
    {"name": "index", "icon": "fa-solid fa-wand-magic-sparkles", "label": "Remove BG", "group": "edit"},
    {"name": "convert", "icon": "fa-solid fa-arrow-right-arrow-left", "label": "Convert", "group": "optimize"},
    {"name": "compress", "icon": "fa-solid fa-compress", "label": "Compress", "group": "optimize"},
    {"name": "instagram", "icon": "fa-brands fa-instagram", "label": "Instagram", "group": "create"},
    {"name": "crop", "icon": "fa-solid fa-crop-simple", "label": "Crop", "group": "edit"},
    {"name": "sticker", "icon": "fa-solid fa-note-sticky", "label": "Stickers", "group": "create"},
    {"name": "text_behind", "icon": "fa-solid fa-font", "label": "Text Behind", "group": "create"},
    {"name": "meme", "icon": "fa-solid fa-face-laugh", "label": "Meme", "group": "create"},
    {"name": "passport", "icon": "fa-solid fa-passport", "label": "Passport", "group": "photos"},
    {"name": "ecommerce", "icon": "fa-solid fa-store", "label": "eCommerce", "group": "photos"},
    {"name": "blur", "icon": "fa-solid fa-camera", "label": "Blur", "group": "edit"},
    {"name": "favicon", "icon": "fa-solid fa-star", "label": "Favicon", "group": "optimize"},
]

# Categories for the "All tools" mega-menu, in display order. Each groups the
# TOOL_NAV items whose `group` matches its key. Labels are translated at render.
TOOL_GROUPS = [
    {"key": "edit", "label": "Remove & Edit"},
    {"key": "optimize", "label": "Convert & Optimize"},
    {"key": "create", "label": "Create & Share"},
    {"key": "photos", "label": "Photos"},
]


# Per-tool signature accent colours as "R G B" (primary, hover). Resolved into
# the --color-primary CSS variables in base.html so each tool page re-tints every
# `primary` element to its own colour. Unlisted views fall back to the brand indigo.
TOOL_ACCENTS = {
    "index": ("79 70 229", "67 56 202"),        # indigo (brand)
    "blur": ("2 132 199", "3 105 161"),         # sky
    "ecommerce": ("5 150 105", "4 120 87"),     # emerald
    "convert": ("124 58 237", "109 40 217"),    # violet
    "compress": ("8 145 178", "14 116 144"),    # cyan
    "crop": ("37 99 235", "29 78 216"),         # blue
    "meme": ("192 38 211", "162 28 175"),       # fuchsia
    "instagram": ("214 41 118", "185 30 99"),   # instagram pink
    "sticker": ("217 119 6", "180 83 9"),       # amber
    "text_behind": ("13 148 136", "15 118 110"), # teal
    "passport": ("220 38 38", "185 28 28"),     # red
    "passport_country": ("220 38 38", "185 28 28"),
    "favicon": ("202 138 4", "161 98 7"),       # yellow/gold
}
_DEFAULT_ACCENT = ("79 70 229", "67 56 202")


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
    accent, accent_hover = TOOL_ACCENTS.get(url_name, _DEFAULT_ACCENT)
    # Header tool switcher: resolve URL + translated label once, reused by both
    # the pill row and the grouped "All tools" mega-menu.
    tool_nav = [
        {**item, "label": tr(item["label"]), "url": reverse(f"remover:{item['name']}")}
        for item in TOOL_NAV
    ]
    tool_groups = [
        {"label": tr(g["label"]), "items": [it for it in tool_nav if it["group"] == g["key"]]}
        for g in TOOL_GROUPS
    ]
    return {
        "accent_rgb": accent,
        "accent_rgb_hover": accent_hover,
        "google_site_verification": settings.GOOGLE_SITE_VERIFICATION,
        "bing_site_verification": settings.BING_SITE_VERIFICATION,
        # Landing pages are surfaced in the footer of every page; the nav label is
        # translated so the footer localises too.
        "use_cases": [{"slug": c["slug"], "nav": tr(c["nav"])} for c in USE_CASES],
        # Header tool switcher: flat list (pill row) + grouped (mega-menu).
        "tool_nav": tool_nav,
        "tool_groups": tool_groups,
        # Monetization: expose the AdSense config only where ads are allowed.
        "adsense_client": settings.ADSENSE_CLIENT if ads_allowed else "",
        "adsense_slot_landing": settings.ADSENSE_SLOT_LANDING,
        # i18n
        "LANGUAGE_CODE": get_language() or "en",
        "alt_en": alternates.get("en"),
        "alt_pt": alternates.get("pt"),
    }
