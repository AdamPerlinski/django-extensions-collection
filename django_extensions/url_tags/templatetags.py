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
        existing_params = parse_qs(parsed.query)

        # Parse new params
        new_params = parse_qs(params)

        # Merge (new params override existing)
        existing_params.update(new_params)

        # Flatten single-value lists
        flat_params = {k: v[0] if len(v) == 1 else v for k, v in existing_params.items()}

        new_query = urlencode(flat_params, doseq=True)

        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
    except Exception:
        return url


@register.filter
def remove_query(url, param):
    """
    Remove a query parameter from URL.

    Usage: {{ url|remove_query:"page" }}
    """
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        if param in params:
            del params[param]

        flat_params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
        new_query = urlencode(flat_params, doseq=True)

        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
    except Exception:
        return url


@register.filter
def absolute_url(path, request):
    """
    Convert relative path to absolute URL.

    Usage: {{ path|absolute_url:request }}
    """
    try:
        return request.build_absolute_uri(path)
    except Exception:
        return path


@register.simple_tag(takes_context=True)
def active_link(context, url_name, css_class='active'):
    """
    Return CSS class if current URL matches.

    Usage: {% active_link 'home' 'active' %}
    """
    try:
        from django.urls import reverse, resolve
        request = context.get('request')
        if request:
            current_url = resolve(request.path_info).url_name
            if current_url == url_name:
                return css_class
    except Exception:
        pass
    return ''


@register.simple_tag(takes_context=True)
def is_active(context, url_pattern):
    """
    Check if current URL matches pattern.

    Usage: {% is_active '/users/' as active %}
    """
    try:
        request = context.get('request')
        if request:
            return request.path.startswith(url_pattern)
    except Exception:
        pass
    return False


@register.filter
def external_link(url):
    """
    Make URL an external link with target="_blank".

    Usage: {{ url|external_link }}
    """
    try:
        return mark_safe(
            f'<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>'
        )
    except Exception:
        return url


@register.filter
def urlize_with_target(text):
    """
    Convert URLs in text to links with target="_blank".

    Usage: {{ text|urlize_with_target }}
    """
    import re
    url_pattern = r'(https?://\S+)'
    replacement = r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>'
    return mark_safe(re.sub(url_pattern, replacement, str(text)))


@register.filter
def strip_protocol(url):
    """
    Remove protocol from URL.

    Usage: {{ url|strip_protocol }}
    """
    try:
        return url.replace('https://', '').replace('http://', '')
    except Exception:
        return url


@register.filter
def ensure_protocol(url, protocol='https'):
    """
    Ensure URL has a protocol.

    Usage: {{ url|ensure_protocol:"https" }}
    """
    try:
        if not url.startswith(('http://', 'https://')):
            return f'{protocol}://{url}'
        return url
    except Exception:
        return url
