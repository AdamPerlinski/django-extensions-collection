"""
Slack Notifications Integration for Django.

Usage:
    # settings.py
    SLACK_BOT_TOKEN = 'xoxb-...'
    SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/...'

    # Send message via webhook
    from django_extensions.slack_notifications import send_webhook

    send_webhook(
        text='Hello from Django!',
        channel='#general',
        username='Bot'
    )

    # Send message via Bot API
    from django_extensions.slack_notifications import send_message

    send_message(
        channel='#general',
        text='Hello!',
        blocks=[...]  # Optional Block Kit blocks
    )
"""

import json
import urllib.request
import urllib.error
from django.conf import settings


def get_slack_client():
    """Get configured Slack client."""
    try:
        from slack_sdk import WebClient
    except ImportError:
        raise ImportError("slack_sdk is required. Install it with: pip install slack-sdk")

    token = getattr(settings, 'SLACK_BOT_TOKEN', None)
    if not token:
        raise ValueError("SLACK_BOT_TOKEN must be set")

    return WebClient(token=token)


class SlackClient:
    """
    Slack API client wrapper.

    Usage:
        client = SlackClient()
        client.send_message('#general', 'Hello!')
        client.send_file('#general', '/path/to/file.txt')
    """

    def __init__(self, token=None, webhook_url=None):
        self._client = None
        self._token = token
        self.webhook_url = webhook_url or getattr(settings, 'SLACK_WEBHOOK_URL', None)

    @property
    def client(self):
        if self._client is None:
            if self._token:
                try:
                    from slack_sdk import WebClient
                except ImportError:
                    raise ImportError("slack_sdk is required. Install it with: pip install slack-sdk")
                self._client = WebClient(token=self._token)
            else:
                self._client = get_slack_client()
        return self._client

    def send_message(self, channel, text=None, blocks=None, attachments=None,
                     thread_ts=None, reply_broadcast=False, unfurl_links=True,
                     unfurl_media=True, mrkdwn=True):
        """
        Send a message to a channel.

        Args:
            channel: Channel ID or name (e.g., '#general' or 'C1234567890')
            text: Message text (required if blocks not provided)
            blocks: Block Kit blocks
            attachments: Legacy attachments
            thread_ts: Thread timestamp to reply to
            reply_broadcast: Whether to also post to channel when replying to thread
            unfurl_links: Whether to unfurl URLs
            unfurl_media: Whether to unfurl media
            mrkdwn: Whether to parse markdown

        Returns:
            dict: Slack API response
        """
        params = {
            'channel': channel,
            'unfurl_links': unfurl_links,
            'unfurl_media': unfurl_media,
            'mrkdwn': mrkdwn,
        }

        if text:
            params['text'] = text
        if blocks:
            params['blocks'] = blocks
        if attachments:
            params['attachments'] = attachments
        if thread_ts:
            params['thread_ts'] = thread_ts
            if reply_broadcast:
                params['reply_broadcast'] = True

        return self.client.chat_postMessage(**params)

    def send_webhook(self, text=None, blocks=None, attachments=None,
                     channel=None, username=None, icon_emoji=None, icon_url=None):
        """
        Send a message via webhook.

        Args:
            text: Message text
            blocks: Block Kit blocks
            attachments: Legacy attachments
            channel: Override channel
            username: Override username
            icon_emoji: Override icon with emoji
            icon_url: Override icon with URL

        Returns:
            bool: True if successful
        """
        if not self.webhook_url:
            raise ValueError("webhook_url must be set")

        payload = {}
        if text:
            payload['text'] = text
        if blocks:
            payload['blocks'] = blocks
        if attachments:
            payload['attachments'] = attachments
        if channel:
            payload['channel'] = channel
        if username:
            payload['username'] = username
        if icon_emoji:
            payload['icon_emoji'] = icon_emoji
        if icon_url:
            payload['icon_url'] = icon_url

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            self.webhook_url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )

        try:
            with urllib.request.urlopen(req) as response:
                return response.status == 200
        except urllib.error.HTTPError:
            return False

    def send_file(self, channels, file=None, content=None, filename=None,
                  title=None, initial_comment=None, thread_ts=None):
        """
        Upload a file to Slack.

        Args:
            channels: Channel(s) to share file to
            file: Path to file
            content: File content (alternative to file path)
            filename: Filename to display
            title: Title of file
            initial_comment: Message with the file
            thread_ts: Thread to post to

        Returns:
            dict: Slack API response
        """
        params = {}

        if isinstance(channels, list):
            params['channels'] = ','.join(channels)
        else:
            params['channels'] = channels

        if file:
            params['file'] = file
        if content:
            params['content'] = content
        if filename:
            params['filename'] = filename
        if title:
            params['title'] = title
        if initial_comment:
            params['initial_comment'] = initial_comment
        if thread_ts:
            params['thread_ts'] = thread_ts

        return self.client.files_upload_v2(**params)

    def update_message(self, channel, ts, text=None, blocks=None, attachments=None):
        """Update an existing message."""
        params = {
            'channel': channel,
            'ts': ts,
        }
        if text:
            params['text'] = text
        if blocks:
            params['blocks'] = blocks
        if attachments:
            params['attachments'] = attachments

        return self.client.chat_update(**params)

    def delete_message(self, channel, ts):
        """Delete a message."""
        return self.client.chat_delete(channel=channel, ts=ts)

    def add_reaction(self, channel, ts, emoji):
        """Add a reaction to a message."""
        return self.client.reactions_add(
            channel=channel,
            timestamp=ts,
            name=emoji.strip(':')
        )

    def get_user_info(self, user_id):
        """Get user information."""
        return self.client.users_info(user=user_id)

    def list_channels(self, types='public_channel', limit=100):
        """List channels."""
        return self.client.conversations_list(types=types, limit=limit)

    def get_channel_history(self, channel, limit=100):
        """Get channel message history."""
        return self.client.conversations_history(channel=channel, limit=limit)


# Convenience functions

def send_message(channel, text=None, blocks=None, **kwargs):
    """Send a message to a Slack channel."""
    client = SlackClient()
    return client.send_message(channel, text=text, blocks=blocks, **kwargs)


def send_webhook(text=None, blocks=None, webhook_url=None, **kwargs):
    """Send a message via Slack webhook."""
    url = webhook_url or getattr(settings, 'SLACK_WEBHOOK_URL', None)
    client = SlackClient(webhook_url=url)
    return client.send_webhook(text=text, blocks=blocks, **kwargs)


def send_file(channels, file=None, content=None, **kwargs):
    """Upload a file to Slack."""
    client = SlackClient()
    return client.send_file(channels, file=file, content=content, **kwargs)


def post_to_channel(channel, text, **kwargs):
    """Simple wrapper to post text to a channel."""
    return send_message(channel, text=text, **kwargs)


# Block Kit helpers

def create_section_block(text, accessory=None, fields=None):
    """Create a section block."""
    block = {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': text
        }
    }
    if accessory:
        block['accessory'] = accessory
    if fields:
        block['fields'] = [{'type': 'mrkdwn', 'text': f} for f in fields]
    return block


def create_divider_block():
    """Create a divider block."""
    return {'type': 'divider'}


def create_header_block(text):
    """Create a header block."""
    return {
        'type': 'header',
        'text': {
            'type': 'plain_text',
            'text': text,
            'emoji': True
        }
    }


def create_context_block(elements):
    """Create a context block."""
    return {
        'type': 'context',
        'elements': [
            {'type': 'mrkdwn', 'text': e} if isinstance(e, str) else e
            for e in elements
        ]
    }


def create_button(text, action_id, value=None, style=None, url=None):
    """Create a button element."""
    button = {
        'type': 'button',
        'text': {
            'type': 'plain_text',
            'text': text,
            'emoji': True
        },
        'action_id': action_id,
    }
    if value:
        button['value'] = value
    if style:
        button['style'] = style  # 'primary' or 'danger'
    if url:
        button['url'] = url
    return button


def create_actions_block(elements):
    """Create an actions block with buttons."""
    return {
        'type': 'actions',
        'elements': elements
    }
