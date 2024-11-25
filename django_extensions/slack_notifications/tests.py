"""Tests for Slack Notifications Integration."""

import pytest
import json
from unittest.mock import MagicMock, patch

from .notifications import (
    SlackClient,
    send_message,
    send_webhook,
    create_section_block,
    create_header_block,
    create_button,
    create_actions_block,
)


class TestSlackClient:
    """Test cases for SlackClient."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.SLACK_BOT_TOKEN = 'xoxb-test-token'
        settings.SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/T00/B00/XXX'
        return settings

    @pytest.fixture
    def mock_slack_client(self):
        """Create mock Slack client."""
        mock = MagicMock()
        return mock

    @pytest.fixture
    def client(self, mock_settings, mock_slack_client):
        """Create SlackClient with mocked client."""
        with patch('django_extensions.slack_notifications.notifications.get_slack_client', return_value=mock_slack_client):
            c = SlackClient()
            c._client = mock_slack_client
            return c

    def test_send_message(self, client, mock_slack_client):
        """Test sending a message."""
        mock_slack_client.chat_postMessage.return_value = {'ok': True, 'ts': '123.456'}

        result = client.send_message('#general', text='Hello!')

        assert result['ok'] is True
        mock_slack_client.chat_postMessage.assert_called_once()
        call_kwargs = mock_slack_client.chat_postMessage.call_args[1]
        assert call_kwargs['channel'] == '#general'
        assert call_kwargs['text'] == 'Hello!'

    def test_send_message_with_blocks(self, client, mock_slack_client):
        """Test sending message with blocks."""
        mock_slack_client.chat_postMessage.return_value = {'ok': True}

        blocks = [
            {'type': 'section', 'text': {'type': 'mrkdwn', 'text': 'Hello'}}
        ]
        client.send_message('#general', blocks=blocks)

        call_kwargs = mock_slack_client.chat_postMessage.call_args[1]
        assert call_kwargs['blocks'] == blocks

    def test_send_message_to_thread(self, client, mock_slack_client):
        """Test replying to a thread."""
        mock_slack_client.chat_postMessage.return_value = {'ok': True}

        client.send_message('#general', text='Reply', thread_ts='123.456')

        call_kwargs = mock_slack_client.chat_postMessage.call_args[1]
        assert call_kwargs['thread_ts'] == '123.456'

    def test_send_webhook(self, mock_settings):
        """Test sending via webhook."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            client = SlackClient(webhook_url='https://hooks.slack.com/test')
            result = client.send_webhook(text='Hello via webhook!')

            assert result is True
            mock_urlopen.assert_called_once()

    def test_send_webhook_with_options(self, mock_settings):
        """Test webhook with override options."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
