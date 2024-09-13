"""Tests for AWS SES Email Backend."""

import pytest
from unittest.mock import MagicMock, patch
from django.core.mail import EmailMessage, EmailMultiAlternatives

from .backend import SESEmailBackend, send_ses_email, send_templated_email


class TestSESEmailBackend:
    """Test cases for SESEmailBackend."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.AWS_SES_REGION = 'us-east-1'
        settings.AWS_ACCESS_KEY_ID = 'test-key'
        settings.AWS_SECRET_ACCESS_KEY = 'test-secret'
        settings.DEFAULT_FROM_EMAIL = 'noreply@example.com'
        return settings

    @pytest.fixture
    def mock_client(self):
        """Create mock SES client."""
        client = MagicMock()
        client.send_email.return_value = {'MessageId': 'test-id'}
        return client

    @pytest.fixture
    def backend(self, mock_settings, mock_client):
        """Create backend with mocked client."""
        with patch('django_extensions.aws_ses_email.backend.get_ses_client', return_value=mock_client):
            b = SESEmailBackend()
            b._client = mock_client
            return b

    def test_send_simple_email(self, backend, mock_client):
        """Test sending a simple email."""
        message = EmailMessage(
            subject='Test Subject',
            body='Test body',
            from_email='sender@example.com',
            to=['recipient@example.com'],
        )

        num_sent = backend.send_messages([message])

        assert num_sent == 1
        mock_client.send_email.assert_called_once()
        call_kwargs = mock_client.send_email.call_args[1]
        assert call_kwargs['Source'] == 'sender@example.com'
        assert call_kwargs['Destination']['ToAddresses'] == ['recipient@example.com']

    def test_send_html_email(self, backend, mock_client):
        """Test sending HTML email."""
        message = EmailMultiAlternatives(
            subject='Test Subject',
            body='Plain text',
            from_email='sender@example.com',
            to=['recipient@example.com'],
        )
        message.attach_alternative('<p>HTML content</p>', 'text/html')

        backend.send_messages([message])

        call_kwargs = mock_client.send_email.call_args[1]
        assert 'Html' in call_kwargs['Message']['Body']
        assert call_kwargs['Message']['Body']['Html']['Data'] == '<p>HTML content</p>'

    def test_send_with_cc_bcc(self, backend, mock_client):
        """Test sending with CC and BCC."""
        message = EmailMessage(
            subject='Test',
            body='Body',
            from_email='sender@example.com',
            to=['to@example.com'],
            cc=['cc@example.com'],
            bcc=['bcc@example.com'],
        )

        backend.send_messages([message])

        call_kwargs = mock_client.send_email.call_args[1]
        assert call_kwargs['Destination']['CcAddresses'] == ['cc@example.com']
        assert call_kwargs['Destination']['BccAddresses'] == ['bcc@example.com']

    def test_send_with_reply_to(self, backend, mock_client):
        """Test sending with reply-to."""
        message = EmailMessage(
            subject='Test',
            body='Body',
            from_email='sender@example.com',
            to=['to@example.com'],
            reply_to=['reply@example.com'],
        )

        backend.send_messages([message])

        call_kwargs = mock_client.send_email.call_args[1]
        assert call_kwargs['ReplyToAddresses'] == ['reply@example.com']

    def test_send_multiple_messages(self, backend, mock_client):
        """Test sending multiple messages."""
        messages = [
