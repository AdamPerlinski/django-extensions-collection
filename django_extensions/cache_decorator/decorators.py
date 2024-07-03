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
                    cache_backend.set(none_key, True, timeout)
            else:
                cache_backend.set(cache_key, result, timeout)

            return result

        # Add method to invalidate this function's cache
        wrapper.invalidate = lambda *args, **kwargs: invalidate_function_cache(
            func, key_prefix, *args, **kwargs
        )

        return wrapper

    return decorator


def invalidate_function_cache(func, key_prefix, *args, **kwargs):
    """Invalidate cache for a specific function call."""
    func_key = f'{func.__module__}.{func.__name__}'
    arg_key = make_cache_key(*args, **kwargs)
    cache_key = f'{key_prefix}:{func_key}:{arg_key}' if key_prefix else f'{func_key}:{arg_key}'

    cache.delete(cache_key)
    cache.delete(f'{cache_key}:none')


def invalidate_cache(pattern):
    """
    Invalidate cache keys matching a pattern.

    Note: This only works with cache backends that support key scanning
    (like Redis with django-redis). For other backends, you may need
    to track keys manually.
    """
    try:
        # Try django-redis pattern deletion
        cache.delete_pattern(pattern)
    except AttributeError:
        # Fallback: just delete the exact key
        cache.delete(pattern)


def cache_page_per_user(timeout=300, cache_anonymous=True):
    """
    Decorator that caches page responses per user.

    Args:
        timeout: Cache timeout in seconds.
        cache_anonymous: Whether to cache for anonymous users.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Don't cache non-GET requests
            if request.method != 'GET':
                return view_func(request, *args, **kwargs)

            # Get user identifier
            if request.user.is_authenticated:
                user_id = request.user.pk
            elif cache_anonymous:
                user_id = 'anonymous'
            else:
                return view_func(request, *args, **kwargs)

            # Generate cache key
            view_key = f'{view_func.__module__}.{view_func.__name__}'
            path_key = make_cache_key(request.path, request.GET.urlencode())
            cache_key = f'page:{view_key}:{user_id}:{path_key}'

            # Try to get from cache
            response = cache.get(cache_key)
            if response is not None:
                return response

            # Generate response and cache it
            response = view_func(request, *args, **kwargs)

            # Only cache successful responses
            if hasattr(response, 'status_code') and response.status_code == 200:
                cache.set(cache_key, response, timeout)

            return response

        return wrapper

    return decorator


def cache_method(timeout=300, key_attr='pk'):
    """
    Decorator that caches method results using an instance attribute as key.

    Args:
        timeout: Cache timeout in seconds.
        key_attr: Instance attribute to use in cache key.
    """
    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            # Get instance identifier
            instance_key = getattr(self, key_attr, id(self))
            method_key = f'{self.__class__.__name__}.{method.__name__}'
            arg_key = make_cache_key(*args, **kwargs)
            cache_key = f'method:{method_key}:{instance_key}:{arg_key}'

            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Call method and cache result
            result = method(self, *args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, timeout)

            return result

        return wrapper

    return decorator
