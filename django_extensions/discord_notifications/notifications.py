"""
Discord Notifications Integration for Django.

Usage:
    # settings.py
    DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/...'

    # Send message
    from django_extensions.discord_notifications import send_webhook, send_embed

    send_webhook('Hello from Django!')

    send_embed(
        title='New Order',
        description='Order #123 placed',
        color=0x00ff00,
        fields=[
            {'name': 'Customer', 'value': 'John Doe'},
            {'name': 'Total', 'value': '$99.99', 'inline': True}
        ]
    )
"""

import json
import urllib.request
import urllib.error
from datetime import datetime
from django.conf import settings


class DiscordWebhook:
    """
    Discord Webhook client.

    Usage:
        webhook = DiscordWebhook()
        webhook.send('Hello Discord!')
        webhook.send_embed(title='Alert', description='Something happened', color=0xff0000)
    """

    def __init__(self, webhook_url=None, username=None, avatar_url=None):
        self.webhook_url = webhook_url or getattr(settings, 'DISCORD_WEBHOOK_URL', None)
        self.username = username
        self.avatar_url = avatar_url

        if not self.webhook_url:
            raise ValueError("webhook_url must be set or DISCORD_WEBHOOK_URL in settings")

    def send(self, content=None, embeds=None, username=None, avatar_url=None,
             tts=False, allowed_mentions=None, files=None):
        """
        Send a message to Discord.

        Args:
            content: Message content
            embeds: List of embed dicts
            username: Override username
            avatar_url: Override avatar URL
            tts: Text-to-speech
            allowed_mentions: Allowed mentions config

        Returns:
            bool: True if successful
        """
        payload = {}

        if content:
            payload['content'] = content
        if embeds:
            payload['embeds'] = embeds
        if username or self.username:
            payload['username'] = username or self.username
        if avatar_url or self.avatar_url:
            payload['avatar_url'] = avatar_url or self.avatar_url
        if tts:
            payload['tts'] = True
        if allowed_mentions:
            payload['allowed_mentions'] = allowed_mentions

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            self.webhook_url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )

        try:
            with urllib.request.urlopen(req) as response:
                return response.status in (200, 204)
        except urllib.error.HTTPError as e:
            if e.code == 204:  # No content is success
                return True
            return False

    def send_embed(self, title=None, description=None, url=None, color=None,
