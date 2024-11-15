"""Tests for Twilio SMS Integration."""

import pytest
from unittest.mock import MagicMock, patch

from .sms import (
    TwilioClient,
    send_sms,
    send_whatsapp,
    make_call,
    twiml_response,
)


class TestTwilioClient:
    """Test cases for TwilioClient."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.TWILIO_ACCOUNT_SID = 'AC123'
        settings.TWILIO_AUTH_TOKEN = 'token123'
        settings.TWILIO_PHONE_NUMBER = '+15551234567'
        return settings

    @pytest.fixture
    def mock_twilio_client(self):
        """Create mock Twilio client."""
        mock = MagicMock()
        return mock

    @pytest.fixture
    def client(self, mock_settings, mock_twilio_client):
        """Create TwilioClient with mocked client."""
        with patch('django_extensions.twilio_sms.sms.get_twilio_client', return_value=mock_twilio_client):
            c = TwilioClient()
            c._client = mock_twilio_client
            return c

    def test_send_sms(self, client, mock_twilio_client):
        """Test sending SMS."""
        mock_twilio_client.messages.create.return_value = MagicMock(sid='SM123', status='queued')

        result = client.send_sms('+15559876543', 'Hello!')

        assert result.sid == 'SM123'
        mock_twilio_client.messages.create.assert_called_once()
        call_kwargs = mock_twilio_client.messages.create.call_args[1]
        assert call_kwargs['to'] == '+15559876543'
        assert call_kwargs['body'] == 'Hello!'

    def test_send_sms_with_media(self, client, mock_twilio_client):
        """Test sending MMS with media."""
        mock_twilio_client.messages.create.return_value = MagicMock(sid='SM123')

        client.send_sms(
            '+15559876543',
            'Check this out!',
            media_url='https://example.com/image.jpg'
        )

        call_kwargs = mock_twilio_client.messages.create.call_args[1]
        assert call_kwargs['media_url'] == ['https://example.com/image.jpg']

    def test_send_sms_with_callback(self, client, mock_twilio_client):
        """Test SMS with status callback."""
        mock_twilio_client.messages.create.return_value = MagicMock(sid='SM123')

        client.send_sms(
            '+15559876543',
            'Hello!',
            status_callback='https://example.com/callback'
        )

        call_kwargs = mock_twilio_client.messages.create.call_args[1]
        assert call_kwargs['status_callback'] == 'https://example.com/callback'

    def test_send_whatsapp(self, client, mock_twilio_client):
        """Test sending WhatsApp message."""
        mock_twilio_client.messages.create.return_value = MagicMock(sid='SM123')

        client.send_whatsapp('+15559876543', 'Hello WhatsApp!')

        call_kwargs = mock_twilio_client.messages.create.call_args[1]
        assert call_kwargs['to'] == 'whatsapp:+15559876543'
        assert call_kwargs['from_'].startswith('whatsapp:')

    def test_send_whatsapp_already_formatted(self, client, mock_twilio_client):
