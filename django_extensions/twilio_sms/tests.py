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
        """Test WhatsApp with already formatted number."""
        mock_twilio_client.messages.create.return_value = MagicMock(sid='SM123')

        client.send_whatsapp('whatsapp:+15559876543', 'Hello!')

        call_kwargs = mock_twilio_client.messages.create.call_args[1]
        assert call_kwargs['to'] == 'whatsapp:+15559876543'

    def test_make_call_with_url(self, client, mock_twilio_client):
        """Test making a call with URL."""
        mock_twilio_client.calls.create.return_value = MagicMock(sid='CA123')

        result = client.make_call(
            '+15559876543',
            url='https://example.com/twiml'
        )

        assert result.sid == 'CA123'
        call_kwargs = mock_twilio_client.calls.create.call_args[1]
        assert call_kwargs['url'] == 'https://example.com/twiml'

    def test_make_call_with_twiml(self, client, mock_twilio_client):
        """Test making a call with TwiML."""
        mock_twilio_client.calls.create.return_value = MagicMock(sid='CA123')

        client.make_call(
            '+15559876543',
            twiml='<Response><Say>Hello</Say></Response>'
        )

        call_kwargs = mock_twilio_client.calls.create.call_args[1]
        assert '<Say>Hello</Say>' in call_kwargs['twiml']

    def test_make_call_requires_url_or_twiml(self, client):
        """Test call requires url or twiml."""
        with pytest.raises(ValueError):
            client.make_call('+15559876543')

    def test_get_message(self, client, mock_twilio_client):
        """Test getting a message."""
        mock_msg = MagicMock(sid='SM123', body='Hello')
        mock_twilio_client.messages.return_value.fetch.return_value = mock_msg

        result = client.get_message('SM123')

        assert result.body == 'Hello'

    def test_list_messages(self, client, mock_twilio_client):
        """Test listing messages."""
        mock_twilio_client.messages.list.return_value = [
            MagicMock(sid='SM1'),
            MagicMock(sid='SM2'),
        ]

        result = client.list_messages(limit=10)

        assert len(result) == 2
        mock_twilio_client.messages.list.assert_called_with(limit=10)


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.TWILIO_ACCOUNT_SID = 'AC123'
        settings.TWILIO_AUTH_TOKEN = 'token123'
        settings.TWILIO_PHONE_NUMBER = '+15551234567'
        return settings

    def test_send_sms_function(self, mock_settings):
        """Test send_sms function."""
        with patch('django_extensions.twilio_sms.sms.get_twilio_client') as mock_get:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = MagicMock(sid='SM123')
            mock_get.return_value = mock_client

            result = send_sms('+15559876543', 'Hello!')

            assert result.sid == 'SM123'

    def test_send_whatsapp_function(self, mock_settings):
        """Test send_whatsapp function."""
        with patch('django_extensions.twilio_sms.sms.get_twilio_client') as mock_get:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = MagicMock(sid='SM123')
            mock_get.return_value = mock_client

            result = send_whatsapp('+15559876543', 'Hello!')

            assert result.sid == 'SM123'

    def test_make_call_function(self, mock_settings):
        """Test make_call function."""
        with patch('django_extensions.twilio_sms.sms.get_twilio_client') as mock_get:
            mock_client = MagicMock()
            mock_client.calls.create.return_value = MagicMock(sid='CA123')
            mock_get.return_value = mock_client

            result = make_call('+15559876543', url='https://example.com/twiml')

            assert result.sid == 'CA123'


class TestTwimlResponse:
    """Test TwiML response generation."""

    def test_say(self):
        """Test TwiML with say."""
        mock_voice_response = MagicMock()
        mock_voice_response.__str__ = lambda s: '<Response><Say>Hello</Say></Response>'

        with patch.dict('sys.modules', {'twilio.twiml.voice_response': MagicMock(VoiceResponse=MagicMock(return_value=mock_voice_response), Gather=MagicMock())}):
            with patch.dict('sys.modules', {'twilio.twiml.messaging_response': MagicMock()}):
                from django_extensions.twilio_sms.sms import twiml_response as twiml_fn
                result = twiml_fn(say='Hello')
                mock_voice_response.say.assert_called_with('Hello')

    def test_sms_response(self):
        """Test TwiML SMS response."""
        mock_msg_response = MagicMock()
        mock_msg_response.__str__ = lambda s: '<Response><Message>Hi</Message></Response>'

        with patch.dict('sys.modules', {
            'twilio': MagicMock(),
            'twilio.twiml': MagicMock(),
            'twilio.twiml.voice_response': MagicMock(VoiceResponse=MagicMock(), Gather=MagicMock()),
            'twilio.twiml.messaging_response': MagicMock(MessagingResponse=MagicMock(return_value=mock_msg_response))
        }):
            from django_extensions.twilio_sms.sms import twiml_response as twiml_fn
            result = twiml_fn(sms='Hi')
            mock_msg_response.message.assert_called_with('Hi')
