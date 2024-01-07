"""
Humanize template tags - Make data more human-readable.

Usage:
    {% load humanize_ext %}

    {{ large_number|intcomma }}
    {{ bytes_value|filesizeformat }}
    {{ list|oxford_comma }}
    {{ number|ordinal }}
"""

from django import template
from django.utils.html import format_html
from django.utils.timesince import timesince
from datetime import datetime, timedelta

register = template.Library()


@register.filter
def intcomma(value, decimal_places=0):
    """
    Format a number with commas as thousands separators.

    Usage: {{ 1000000|intcomma }} -> "1,000,000"
    """
    try:
        if decimal_places:
            return f'{float(value):,.{decimal_places}f}'
        return f'{int(value):,}'
    except (ValueError, TypeError):
        return value


@register.filter
def intword(value):
    """
    Convert large numbers to readable word format.

    Usage: {{ 1000000|intword }} -> "1.0 million"
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        return value

    abs_value = abs(value)

    if abs_value < 1000:
        return str(value)

    suffixes = [
        (10**12, 'trillion'),
        (10**9, 'billion'),
        (10**6, 'million'),
        (10**3, 'thousand'),
    ]

    for divisor, suffix in suffixes:
        if abs_value >= divisor:
            result = value / divisor
            if result == int(result):
                return f'{int(result)} {suffix}'
            return f'{result:.1f} {suffix}'

    return str(value)


@register.filter
def ordinal(value):
    """
    Convert a number to its ordinal form.

    Usage: {{ 1|ordinal }} -> "1st", {{ 2|ordinal }} -> "2nd"
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        return value

    if 10 <= abs(value) % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(abs(value) % 10, 'th')

