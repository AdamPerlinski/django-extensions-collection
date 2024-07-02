"""
Cache decorators - Enhanced caching utilities.

Usage:
    from django_extensions.cache_decorator import cache_result, cache_page_per_user

    @cache_result(timeout=3600, key_prefix='user_data')
    def get_user_data(user_id):
        ...

    @cache_page_per_user(timeout=300)
    def user_dashboard(request):
        ...
"""

import hashlib
from functools import wraps
from django.core.cache import cache


def make_cache_key(*args, **kwargs):
    """Generate a cache key from arguments."""
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f'{k}={v}' for k, v in sorted(kwargs.items()))
    key_string = ':'.join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cache_result(timeout=300, key_prefix='', cache_none=True, cache_alias='default'):
    """
    Decorator that caches the result of a function.

    Args:
        timeout: Cache timeout in seconds (default 300).
        key_prefix: Prefix for the cache key.
        cache_none: Whether to cache None results.
        cache_alias: Which cache backend to use.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            func_key = f'{func.__module__}.{func.__name__}'
            arg_key = make_cache_key(*args, **kwargs)
            cache_key = f'{key_prefix}:{func_key}:{arg_key}' if key_prefix else f'{func_key}:{arg_key}'

            # Try to get from cache
            from django.core.cache import caches
            cache_backend = caches[cache_alias]

            result = cache_backend.get(cache_key)
            if result is not None:
                return result

            # Check for cached None
            none_key = f'{cache_key}:none'
            if cache_none and cache_backend.get(none_key):
                return None

            # Call function and cache result
            result = func(*args, **kwargs)

            if result is None:
                if cache_none:
