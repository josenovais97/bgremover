"""
Passport / ID photo specifications by country.

Powers the programmatic SEO landing pages at ``/passport-photo/<country>/`` —
each targets high-intent, low-competition queries like "<country> passport photo
size" and "<country> passport photo online". Sizes are the widely-published
official requirements; every page also tells visitors to confirm their own
government's exact rules (this is a free helper, not an official service).
"""
DPI = 300


def _px(mm):
    """Pixels for a millimetre length at 300 DPI (print resolution)."""
    return round(mm * DPI / 25.4)


# Head-height guidance (crown → chin) by frame size.
_HEAD_3545 = "32–36 mm tall — roughly 70–80% of the photo — centred, with the eyes level and looking straight ahead."
_HEAD_US = "1 to 1⅜ inches (25–35 mm), about 50–69% of the photo, with the eyes 1⅛–1⅜ in from the bottom."


def _entry(slug, name, flag, w_mm, h_mm, *, imperial=None, bg="plain white", head=None, note=""):
    return {
        "slug": slug,
        "name": name,
        "flag": flag,
        "w_mm": w_mm,
        "h_mm": h_mm,
        "w_px": _px(w_mm),
        "h_px": _px(h_mm),
        "imperial": imperial,           # e.g. "2 × 2 in" for the US, else None
        "bg": bg,
        "head": head or (_HEAD_US if imperial else _HEAD_3545),
        "note": note,
    }


# Curated, confidently-sourced set. 35×45 mm is the international default used by
# the majority of countries; the exceptions (US, Canada, China, Brazil) carry
# their own dimensions.
# Only countries with a genuinely distinct spec or real standalone search intent
# keep their own page. A wider list (Germany, France, Japan, …) shared the
# identical 35×45 mm / plain-white spec with no distinguishing content, so those
# pages were 85%-similar near-duplicates Google discovered but refused to index
# (measured: 0.83 sibling similarity vs a 0.32 boilerplate floor). They now 301
# to the main tool (see FOLDED_COUNTRY_SLUGS) — the tool still makes photos for
# every country via its own preset list in passport.js; only the thin SEO pages
# are gone. Portugal stays deliberately: it's the home market where the .pt ccTLD
# is a ranking advantage rather than a handicap.
COUNTRIES = [
    _entry("united-states", "United States", "🇺🇸", 51, 51, imperial="2 × 2 in",
           note="The 2×2 inch size is used for the US passport, visa, Green Card and DV lottery."),
    _entry("united-kingdom", "United Kingdom", "🇬🇧", 35, 45, bg="plain light grey or cream",
           note="Used for the UK passport and most UK visa applications."),
    _entry("canada", "Canada", "🇨🇦", 50, 70,
           note="Canada uses a larger 50×70 mm photo for passports."),
    _entry("australia", "Australia", "🇦🇺", 35, 45, bg="plain white or light grey",
           note="Australian passport photos use a plain white or light grey background."),
    _entry("india", "India", "🇮🇳", 35, 45,
           note="Common size for the Indian passport (Passport Seva) application."),
    _entry("schengen-visa", "Schengen Visa (EU)", "🇪🇺", 35, 45,
           note="Accepted across Schengen-area visa and residence applications."),
    _entry("portugal", "Portugal", "🇵🇹", 35, 45,
           note="Portugal uses the EU-standard 35×45 mm size for passport photos."),
    _entry("china", "China", "🇨🇳", 33, 48,
           note="China visa photos use a 33×48 mm size on a white background."),
    _entry("brazil", "Brazil", "🇧🇷", 50, 70,
           note="Brazil commonly uses a 5×7 cm (50×70 mm) photo."),
]

COUNTRIES_BY_SLUG = {c["slug"]: c for c in COUNTRIES}

# Retired per-country pages (identical 35×45 mm / plain-white spec, no unique
# content). They 301 to the main passport tool so any link equity and stray index
# entries consolidate onto a page that can actually rank, instead of 404-ing.
FOLDED_COUNTRY_SLUGS = frozenset({
    "germany", "france", "italy", "ireland", "netherlands", "japan",
    "new-zealand", "south-africa", "singapore", "philippines",
    "south-korea", "nigeria", "pakistan",
})


def size_label(c):
    """Human size string, e.g. '2 × 2 in (51 × 51 mm)' or '35 × 45 mm'."""
    metric = f"{c['w_mm']} × {c['h_mm']} mm"
    return f"{c['imperial']} ({metric})" if c["imperial"] else metric


def country_faqs(c):
    """Generate the FAQ list for a country page from its spec."""
    name = c["name"]
    return [
        {"q": f"What size is a {name} passport photo?",
         "a": f"A {name} passport photo is {size_label(c)}, which is {c['w_px']} × {c['h_px']} pixels at 300 DPI."},
        {"q": f"What background should a {name} passport photo have?",
         "a": f"It should be a {c['bg']} background with even lighting and no shadows. This tool removes your original background and replaces it automatically."},
        {"q": f"How big should the head be in a {name} passport photo?",
         "a": f"The head should be {c['head']}"},
        {"q": f"Can I make a {name} passport photo online for free?",
         "a": "Yes. Upload a photo, position your head inside the guides and download the exact size — free, with no watermark, and your photo never leaves your device."},
        {"q": f"Can I print my {name} passport photo at home?",
         "a": "Yes. Use the 6×4 inch print-sheet option to tile several copies onto a standard print you can order at any pharmacy or photo kiosk."},
    ]
