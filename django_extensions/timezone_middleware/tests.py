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

