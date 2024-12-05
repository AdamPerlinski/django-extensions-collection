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
                   fields=None, author=None, footer=None, image=None,
                   thumbnail=None, timestamp=None, **kwargs):
        """
        Send an embed message.

        Args:
            title: Embed title
            description: Embed description
            url: URL for title link
            color: Embed color (integer)
            fields: List of field dicts with name, value, inline
            author: Dict with name, url, icon_url
            footer: Dict with text, icon_url
            image: Dict with url
            thumbnail: Dict with url
            timestamp: ISO8601 timestamp

        Returns:
            bool: True if successful
        """
        embed = {}

        if title:
            embed['title'] = title
        if description:
            embed['description'] = description
        if url:
            embed['url'] = url
        if color is not None:
            embed['color'] = color
        if fields:
            embed['fields'] = fields
        if author:
            embed['author'] = author
        if footer:
            embed['footer'] = footer
        if image:
            embed['image'] = image if isinstance(image, dict) else {'url': image}
        if thumbnail:
            embed['thumbnail'] = thumbnail if isinstance(thumbnail, dict) else {'url': thumbnail}
        if timestamp:
            if isinstance(timestamp, datetime):
                embed['timestamp'] = timestamp.isoformat()
            else:
                embed['timestamp'] = timestamp

        return self.send(embeds=[embed], **kwargs)

    def send_success(self, title, description=None, **kwargs):
        """Send a green success embed."""
        return self.send_embed(
            title=f"✅ {title}",
            description=description,
            color=0x00ff00,
            **kwargs
        )

    def send_error(self, title, description=None, **kwargs):
        """Send a red error embed."""
        return self.send_embed(
            title=f"❌ {title}",
            description=description,
            color=0xff0000,
            **kwargs
        )

    def send_warning(self, title, description=None, **kwargs):
        """Send a yellow warning embed."""
        return self.send_embed(
            title=f"⚠️ {title}",
            description=description,
            color=0xffff00,
            **kwargs
        )

    def send_info(self, title, description=None, **kwargs):
        """Send a blue info embed."""
        return self.send_embed(
            title=f"ℹ️ {title}",
            description=description,
            color=0x0099ff,
            **kwargs
        )


# Convenience functions

def send_webhook(content=None, webhook_url=None, **kwargs):
    """Send a message to Discord webhook."""
    url = webhook_url or getattr(settings, 'DISCORD_WEBHOOK_URL', None)
    webhook = DiscordWebhook(webhook_url=url)
    return webhook.send(content=content, **kwargs)


def send_embed(title=None, description=None, webhook_url=None, **kwargs):
    """Send an embed to Discord webhook."""
    url = webhook_url or getattr(settings, 'DISCORD_WEBHOOK_URL', None)
    webhook = DiscordWebhook(webhook_url=url)
    return webhook.send_embed(title=title, description=description, **kwargs)


# Embed builders

def create_embed(title=None, description=None, color=None, url=None):
    """Create a base embed dict."""
    embed = {}
    if title:
        embed['title'] = title
    if description:
        embed['description'] = description
    if color is not None:
        embed['color'] = color
    if url:
        embed['url'] = url
    return embed


def add_field(embed, name, value, inline=False):
    """Add a field to an embed."""
    if 'fields' not in embed:
        embed['fields'] = []
    embed['fields'].append({
        'name': name,
        'value': value,
        'inline': inline
    })
    return embed


def add_author(embed, name, url=None, icon_url=None):
    """Add author to an embed."""
    author = {'name': name}
    if url:
        author['url'] = url
    if icon_url:
        author['icon_url'] = icon_url
    embed['author'] = author
    return embed


def add_footer(embed, text, icon_url=None):
    """Add footer to an embed."""
    footer = {'text': text}
    if icon_url:
        footer['icon_url'] = icon_url
    embed['footer'] = footer
    return embed


def add_image(embed, url):
    """Add image to an embed."""
    embed['image'] = {'url': url}
    return embed


def add_thumbnail(embed, url):
    """Add thumbnail to an embed."""
    embed['thumbnail'] = {'url': url}
    return embed


# Color constants
class Colors:
    """Common Discord embed colors."""
    SUCCESS = 0x00ff00
    ERROR = 0xff0000
    WARNING = 0xffff00
    INFO = 0x0099ff
    PRIMARY = 0x5865f2
    SECONDARY = 0x99aab5
    DANGER = 0xed4245
    BLURPLE = 0x5865f2
    GREEN = 0x57f287
    YELLOW = 0xfee75c
    FUCHSIA = 0xeb459e
    RED = 0xed4245
    WHITE = 0xffffff
    BLACK = 0x000000
