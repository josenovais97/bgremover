"""
Lightweight in-code translation catalogues.

Django's gettext workflow needs the gettext binaries (msgfmt/xgettext) to compile
``.mo`` files, which aren't guaranteed on the build host. Instead each language is
a plain Python module in ``remover.locale_data`` exposing four dicts, resolved
through the helpers here: the ``{% t %}`` tag (remover/templatetags/i18n_extras.py)
for template copy, and ``CBG.t()`` in the browser for runtime messages.

English is deliberately not a catalogue. Every key IS its English text, so an
English page needs no data and no payload — which is also why a missing string
anywhere degrades to English rather than to a blank or a key.

**Adding a language** is a data edit, not an architecture change:

1. write ``locale_data/lang_<code>.py`` with ``UI``, ``JS_UI``, ``USE_CASES``
   and ``FAQS`` (copy an existing one — the keys are the English source text);
2. register it in ``CATALOGUES`` and ``LANGUAGE_NAMES`` below;
3. add ``("<code>", "<Endonym>")`` to ``settings.LANGUAGES``;
4. list the paths whose templates really are translated in
   ``views.TRANSLATED_PATHS``.

Nothing else in the app is told how many languages exist: the hreflang set, the
sitemap, the footer switcher, the canonical rules and the `noindex` on
untranslated prefixes all derive from these four places. Step 4 is the one that
is a judgement call rather than a fact, so ``TranslationCoverageTests`` checks
the claim against what each page actually renders, in both directions.

Language is activated by Django's LocaleMiddleware from the URL prefix
(config/urls.py), so ``get_language()`` returns e.g. ``"es"`` on ``/es/`` pages.
"""
from django.utils.translation import get_language

from .locale_data import lang_es, lang_pt

# Non-English catalogues, in the order the footer switcher lists them.
CATALOGUES = {
    "pt": lang_pt,
    "es": lang_es,
}

# Endonyms for the language switcher: a Spanish speaker scans for "Español", not
# for "Spanish". English is added by the template, which always offers the root.
LANGUAGE_NAMES = {
    "pt": "Português",
    "es": "Español",
}

# The non-English language codes, as a tuple. Import this rather than hard-coding
# ("pt",) anywhere — that second list is the thing that drifts.
LANGUAGES = tuple(CATALOGUES)


def _code(lang=None):
    """Normalise `lang` to a catalogue code, or None for English/unknown.

    ``get_language()`` can return a regional tag (``pt-br``, ``es-419``) where
    the catalogue is keyed by the base language, so the subtag is dropped before
    lookup. An unknown language is None, which every helper below reads as
    "serve English" — the same graceful path as a missing string.
    """
    lang = (lang or get_language() or "en").split("-")[0].lower()
    return lang if lang in CATALOGUES else None


def catalogue(lang=None):
    """The catalogue module for `lang`, or None on English."""
    code = _code(lang)
    return CATALOGUES[code] if code else None


# --- URL-prefix helpers ------------------------------------------------------
# `prefix_default_language=False` means English lives at the root and every other
# language under /<code>/. These two are the only places that know that shape.

def strip_language(path):
    """``/es/crop/`` → ``/crop/``. An English path comes back unchanged."""
    for code in CATALOGUES:
        if path == f"/{code}":
            return "/"
        if path.startswith(f"/{code}/"):
            return path[len(code) + 1:]
    return path


def path_language(path):
    """The language a URL prefix names, or None for an English (root) path."""
    for code in CATALOGUES:
        if path == f"/{code}" or path.startswith(f"/{code}/"):
            return code
    return None


# --- Lookups -----------------------------------------------------------------

def t(text, lang=None):
    """Translate a UI string, falling back to the English source."""
    cat = catalogue(lang)
    return cat.UI.get(text, text) if cat else text


# --- The knockout noun -------------------------------------------------------
# The home page's h1 renders one word as an outline filled with the transparency
# checkerboard (see `.knockout` in input.css) — the brand's signature device.
#
# It has to be a word that REALLY OCCURS in that language's translation of the
# headline, and the languages do not agree on word order:
#
#   en  Free /Background/ Remover
#   pt  Removedor de /Fundo/ Grátis
#   es  Eliminador de /Fondos/ Gratis
#
# So the headline cannot be assembled from three separate {% t %} calls — in
# Portuguese that renders "Grátis Fundo Removedor". Instead the translated string
# stays whole and the noun is wrapped inside it, which also means translators
# never see markup and the h1's text content is unchanged for crawlers and
# screen readers.
#
# `None` is the English key, matching `_code()`'s convention. KnockoutTests
# asserts every entry actually appears in its language's headline, so a
# retranslation cannot silently drop the device.
KNOCKOUT_NOUN = {None: "Background", "pt": "Fundo", "es": "Fondos"}

# The headline the noun is looked for in — named once so the test and the
# template cannot disagree about which string carries the device.
KNOCKOUT_HEADLINE = "Free Background Remover"


def knockout_noun(lang=None):
    """The word the h1 knocks out in `lang` (English if it has no entry)."""
    return KNOCKOUT_NOUN.get(_code(lang), KNOCKOUT_NOUN[None])


def js_catalogue(lang=None):
    """The runtime string catalogue for the browser, or {} on English pages.

    Empty for English on purpose: CBG.t() returns its key unchanged when a
    string is missing, and the keys ARE the English text, so an English page
    needs no payload at all.
    """
    cat = catalogue(lang)
    return cat.JS_UI if cat else {}


def localize_use_case(case, lang=None):
    """Return the use-case dict with translated fields merged in (or unchanged)."""
    cat = catalogue(lang)
    if cat is None:
        return case
    tr = cat.USE_CASES.get(case["slug"])
    return {**case, **tr} if tr else case


def localize_faqs(faqs, lang=None):
    """Return `faqs` with the translated Q&A swapped in on a translated page.

    Keys are the English question text; a question without a translation stays
    English (graceful degradation, like everything else in this module).
    """
    cat = catalogue(lang)
    if cat is None:
        return faqs
    out = []
    for f in faqs:
        tr = cat.FAQS.get(f["q"])
        out.append({"q": tr[0], "a": tr[1]} if tr else f)
    return out
