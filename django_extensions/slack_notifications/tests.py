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
            mock_urlopen.return_value = mock_response

            client = SlackClient(webhook_url='https://hooks.slack.com/test')
            client.send_webhook(
                text='Hello!',
                channel='#alerts',
                username='AlertBot',
                icon_emoji=':warning:'
            )

            call_args = mock_urlopen.call_args[0][0]
            payload = json.loads(call_args.data.decode())
            assert payload['channel'] == '#alerts'
            assert payload['username'] == 'AlertBot'
            assert payload['icon_emoji'] == ':warning:'

    def test_send_file(self, client, mock_slack_client):
        """Test uploading a file."""
        mock_slack_client.files_upload_v2.return_value = {'ok': True, 'file': {'id': 'F123'}}

        result = client.send_file(
            '#general',
            content='File contents',
            filename='test.txt',
            title='Test File'
        )

        assert result['ok'] is True
        call_kwargs = mock_slack_client.files_upload_v2.call_args[1]
        assert call_kwargs['content'] == 'File contents'
        assert call_kwargs['filename'] == 'test.txt'

    def test_update_message(self, client, mock_slack_client):
        """Test updating a message."""
        mock_slack_client.chat_update.return_value = {'ok': True}

        client.update_message('#general', '123.456', text='Updated text')

        mock_slack_client.chat_update.assert_called_once()
        call_kwargs = mock_slack_client.chat_update.call_args[1]
        assert call_kwargs['ts'] == '123.456'
        assert call_kwargs['text'] == 'Updated text'

    def test_delete_message(self, client, mock_slack_client):
        """Test deleting a message."""
        mock_slack_client.chat_delete.return_value = {'ok': True}

        client.delete_message('#general', '123.456')

        mock_slack_client.chat_delete.assert_called_with(channel='#general', ts='123.456')

    def test_add_reaction(self, client, mock_slack_client):
        """Test adding a reaction."""
        mock_slack_client.reactions_add.return_value = {'ok': True}

        client.add_reaction('#general', '123.456', ':thumbsup:')

        mock_slack_client.reactions_add.assert_called_with(
            channel='#general',
            timestamp='123.456',
            name='thumbsup'
        )


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.SLACK_BOT_TOKEN = 'xoxb-test-token'
        settings.SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/test'
        return settings

    def test_send_message_function(self, mock_settings):
        """Test send_message function."""
        with patch('django_extensions.slack_notifications.notifications.get_slack_client') as mock_get:
            mock_client = MagicMock()
            mock_client.chat_postMessage.return_value = {'ok': True}
            mock_get.return_value = mock_client

            result = send_message('#general', text='Hello!')

            assert result['ok'] is True

    def test_send_webhook_function(self, mock_settings):
        """Test send_webhook function."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            result = send_webhook(text='Hello!')

            assert result is True


class TestBlockKitHelpers:
    """Test Block Kit helper functions."""

    def test_create_section_block(self):
        """Test creating a section block."""
        block = create_section_block('Hello *world*!')

        assert block['type'] == 'section'
        assert block['text']['type'] == 'mrkdwn'
        assert block['text']['text'] == 'Hello *world*!'

    def test_create_section_with_fields(self):
        """Test section with fields."""
        block = create_section_block('Header', fields=['Field 1', 'Field 2'])

        assert len(block['fields']) == 2
        assert block['fields'][0]['text'] == 'Field 1'

    def test_create_header_block(self):
        """Test creating a header block."""
        block = create_header_block('Welcome!')

        assert block['type'] == 'header'
        assert block['text']['text'] == 'Welcome!'

    def test_create_button(self):
        """Test creating a button."""
        button = create_button('Click Me', 'button_click', value='123', style='primary')

        assert button['type'] == 'button'
        assert button['text']['text'] == 'Click Me'
        assert button['action_id'] == 'button_click'
        assert button['value'] == '123'
        assert button['style'] == 'primary'

    def test_create_actions_block(self):
        """Test creating actions block."""
        buttons = [
            create_button('Yes', 'yes_click'),
            create_button('No', 'no_click', style='danger')
        ]
        block = create_actions_block(buttons)

        assert block['type'] == 'actions'
        assert len(block['elements']) == 2
