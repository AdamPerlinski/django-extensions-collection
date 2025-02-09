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
        """Test setting user with model instance."""
        with patch('django_extensions.sentry_integration.tracking.get_sentry', return_value=mock_sentry):
            mock_user = MagicMock()
            mock_user.id = 123
            mock_user.email = 'user@example.com'
            mock_user.username = 'johndoe'

            set_user(mock_user)

            call_args = mock_sentry.set_user.call_args[0][0]
            assert call_args['id'] == '123'
            assert call_args['email'] == 'user@example.com'
            assert call_args['username'] == 'johndoe'

    def test_set_tag(self, mock_settings, mock_sentry):
        """Test setting tag."""
        with patch('django_extensions.sentry_integration.tracking.get_sentry', return_value=mock_sentry):
            set_tag('environment', 'production')

            mock_sentry.set_tag.assert_called_with('environment', 'production')

    def test_set_context(self, mock_settings, mock_sentry):
        """Test setting context."""
        with patch('django_extensions.sentry_integration.tracking.get_sentry', return_value=mock_sentry):
            set_context('order', {'id': 123, 'total': 99.99})

            mock_sentry.set_context.assert_called_with('order', {'id': 123, 'total': 99.99})

    def test_add_breadcrumb(self, mock_settings, mock_sentry):
        """Test adding breadcrumb."""
        with patch('django_extensions.sentry_integration.tracking.get_sentry', return_value=mock_sentry):
            add_breadcrumb(
                'User clicked button',
                category='ui',
                level='info',
                data={'button': 'submit'}
            )

            mock_sentry.add_breadcrumb.assert_called_once()
            call_args = mock_sentry.add_breadcrumb.call_args[0][0]
            assert call_args['message'] == 'User clicked button'
            assert call_args['category'] == 'ui'


class TestSentryDecorators:
    """Test Sentry decorators."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.SENTRY_DSN = 'https://xxx@xxx.ingest.sentry.io/xxx'
        return settings

    @pytest.fixture
    def mock_sentry(self):
        """Create mock sentry_sdk."""
        mock = MagicMock()
        mock_transaction = MagicMock()
        mock_transaction.__enter__ = MagicMock()
        mock_transaction.__exit__ = MagicMock(return_value=False)
        mock.start_transaction.return_value = mock_transaction
        mock.start_span.return_value = mock_transaction
        return mock

    def test_sentry_trace_decorator(self, mock_settings, mock_sentry):
        """Test sentry_trace decorator."""
        with patch('django_extensions.sentry_integration.tracking.get_sentry', return_value=mock_sentry):
            @sentry_trace(op='task', name='test_task')
            def my_task():
                return 'done'

            result = my_task()

            assert result == 'done'
            mock_sentry.start_transaction.assert_called_once()
            call_kwargs = mock_sentry.start_transaction.call_args[1]
            assert call_kwargs['op'] == 'task'
            assert call_kwargs['name'] == 'test_task'

    def test_sentry_span_decorator(self, mock_settings, mock_sentry):
        """Test sentry_span decorator."""
        with patch('django_extensions.sentry_integration.tracking.get_sentry', return_value=mock_sentry):
            @sentry_span(op='db', description='fetch data')
            def fetch_data():
                return [1, 2, 3]

            result = fetch_data()

            assert result == [1, 2, 3]
            mock_sentry.start_span.assert_called_once()
            call_kwargs = mock_sentry.start_span.call_args[1]
            assert call_kwargs['op'] == 'db'
            assert call_kwargs['description'] == 'fetch data'

    def test_sentry_trace_uses_function_name(self, mock_settings, mock_sentry):
        """Test trace uses function name as default."""
        with patch('django_extensions.sentry_integration.tracking.get_sentry', return_value=mock_sentry):
            @sentry_trace()
            def process_order():
                pass

            process_order()

            call_kwargs = mock_sentry.start_transaction.call_args[1]
            assert call_kwargs['name'] == 'process_order'
