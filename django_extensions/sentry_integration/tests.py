"""Tests for Sentry Integration."""

import pytest
from unittest.mock import MagicMock, patch

from .tracking import (
    capture_exception,
    capture_message,
    set_user,
    set_tag,
    set_context,
    add_breadcrumb,
    sentry_trace,
    sentry_span,
)


class TestSentryFunctions:
    """Test Sentry functions."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.SENTRY_DSN = 'https://xxx@xxx.ingest.sentry.io/xxx'
        settings.SENTRY_ENVIRONMENT = 'test'
        return settings

    @pytest.fixture
    def mock_sentry(self):
        """Create mock sentry_sdk."""
        mock = MagicMock()
        mock.push_scope.return_value.__enter__ = MagicMock()
        mock.push_scope.return_value.__exit__ = MagicMock(return_value=False)
        return mock

    def test_capture_exception(self, mock_settings, mock_sentry):
        """Test capturing exception."""
        with patch('django_extensions.sentry_integration.tracking.get_sentry', return_value=mock_sentry):
            exc = ValueError('test error')
            capture_exception(exc)

            mock_sentry.capture_exception.assert_called_once()

    def test_capture_exception_with_context(self, mock_settings, mock_sentry):
        """Test capturing exception with extra context."""
        mock_scope = MagicMock()
        mock_sentry.push_scope.return_value.__enter__.return_value = mock_scope

        with patch('django_extensions.sentry_integration.tracking.get_sentry', return_value=mock_sentry):
            exc = ValueError('test error')
            capture_exception(exc, user_id=123, action='test')

            mock_scope.set_extra.assert_any_call('user_id', 123)
            mock_scope.set_extra.assert_any_call('action', 'test')

    def test_capture_message(self, mock_settings, mock_sentry):
        """Test capturing message."""
        with patch('django_extensions.sentry_integration.tracking.get_sentry', return_value=mock_sentry):
            capture_message('Test message', level='warning')

            mock_sentry.capture_message.assert_called_with('Test message', level='warning')

    def test_set_user_dict(self, mock_settings, mock_sentry):
        """Test setting user with dict."""
        with patch('django_extensions.sentry_integration.tracking.get_sentry', return_value=mock_sentry):
            set_user({'id': '123', 'email': 'user@example.com'})

            mock_sentry.set_user.assert_called_with({'id': '123', 'email': 'user@example.com'})

    def test_set_user_model(self, mock_settings, mock_sentry):
