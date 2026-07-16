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
    {"name": "resize", "icon": "fa-solid fa-expand", "label": "Resize", "group": "optimize"},
    {"name": "instagram", "icon": "fa-brands fa-instagram", "label": "Instagram", "group": "create"},
    {"name": "crop", "icon": "fa-solid fa-crop-simple", "label": "Crop", "group": "edit"},
    {"name": "sticker", "icon": "fa-solid fa-note-sticky", "label": "Stickers", "group": "create"},
    {"name": "text_behind", "icon": "fa-solid fa-font", "label": "Text Behind", "group": "create"},
    {"name": "watermark", "icon": "fa-solid fa-stamp", "label": "Watermark", "group": "create"},
    {"name": "gif", "icon": "fa-solid fa-images", "label": "GIF Maker", "group": "create"},
    {"name": "meme", "icon": "fa-solid fa-face-laugh", "label": "Meme", "group": "create"},
    {"name": "passport", "icon": "fa-solid fa-passport", "label": "Passport", "group": "photos"},
    {"name": "ecommerce", "icon": "fa-solid fa-store", "label": "eCommerce", "group": "photos"},
    {"name": "blur", "icon": "fa-solid fa-camera", "label": "Blur", "group": "edit"},
    {"name": "redact", "icon": "fa-solid fa-shield-halved", "label": "Redact", "group": "edit"},
    {"name": "favicon", "icon": "fa-solid fa-star", "label": "Favicon", "group": "optimize"},
    {"name": "qr", "icon": "fa-solid fa-table-cells-large", "label": "QR Code", "group": "optimize"},
    {"name": "exif", "icon": "fa-solid fa-database", "label": "EXIF", "group": "optimize"},
]

# Categories for the "All tools" mega-menu, in display order. Each groups the
# TOOL_NAV items whose `group` matches its key. Labels are translated at render.
TOOL_GROUPS = [
    {"key": "edit", "label": "Remove & Edit"},
    {"key": "optimize", "label": "Convert & Optimize"},
    {"key": "create", "label": "Create & Share"},
    {"key": "photos", "label": "Photos"},
]


# Per-tool signature accent colours as "R G B", each a
# (surface, surface_hover, text_dark, text_dark_alt) tuple resolved into CSS
# variables in base.html. Unlisted views fall back to the brand indigo.
#
# Why four values and not one: `primary` does two jobs with opposite contrast
# needs. As a SURFACE (`bg-primary`/`from-primary` under white text) it must stay
# dark enough to carry that text in BOTH themes, so it does not vary by theme. As
# TEXT on the page background (`text-primaryText`) it must invert — a shade that
# reads on white is unreadable on the dark surface, and vice versa.
#
#   surface, surface_hover  the two surface stops (also the light-theme text pair)
#   text_dark, text_dark_alt the dark-theme text pair
#
# The pairs exist because the hero headline paints a GRADIENT as text
# (`bg-clip-text from-primaryText to-primaryTextAlt`), so both stops must be
# legible — a single text token would only fix the first one.
#
# Every value is a Tailwind palette shade chosen so all four roles clear WCAG AA
# (4.5:1) — surface and hover against white, the text pair against the dark glass
# surface. Shades were picked by contrast measurement, not by eye: each hue uses
# the most vivid shade that still passes, so the signature colour survives.
# AccentContrastTests recomputes those ratios, so an edit below that dips under AA
# fails the suite rather than shipping.
TOOL_ACCENTS = {
    "index": ("79 70 229", "67 56 202", "129 140 248", "165 180 252"),        # indigo 600/700/400/300 (brand)
    "blur": ("3 105 161", "7 89 133", "2 132 199", "14 165 233"),            # sky 700/800/600/500
    "ecommerce": ("4 120 87", "6 95 70", "5 150 105", "16 185 129"),         # emerald 700/800/600/500
    "convert": ("124 58 237", "109 40 217", "167 139 250", "196 181 253"),    # violet 600/700/400/300
    "compress": ("14 116 144", "21 94 117", "8 145 178", "6 182 212"),      # cyan 700/800/600/500
    "crop": ("37 99 235", "29 78 216", "59 130 246", "96 165 250"),          # blue 600/700/500/400
    "meme": ("192 38 211", "162 28 175", "217 70 239", "232 121 249"),        # fuchsia 600/700/500/400
    "instagram": ("219 39 119", "190 24 93", "236 72 153", "244 114 182"),    # pink 600/700/500/400
    "sticker": ("180 83 9", "146 64 14", "217 119 6", "245 158 11"),         # amber 700/800/600/500
    "text_behind": ("15 118 110", "17 94 89", "13 148 136", "20 184 166"),   # teal 700/800/600/500
    "passport": ("220 38 38", "185 28 28", "239 68 68", "248 113 113"),       # red 600/700/500/400
    "passport_country": ("220 38 38", "185 28 28", "239 68 68", "248 113 113"),
    "favicon": ("161 98 7", "133 77 14", "202 138 4", "234 179 8"),         # yellow 700/800/600/500
    "qr": ("100 116 139", "71 85 105", "148 163 184", "203 213 225"),         # slate 500/600/400/300
    "redact": ("225 29 72", "190 18 60", "244 63 94", "251 113 133"),         # rose 600/700/500/400
    "exif": ("21 128 61", "22 101 52", "22 163 74", "34 197 94"),           # green 700/800/600/500
    "resize": ("194 65 12", "154 52 18", "234 88 12", "249 115 22"),         # orange 700/800/600/500
    "watermark": ("77 124 15", "63 98 18", "101 163 13", "132 204 22"),      # lime 700/800/600/500
    "gif": ("147 51 234", "126 34 206", "168 85 247", "192 132 252"),         # purple 600/700/500/400
}
_DEFAULT_ACCENT = TOOL_ACCENTS["index"]


def _hex(rgb):
    """"R G B" -> "#rrggbb" (for <meta name=theme-color>, which takes no rgb())."""
    return "#" + "".join(f"{int(c):02x}" for c in rgb.split())


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
    accent, accent_hover, accent_text_dark, accent_text_dark_alt = TOOL_ACCENTS.get(
        url_name, _DEFAULT_ACCENT
    )
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
        "accent_rgb_text_dark": accent_text_dark,
        "accent_rgb_text_dark_alt": accent_text_dark_alt,
        # Browser chrome (address bar / PWA) matches the tool's accent too.
        "accent_hex": _hex(accent),
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
