"""Template tag for the lightweight in-code translation catalogue.

Usage: ``{% load i18n_extras %}`` then ``{% t "Convert" %}``. Returns the string
for the active language (when one exists in the matching remover.locale_data
catalogue) and the English source otherwise. Keeps English text in the templates
as the source of truth, so untranslated strings degrade gracefully.
"""
from django import template
from django.utils.html import escape

from remover.translations import t as translate

register = template.Library()


@register.simple_tag
def t(text):
    # `escape` (not conditional_escape): Django marks template string literals as
    # "safe", which conditional_escape would skip — leaving a raw "&". escape()
    # always escapes, so special characters in the copy become valid HTML
    # entities, matching how the original literal markup was written. Our
    # translations are plain prose, so there's nothing that should stay raw HTML.
    return escape(translate(text))
