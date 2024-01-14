"""
URL template tags - URL manipulation in templates.

Usage:
    {% load url_ext %}

    {{ url|domain }}
    {{ url|add_query:"page=2" }}
    {{ request.path|active_link:"home" }}
"""

from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def domain(url):
    """
    Extract domain from URL.

    Usage: {{ url|domain }}
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return url


@register.filter
def scheme(url):
    """
    Extract scheme from URL.

    Usage: {{ url|scheme }}
    """
    try:
        parsed = urlparse(url)
        return parsed.scheme
    except Exception:
        return ''


@register.filter
def path(url):
    """
    Extract path from URL.

    Usage: {{ url|path }}
    """
    try:
        parsed = urlparse(url)
        return parsed.path
    except Exception:
        return url


@register.filter
def query_string(url):
    """
    Extract query string from URL.

    Usage: {{ url|query_string }}
    """
    try:
        parsed = urlparse(url)
        return parsed.query
    except Exception:
        return ''


@register.filter
def add_query(url, params):
    """
    Add query parameters to URL.

    Usage: {{ url|add_query:"foo=bar&baz=qux" }}
    """
    try:
        parsed = urlparse(url)
