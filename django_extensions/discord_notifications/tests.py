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

    def test_send_embed_with_fields(self, webhook):
        """Test embed with fields."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.status = 204
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            webhook.send_embed(
                title='Order',
                fields=[
                    {'name': 'Product', 'value': 'Widget', 'inline': True},
                    {'name': 'Price', 'value': '$10', 'inline': True}
                ]
            )

            call_args = mock_urlopen.call_args[0][0]
            payload = json.loads(call_args.data.decode())
            assert len(payload['embeds'][0]['fields']) == 2

    def test_send_embed_with_timestamp(self, webhook):
        """Test embed with datetime timestamp."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.status = 204
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            now = datetime.now()
            webhook.send_embed(title='Event', timestamp=now)

            call_args = mock_urlopen.call_args[0][0]
            payload = json.loads(call_args.data.decode())
            assert 'timestamp' in payload['embeds'][0]

    def test_send_success(self, webhook):
        """Test success embed."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.status = 204
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            webhook.send_success('Operation Complete', 'All done!')

            call_args = mock_urlopen.call_args[0][0]
            payload = json.loads(call_args.data.decode())
            assert '✅' in payload['embeds'][0]['title']
            assert payload['embeds'][0]['color'] == 0x00ff00

    def test_send_error(self, webhook):
        """Test error embed."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.status = 204
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            webhook.send_error('Error Occurred', 'Something went wrong')

            call_args = mock_urlopen.call_args[0][0]
            payload = json.loads(call_args.data.decode())
            assert '❌' in payload['embeds'][0]['title']
            assert payload['embeds'][0]['color'] == 0xff0000


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/123/abc'
        return settings

    def test_send_webhook_function(self, mock_settings):
        """Test send_webhook function."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.status = 204
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            result = send_webhook('Hello!')

            assert result is True

    def test_send_embed_function(self, mock_settings):
        """Test send_embed function."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.status = 204
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            result = send_embed(title='Test', description='Desc')

            assert result is True


class TestEmbedBuilders:
    """Test embed builder functions."""

    def test_create_embed(self):
        """Test creating a base embed."""
        embed = create_embed(
            title='Test',
            description='Description',
            color=0x00ff00
        )

        assert embed['title'] == 'Test'
        assert embed['description'] == 'Description'
        assert embed['color'] == 0x00ff00

    def test_add_field(self):
        """Test adding a field."""
        embed = create_embed(title='Test')
        add_field(embed, 'Name', 'Value', inline=True)

        assert len(embed['fields']) == 1
        assert embed['fields'][0]['name'] == 'Name'
        assert embed['fields'][0]['inline'] is True

    def test_add_multiple_fields(self):
        """Test adding multiple fields."""
        embed = create_embed(title='Test')
        add_field(embed, 'Field 1', 'Value 1')
        add_field(embed, 'Field 2', 'Value 2')

        assert len(embed['fields']) == 2

    def test_add_author(self):
        """Test adding author."""
        embed = create_embed(title='Test')
        add_author(embed, 'John Doe', url='https://example.com', icon_url='https://example.com/avatar.png')

        assert embed['author']['name'] == 'John Doe'
        assert embed['author']['url'] == 'https://example.com'

    def test_add_footer(self):
        """Test adding footer."""
        embed = create_embed(title='Test')
        add_footer(embed, 'Footer text', icon_url='https://example.com/icon.png')

        assert embed['footer']['text'] == 'Footer text'
        assert embed['footer']['icon_url'] == 'https://example.com/icon.png'


class TestColors:
    """Test color constants."""

    def test_success_color(self):
        """Test success color."""
        assert Colors.SUCCESS == 0x00ff00

    def test_error_color(self):
        """Test error color."""
        assert Colors.ERROR == 0xff0000

    def test_blurple_color(self):
        """Test Discord blurple."""
        assert Colors.BLURPLE == 0x5865f2
