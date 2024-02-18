"""
String template tags - String manipulation in templates.

Usage:
    {% load string_ext %}

    {{ text|truncate_chars:50 }}
    {{ text|strip }}
    {{ text|replace:"old,new" }}
"""

import re
from django import template
from django.utils.html import strip_tags
from django.utils.text import slugify as django_slugify

register = template.Library()


@register.filter
def truncate_chars(value, length):
    """
    Truncate string to specified length with ellipsis.

    Usage: {{ text|truncate_chars:50 }}
    """
    try:
        length = int(length)
        value = str(value)
        if len(value) <= length:
            return value
        return value[:length-3] + '...'
    except (ValueError, TypeError):
        return value


@register.filter
def truncate_words(value, count):
    """
    Truncate string to specified number of words.

    Usage: {{ text|truncate_words:10 }}
    """
    try:
        count = int(count)
        words = str(value).split()
        if len(words) <= count:
            return value
        return ' '.join(words[:count]) + '...'
    except (ValueError, TypeError):
        return value


@register.filter(name='strip')
def strip_whitespace(value):
    """
    Strip leading and trailing whitespace.

    Usage: {{ text|strip }}
    """
    try:
        return str(value).strip()
    except (ValueError, TypeError):
        return value


@register.filter
def lstrip(value, chars=None):
    """
    Strip leading characters.

    Usage: {{ text|lstrip }} or {{ text|lstrip:"/" }}
    """
    try:
        return str(value).lstrip(chars)
    except (ValueError, TypeError):
        return value


@register.filter
def rstrip(value, chars=None):
    """
    Strip trailing characters.

    Usage: {{ text|rstrip }} or {{ text|rstrip:"/" }}
    """
    try:
        return str(value).rstrip(chars)
    except (ValueError, TypeError):
        return value


@register.filter
def replace(value, args):
    """
    Replace occurrences in string.

    Usage: {{ text|replace:"old,new" }}
    """
    try:
        old, new = args.split(',', 1)
        return str(value).replace(old, new)
    except (ValueError, TypeError, AttributeError):
        return value


@register.filter
def split(value, separator=' '):
    """
    Split string into list.
