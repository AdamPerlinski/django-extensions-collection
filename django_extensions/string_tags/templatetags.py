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

    Usage: {{ text|split:"," }}
    """
    try:
        return str(value).split(separator)
    except (ValueError, TypeError):
        return [value]


@register.filter
def join_str(value, separator=', '):
    """
    Join list into string.

    Usage: {{ items|join_str:", " }}
    """
    try:
        return separator.join(str(v) for v in value)
    except (ValueError, TypeError):
        return value


@register.filter
def upper(value):
    """
    Convert to uppercase.

    Usage: {{ text|upper }}
    """
    try:
        return str(value).upper()
    except (ValueError, TypeError):
        return value


@register.filter
def lower(value):
    """
    Convert to lowercase.

    Usage: {{ text|lower }}
    """
    try:
        return str(value).lower()
    except (ValueError, TypeError):
        return value


@register.filter
def title(value):
    """
    Convert to title case.

    Usage: {{ text|title }}
    """
    try:
        return str(value).title()
    except (ValueError, TypeError):
        return value


@register.filter
def capitalize(value):
    """
    Capitalize first letter.

    Usage: {{ text|capitalize }}
    """
    try:
        return str(value).capitalize()
    except (ValueError, TypeError):
        return value


@register.filter
def slugify(value):
    """
    Convert to URL-friendly slug.

    Usage: {{ text|slugify }}
    """
    try:
        return django_slugify(str(value))
    except (ValueError, TypeError):
        return value


@register.filter
def startswith(value, prefix):
    """
    Check if string starts with prefix.

    Usage: {% if text|startswith:"Hello" %}
    """
    try:
        return str(value).startswith(prefix)
    except (ValueError, TypeError):
        return False


@register.filter
def endswith(value, suffix):
    """
    Check if string ends with suffix.

    Usage: {% if text|endswith:".pdf" %}
    """
    try:
        return str(value).endswith(suffix)
    except (ValueError, TypeError):
        return False


@register.filter
def contains(value, substring):
    """
    Check if string contains substring.

    Usage: {% if text|contains:"search" %}
    """
    try:
        return substring in str(value)
    except (ValueError, TypeError):
        return False


@register.filter
def reverse_str(value):
    """
    Reverse the string.

    Usage: {{ text|reverse_str }}
    """
    try:
        return str(value)[::-1]
    except (ValueError, TypeError):
        return value


@register.filter
def repeat(value, times):
    """
    Repeat string n times.

    Usage: {{ text|repeat:3 }}
    """
    try:
        return str(value) * int(times)
    except (ValueError, TypeError):
        return value


@register.filter
def remove_html(value):
    """
    Remove all HTML tags.

    Usage: {{ html_content|remove_html }}
    """
    try:
        return strip_tags(str(value))
    except (ValueError, TypeError):
        return value


@register.filter
def regex_replace(value, pattern_repl):
    """
    Replace using regex pattern.

    Usage: {{ text|regex_replace:"\\d+,NUMBER" }}
    """
    try:
        pattern, replacement = pattern_repl.split(',', 1)
        return re.sub(pattern, replacement, str(value))
    except (ValueError, TypeError, re.error):
        return value


@register.filter
def pad_left(value, args):
    """
    Pad string on the left.

    Usage: {{ num|pad_left:"5,0" }} -> "00042"
    """
    try:
        width, char = args.split(',')
        return str(value).rjust(int(width), char)
    except (ValueError, TypeError, AttributeError):
        return value


@register.filter
def pad_right(value, args):
    """
    Pad string on the right.

    Usage: {{ text|pad_right:"10,." }}
    """
    try:
        width, char = args.split(',')
        return str(value).ljust(int(width), char)
    except (ValueError, TypeError, AttributeError):
        return value
