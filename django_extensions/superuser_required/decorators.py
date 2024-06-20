"""
superuser_required - Decorator to require superuser access.

Usage:
    from django_extensions.superuser_required import superuser_required

    @superuser_required
    def admin_view(request):
        ...

    # With custom login URL
    @superuser_required(login_url='/admin/login/')
    def admin_view(request):
        ...
"""

from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME


def superuser_required(function=None, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME,
                       raise_exception=False):
    """
    Decorator that requires the user to be a superuser.

    Args:
        function: The view function to decorate.
        login_url: URL to redirect unauthenticated users to.
        redirect_field_name: Query parameter name for the redirect URL.
        raise_exception: If True, raise 403 instead of redirecting.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user

            # Check if authenticated
            if not user.is_authenticated:
                if raise_exception:
                    return HttpResponseForbidden('Authentication required.')

                url = login_url or getattr(settings, 'LOGIN_URL', '/login/')
                redirect_url = f'{url}?{redirect_field_name}={request.path}'
                return redirect(redirect_url)

            # Check if superuser
            if not user.is_superuser:
                if raise_exception:
                    return HttpResponseForbidden('Superuser access required.')

                return HttpResponseForbidden(
                    'You do not have permission to access this page.'
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    if function:
        return decorator(function)

    return decorator


def staff_required(function=None, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME,
                   raise_exception=False):
    """
    Decorator that requires the user to be a staff member.
    Similar to superuser_required but for is_staff.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                if raise_exception:
                    return HttpResponseForbidden('Authentication required.')

                url = login_url or getattr(settings, 'LOGIN_URL', '/login/')
                redirect_url = f'{url}?{redirect_field_name}={request.path}'
                return redirect(redirect_url)

            if not user.is_staff:
                if raise_exception:
                    return HttpResponseForbidden('Staff access required.')

                return HttpResponseForbidden(
                    'You do not have permission to access this page.'
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    if function:
        return decorator(function)

    return decorator
