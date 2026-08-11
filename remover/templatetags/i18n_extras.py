"""Template tag for the lightweight in-code translation catalogue.

Usage: ``{% load i18n_extras %}`` then ``{% t "Convert" %}``. Returns the string
for the active language (when one exists in the matching remover.locale_data
catalogue) and the English source otherwise. Keeps English text in the templates
as the source of truth, so untranslated strings degrade gracefully.
"""
import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

from remover.translations import knockout_noun
from remover.translations import t as translate

register = template.Library()


@register.simple_tag
def t_knockout(text):
    """Translate `text` and wrap its knockout noun in a `.knockout` span.

    The home page's signature device: one word in the h1 rendered as an outline
    filled with the transparency checkerboard. The noun differs per language and
    so does its position in the sentence (see translations.KNOCKOUT_NOUN), so the
    translated string is kept WHOLE and the word is wrapped inside it — rather
    than the headline being assembled from three separate {% t %} calls, which
    would reorder the words in Portuguese and Spanish.

    Everything is escaped first and only the span is added back as safe markup,
    so this is no laxer than the plain `t` tag. If the noun is not present (a
    retranslation that no longer contains it) the headline renders unchanged and
    simply loses the effect — never a broken tag, never an empty h1.
    KnockoutTests guards against that drifting unnoticed.
    """
    translated = escape(translate(text))
    noun = escape(knockout_noun())
    # Whole word only, so "Background" does not match inside "Backgrounds", and
    # first occurrence only — the device is one word, not every instance of it.
    pattern = re.compile(rf"(?<!\w){re.escape(noun)}(?!\w)")
    return mark_safe(pattern.sub(
        lambda m: f'<span class="knockout">{m.group(0)}</span>', translated, count=1,
    ))


@register.simple_tag
def t(text):
    # `escape` (not conditional_escape): Django marks template string literals as
    # "safe", which conditional_escape would skip — leaving a raw "&". escape()
    # always escapes, so special characters in the copy become valid HTML
    # entities, matching how the original literal markup was written. Our
    # translations are plain prose, so there's nothing that should stay raw HTML.
    return escape(translate(text))
