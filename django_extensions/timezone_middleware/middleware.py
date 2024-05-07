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

    def __call__(self, request):
        tz = self.get_timezone(request)

        if tz:
            try:
                timezone.activate(zoneinfo.ZoneInfo(tz))
            except (KeyError, zoneinfo.ZoneInfoNotFoundError):
                timezone.deactivate()
        else:
            timezone.deactivate()

        response = self.get_response(request)
        return response

    def get_timezone(self, request):
        """
        Get the timezone for the current request.
        Override this method to customize timezone detection.
        """
        # Check session first
        tz = request.session.get('timezone')
        if tz:
            return tz

        # Check user profile
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Try common attribute names
            user = request.user
            if hasattr(user, 'timezone'):
                return user.timezone
            if hasattr(user, 'profile') and hasattr(user.profile, 'timezone'):
                return user.profile.timezone

        # Check cookies
        tz = request.COOKIES.get('timezone')
        if tz:
            return tz

        return None


def get_common_timezones():
    """Return a list of common timezones for use in forms."""
    return [
        ('UTC', 'UTC'),
        ('US/Eastern', 'US Eastern'),
        ('US/Central', 'US Central'),
        ('US/Mountain', 'US Mountain'),
        ('US/Pacific', 'US Pacific'),
        ('Europe/London', 'London'),
        ('Europe/Paris', 'Paris'),
        ('Europe/Berlin', 'Berlin'),
        ('Asia/Tokyo', 'Tokyo'),
        ('Asia/Shanghai', 'Shanghai'),
        ('Asia/Kolkata', 'India'),
        ('Australia/Sydney', 'Sydney'),
    ]


def get_all_timezones():
    """Return all available timezones."""
    import zoneinfo
    return sorted(zoneinfo.available_timezones())
