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

    return f'{value}{suffix}'


@register.filter
def oxford_comma(items):
    """
    Join a list with Oxford comma.

    Usage: {{ items|oxford_comma }}
    ['a', 'b', 'c'] -> "a, b, and c"
    """
    try:
        items = list(items)
    except TypeError:
        return items

    if not items:
        return ''
    if len(items) == 1:
        return str(items[0])
    if len(items) == 2:
        return f'{items[0]} and {items[1]}'

    return ', '.join(str(i) for i in items[:-1]) + f', and {items[-1]}'


@register.filter
def truncatewords_html(value, length=30):
    """
    Truncate text to a number of words, preserving HTML.

    Usage: {{ text|truncatewords_html:20 }}
    """
    from django.utils.text import Truncator
    return Truncator(value).words(length, html=True)


@register.filter
def filesizeformat(bytes_value, binary=True):
    """
    Format a file size in bytes to human-readable format.

    Usage: {{ size|filesizeformat }}
    """
    try:
        bytes_value = float(bytes_value)
    except (ValueError, TypeError):
        return bytes_value

    if binary:
        suffixes = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']
        divisor = 1024
    else:
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        divisor = 1000

    for suffix in suffixes[:-1]:
        if abs(bytes_value) < divisor:
            if suffix == 'B':
                return f'{int(bytes_value)} {suffix}'
            return f'{bytes_value:.1f} {suffix}'
        bytes_value /= divisor

    return f'{bytes_value:.1f} {suffixes[-1]}'


@register.filter
def naturaltime(value):
    """
    Format a datetime as relative time (e.g., "3 hours ago").

    Usage: {{ datetime|naturaltime }}
    """
    from django.utils import timezone

    if not value:
        return ''

    now = timezone.now()
    if not timezone.is_aware(value):
        value = timezone.make_aware(value)

    diff = now - value

    if diff.total_seconds() < 0:
        # Future
        diff = abs(diff)
        suffix = 'from now'
    else:
        suffix = 'ago'

    if diff.days > 0:
        return f'{timesince(value)} {suffix}'

    seconds = diff.seconds
    if seconds < 60:
        return 'just now' if suffix == 'ago' else 'soon'
    if seconds < 3600:
        minutes = seconds // 60
        unit = 'minute' if minutes == 1 else 'minutes'
        return f'{minutes} {unit} {suffix}'

    hours = seconds // 3600
    unit = 'hour' if hours == 1 else 'hours'
    return f'{hours} {unit} {suffix}'


@register.filter
def pluralize(value, suffixes='s'):
    """
    Return plural suffix based on value.

    Usage:
        {{ count }} item{{ count|pluralize }}
        {{ count }} categor{{ count|pluralize:"y,ies" }}
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        return ''

    if ',' in suffixes:
        singular, plural = suffixes.split(',', 1)
    else:
        singular = ''
        plural = suffixes

    return singular if value == 1 else plural


@register.filter
def duration(seconds):
    """
    Format seconds as human-readable duration.

    Usage: {{ 3661|duration }} -> "1 hour, 1 minute, 1 second"
    """
    try:
        seconds = int(seconds)
    except (ValueError, TypeError):
        return seconds

    if seconds < 0:
        return 'negative duration'

    parts = []

    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    if days:
        parts.append(f'{days} day{"s" if days != 1 else ""}')
    if hours:
        parts.append(f'{hours} hour{"s" if hours != 1 else ""}')
    if minutes:
        parts.append(f'{minutes} minute{"s" if minutes != 1 else ""}')
    if seconds or not parts:
        parts.append(f'{seconds} second{"s" if seconds != 1 else ""}')

    return ', '.join(parts)
