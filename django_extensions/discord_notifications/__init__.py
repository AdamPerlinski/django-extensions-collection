"""Discord notifications integration for Django."""

from .notifications import (
    DiscordWebhook,
    send_webhook,
    send_embed,
)

__all__ = [
    'DiscordWebhook',
    'send_webhook',
    'send_embed',
]
