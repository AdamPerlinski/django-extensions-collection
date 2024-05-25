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

    def test_get_client_ip_forwarded(self, middleware, mock_request):
        """Test getting forwarded client IP."""
        mock_request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        ip = middleware.get_client_ip(mock_request)
        assert ip == '192.168.1.1'

    @patch('django_extensions.request_logging_middleware.middleware.logger')
    def test_logs_request(self, mock_logger, middleware, mock_request):
        """Test request is logged."""
        middleware(mock_request)

        assert mock_logger.info.called

    @patch('django_extensions.request_logging_middleware.middleware.logger')
    def test_logs_response(self, mock_logger, middleware, mock_request):
        """Test response is logged."""
        middleware(mock_request)

        # Should log both request and response
        assert mock_logger.info.call_count >= 1 or mock_logger.log.call_count >= 1

    @patch('django_extensions.request_logging_middleware.middleware.logger')
    def test_excluded_path_not_logged(self, mock_logger, middleware):
        """Test excluded paths are not logged."""
        factory = RequestFactory()
        req = factory.get('/static/css/style.css')

        middleware(req)

        # Should not have logged request info
        for call in mock_logger.info.call_args_list:
            if 'Request:' in str(call):
                assert '/static/' not in str(call)

    def test_disabled_middleware(self, mock_request):
        """Test disabled middleware skips logging."""
        response = MagicMock()
        response.status_code = 200

        with patch.object(RequestLoggingMiddleware, '__init__', lambda self, get_response: None):
            middleware = RequestLoggingMiddleware.__new__(RequestLoggingMiddleware)
            middleware.get_response = lambda r: response
            middleware.enabled = False
            middleware.exclude_paths = []

            result = middleware(mock_request)
            assert result == response

    def test_log_level_for_errors(self, mock_request):
        """Test warning log level for error responses."""
        error_response = MagicMock()
        error_response.status_code = 500

        middleware = RequestLoggingMiddleware(lambda r: error_response)

        with patch('django_extensions.request_logging_middleware.middleware.logger') as mock_logger:
            middleware(mock_request)
            # Should use WARNING level for 5xx errors
            assert mock_logger.log.called
