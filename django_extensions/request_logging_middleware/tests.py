"""Tests for RequestLoggingMiddleware."""

import pytest
from django.test import RequestFactory
from unittest.mock import MagicMock, patch

from .middleware import RequestLoggingMiddleware


class TestRequestLoggingMiddleware:
    """Test cases for RequestLoggingMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        response = MagicMock()
        response.status_code = 200
        return RequestLoggingMiddleware(lambda r: response)

    @pytest.fixture
    def mock_request(self):
        """Create a mock request."""
        factory = RequestFactory()
        req = factory.get('/test/')
        return req

    def test_should_exclude_static(self, middleware):
        """Test static paths are excluded."""
        assert middleware.should_exclude('/static/css/style.css') is True

    def test_should_not_exclude_api(self, middleware):
        """Test API paths are not excluded."""
        assert middleware.should_exclude('/api/users/') is False

    def test_get_client_ip_direct(self, middleware, mock_request):
        """Test getting direct client IP."""
        mock_request.META['REMOTE_ADDR'] = '127.0.0.1'
        ip = middleware.get_client_ip(mock_request)
        assert ip == '127.0.0.1'
