"""
TimezoneMiddleware - Activate user's timezone for each request.

Usage:
    # settings.py
    MIDDLEWARE = [
        ...
        'django_extensions.timezone_middleware.TimezoneMiddleware',
    ]

    # Set timezone in session or user profile
    request.session['timezone'] = 'America/New_York'
    # or
    user.profile.timezone = 'Europe/London'
"""

import zoneinfo
from django.utils import timezone


class TimezoneMiddleware:
    """
    Middleware that activates the user's timezone for each request.

    Looks for timezone in:
    1. request.session['timezone']
    2. request.user.timezone (if authenticated)
    3. request.COOKIES['timezone']
    """

    def __init__(self, get_response):
        self.get_response = get_response

