"""Tests for TimezoneMiddleware."""

import pytest
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from unittest.mock import MagicMock

from .middleware import TimezoneMiddleware, get_common_timezones, get_all_timezones


class TestTimezoneMiddleware:
    """Test cases for TimezoneMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        return TimezoneMiddleware(lambda r: MagicMock())

    @pytest.fixture
    def mock_request(self):
        """Create a mock request."""
        factory = RequestFactory()
        req = factory.get('/')
        req.session = {}
        req.user = AnonymousUser()
        req.COOKIES = {}
        return req

    def test_no_timezone(self, middleware, mock_request):
        """Test when no timezone is set."""
        tz = middleware.get_timezone(mock_request)
        assert tz is None

    def test_session_timezone(self, middleware, mock_request):
        """Test timezone from session."""
        mock_request.session['timezone'] = 'America/New_York'

        tz = middleware.get_timezone(mock_request)
        assert tz == 'America/New_York'

    def test_cookie_timezone(self, middleware, mock_request):
        """Test timezone from cookie."""
        mock_request.COOKIES['timezone'] = 'Europe/London'

        tz = middleware.get_timezone(mock_request)
        assert tz == 'Europe/London'

    def test_session_takes_priority(self, middleware, mock_request):
        """Test session takes priority over cookies."""
        mock_request.session['timezone'] = 'America/New_York'
        mock_request.COOKIES['timezone'] = 'Europe/London'

        tz = middleware.get_timezone(mock_request)
        assert tz == 'America/New_York'

    def test_user_timezone(self, middleware, mock_request):
        """Test timezone from user attribute."""
        user = MagicMock()
        user.is_authenticated = True
        user.timezone = 'Asia/Tokyo'
        mock_request.user = user

        tz = middleware.get_timezone(mock_request)
        assert tz == 'Asia/Tokyo'

    def test_user_profile_timezone(self, middleware, mock_request):
        """Test timezone from user profile."""
        profile = MagicMock()
        profile.timezone = 'Australia/Sydney'

        user = MagicMock()
        user.is_authenticated = True
        user.profile = profile
        del user.timezone  # Make sure user.timezone doesn't exist
        mock_request.user = user

        tz = middleware.get_timezone(mock_request)
        assert tz == 'Australia/Sydney'

    def test_middleware_call(self, mock_request):
        """Test middleware __call__ method."""
        mock_request.session['timezone'] = 'America/New_York'

        response = MagicMock()
        get_response = MagicMock(return_value=response)

        middleware = TimezoneMiddleware(get_response)
        result = middleware(mock_request)

        assert result == response
        get_response.assert_called_once_with(mock_request)


class TestTimezoneHelpers:
    """Test timezone helper functions."""

    def test_get_common_timezones(self):
        """Test get_common_timezones returns list."""
        timezones = get_common_timezones()

        assert isinstance(timezones, list)
        assert len(timezones) > 0
        assert all(len(tz) == 2 for tz in timezones)  # (value, label) tuples

    def test_get_all_timezones(self):
        """Test get_all_timezones returns all zones."""
        timezones = get_all_timezones()

        assert isinstance(timezones, list)
        assert 'UTC' in timezones
        assert 'America/New_York' in timezones
        # Should be sorted
        assert timezones == sorted(timezones)
