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
            EmailMessage('Subject 1', 'Body 1', 'from@example.com', ['to1@example.com']),
            EmailMessage('Subject 2', 'Body 2', 'from@example.com', ['to2@example.com']),
        ]

        num_sent = backend.send_messages(messages)

        assert num_sent == 2
        assert mock_client.send_email.call_count == 2

    def test_empty_recipients_skipped(self, backend, mock_client):
        """Test messages with no recipients are skipped."""
        message = EmailMessage(
            subject='Test',
            body='Body',
            from_email='sender@example.com',
            to=[],
        )

        num_sent = backend.send_messages([message])

        assert num_sent == 0
        mock_client.send_email.assert_not_called()

    def test_fail_silently(self, mock_settings, mock_client):
        """Test fail_silently option."""
        mock_client.send_email.side_effect = Exception('SES Error')

        with patch('django_extensions.aws_ses_email.backend.get_ses_client', return_value=mock_client):
            backend = SESEmailBackend(fail_silently=True)
            backend._client = mock_client

            message = EmailMessage('Test', 'Body', 'from@example.com', ['to@example.com'])
            num_sent = backend.send_messages([message])

            assert num_sent == 0

    def test_configuration_set(self, mock_settings, mock_client):
        """Test configuration set is included."""
        mock_settings.AWS_SES_CONFIGURATION_SET = 'my-config-set'

        with patch('django_extensions.aws_ses_email.backend.get_ses_client', return_value=mock_client):
            backend = SESEmailBackend()
            backend._client = mock_client

            message = EmailMessage('Test', 'Body', 'from@example.com', ['to@example.com'])
            backend.send_messages([message])

            call_kwargs = mock_client.send_email.call_args[1]
            assert call_kwargs['ConfigurationSetName'] == 'my-config-set'


class TestSendSesEmail:
    """Test send_ses_email function."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.AWS_SES_REGION = 'us-east-1'
        settings.AWS_ACCESS_KEY_ID = 'test-key'
        settings.AWS_SECRET_ACCESS_KEY = 'test-secret'
        settings.DEFAULT_FROM_EMAIL = 'noreply@example.com'
        return settings

    def test_send_simple(self, mock_settings):
        """Test simple email send."""
        with patch('django_extensions.aws_ses_email.backend.get_ses_client') as mock_get:
            mock_client = MagicMock()
            mock_client.send_email.return_value = {'MessageId': 'test-123'}
            mock_get.return_value = mock_client

            result = send_ses_email(
                subject='Test',
                body='Hello',
                to=['user@example.com'],
                from_email='sender@example.com'
            )

            assert result['MessageId'] == 'test-123'
            mock_client.send_email.assert_called_once()

    def test_send_with_html(self, mock_settings):
        """Test sending with HTML body."""
        with patch('django_extensions.aws_ses_email.backend.get_ses_client') as mock_get:
            mock_client = MagicMock()
            mock_get.return_value = mock_client

            send_ses_email(
                subject='Test',
                body='Plain text',
                html_body='<p>HTML</p>',
                to=['user@example.com']
            )

            call_kwargs = mock_client.send_email.call_args[1]
            assert 'Html' in call_kwargs['Message']['Body']

    def test_send_with_tags(self, mock_settings):
        """Test sending with tags."""
        with patch('django_extensions.aws_ses_email.backend.get_ses_client') as mock_get:
            mock_client = MagicMock()
            mock_get.return_value = mock_client

            send_ses_email(
                subject='Test',
                body='Body',
                to=['user@example.com'],
                tags={'campaign': 'welcome', 'source': 'signup'}
            )

            call_kwargs = mock_client.send_email.call_args[1]
            assert 'Tags' in call_kwargs
            assert len(call_kwargs['Tags']) == 2

    def test_string_recipient_converted_to_list(self, mock_settings):
        """Test single recipient string is converted to list."""
        with patch('django_extensions.aws_ses_email.backend.get_ses_client') as mock_get:
            mock_client = MagicMock()
            mock_get.return_value = mock_client

            send_ses_email(
                subject='Test',
                body='Body',
                to='user@example.com'
            )

            call_kwargs = mock_client.send_email.call_args[1]
            assert call_kwargs['Destination']['ToAddresses'] == ['user@example.com']


class TestSendTemplatedEmail:
    """Test send_templated_email function."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.AWS_SES_REGION = 'us-east-1'
        settings.AWS_ACCESS_KEY_ID = 'test-key'
        settings.AWS_SECRET_ACCESS_KEY = 'test-secret'
        settings.DEFAULT_FROM_EMAIL = 'noreply@example.com'
        return settings

    def test_send_templated(self, mock_settings):
        """Test sending templated email."""
        with patch('django_extensions.aws_ses_email.backend.get_ses_client') as mock_get:
            mock_client = MagicMock()
            mock_client.send_templated_email.return_value = {'MessageId': 'test-456'}
            mock_get.return_value = mock_client

            result = send_templated_email(
                template_name='WelcomeEmail',
                template_data={'name': 'John', 'link': 'https://example.com'},
                to=['user@example.com']
            )

            assert result['MessageId'] == 'test-456'
            call_kwargs = mock_client.send_templated_email.call_args[1]
            assert call_kwargs['Template'] == 'WelcomeEmail'
            assert '"name": "John"' in call_kwargs['TemplateData']
