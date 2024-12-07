"""Tests for Discord Notifications Integration."""

import pytest
import json
from unittest.mock import MagicMock, patch
from datetime import datetime

from .notifications import (
    DiscordWebhook,
    send_webhook,
    send_embed,
    create_embed,
    add_field,
    add_author,
    add_footer,
    Colors,
)


class TestDiscordWebhook:
    """Test cases for DiscordWebhook."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/123/abc'
        return settings

    @pytest.fixture
    def webhook(self, mock_settings):
        """Create webhook instance."""
        return DiscordWebhook()

    def test_init_from_settings(self, mock_settings):
        """Test webhook initializes from settings."""
        webhook = DiscordWebhook()
        assert webhook.webhook_url == 'https://discord.com/api/webhooks/123/abc'

    def test_init_with_url(self):
        """Test webhook with explicit URL."""
        webhook = DiscordWebhook(webhook_url='https://discord.com/api/webhooks/custom')
        assert webhook.webhook_url == 'https://discord.com/api/webhooks/custom'

    def test_init_with_options(self):
        """Test webhook with username and avatar."""
        webhook = DiscordWebhook(
            webhook_url='https://discord.com/api/webhooks/test',
            username='TestBot',
            avatar_url='https://example.com/avatar.png'
        )
        assert webhook.username == 'TestBot'
        assert webhook.avatar_url == 'https://example.com/avatar.png'

    def test_init_requires_url(self, settings):
        """Test init fails without URL."""
        settings.DISCORD_WEBHOOK_URL = None
        with pytest.raises(ValueError):
            DiscordWebhook()

    def test_send_message(self, webhook):
        """Test sending a simple message."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.status = 204
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            result = webhook.send('Hello Discord!')

            assert result is True
            call_args = mock_urlopen.call_args[0][0]
            payload = json.loads(call_args.data.decode())
            assert payload['content'] == 'Hello Discord!'

    def test_send_with_username(self, webhook):
        """Test sending with username override."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.status = 204
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            webhook.send('Hello!', username='CustomBot')

            call_args = mock_urlopen.call_args[0][0]
            payload = json.loads(call_args.data.decode())
            assert payload['username'] == 'CustomBot'

    def test_send_embed(self, webhook):
        """Test sending an embed."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.status = 204
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            result = webhook.send_embed(
                title='Test Embed',
                description='This is a test',
                color=0x00ff00
            )

            assert result is True
            call_args = mock_urlopen.call_args[0][0]
            payload = json.loads(call_args.data.decode())
            assert len(payload['embeds']) == 1
            assert payload['embeds'][0]['title'] == 'Test Embed'
            assert payload['embeds'][0]['color'] == 0x00ff00

