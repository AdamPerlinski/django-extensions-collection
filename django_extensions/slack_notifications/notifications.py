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
