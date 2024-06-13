"""
anonymous_required - Decorator to require non-authenticated users.

Usage:
    from django_extensions.anonymous_required import anonymous_required

    @anonymous_required
    def login_view(request):
        ...

    # With custom redirect
    @anonymous_required(redirect_url='/dashboard/')
    def register_view(request):
        ...
"""

from functools import wraps
from django.shortcuts import redirect
from django.conf import settings


def anonymous_required(function=None, redirect_url=None):
    """
    Decorator that requires the user to NOT be authenticated.
    Useful for login and registration pages.

    Args:
        function: The view function to decorate.
        redirect_url: URL to redirect authenticated users to.
                     Defaults to settings.LOGIN_REDIRECT_URL or '/'.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                url = redirect_url or getattr(settings, 'LOGIN_REDIRECT_URL', '/')
                return redirect(url)

            return view_func(request, *args, **kwargs)

        return wrapper

    if function:
        return decorator(function)

    return decorator
