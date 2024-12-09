# Discord Notifications

Discord webhook integration for notifications.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.discord_notifications',
]
```

## Configuration

```python
# settings.py
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/...'
DISCORD_DEFAULT_USERNAME = 'Django Bot'
DISCORD_DEFAULT_AVATAR_URL = 'https://example.com/avatar.png'
```

## Usage

### Simple Message

```python
from django_extensions.discord_notifications import send_message

send_message('Hello from Django!')

# With username
send_message('Alert!', username='Alert Bot')
```

### Webhook Function

```python
from django_extensions.discord_notifications import send_webhook

send_webhook(
    content='Server status update',
    username='Status Bot',
    avatar_url='https://example.com/bot.png'
)
```

### Embeds

```python
from django_extensions.discord_notifications import send_embed

send_embed(
    title='New Order',
    description='Order #12345 has been placed',
    color=0x00ff00,  # Green
    fields=[
        {'name': 'Customer', 'value': 'John Doe', 'inline': True},
        {'name': 'Amount', 'value': '$99.99', 'inline': True}
    ]
)
```

### Multiple Embeds

```python
from django_extensions.discord_notifications import send_webhook

send_webhook(
    content='Daily Report',
    embeds=[
        {
            'title': 'Sales',
            'description': 'Today: $1,234',
            'color': 0x00ff00
        },
        {
            'title': 'Users',
            'description': 'New signups: 42',
            'color': 0x0000ff
        }
    ]
)
```

### Rich Embeds

```python
send_embed(
    title='Alert',
    description='Server CPU usage high',
    color=0xff0000,
    author={'name': 'Monitoring Bot', 'icon_url': '...'},
    thumbnail={'url': 'https://...'},
    fields=[
        {'name': 'Server', 'value': 'web-01'},
        {'name': 'CPU', 'value': '95%'}
    ],
    footer={'text': 'Sent at 2024-01-15 10:30 UTC'},
    timestamp='2024-01-15T10:30:00Z'
)
```

### DiscordNotifier Class

```python
from django_extensions.discord_notifications import DiscordNotifier

notifier = DiscordNotifier()

notifier.info('Info message')
notifier.success('Success!')
notifier.warning('Warning!')
notifier.error('Error occurred!')
```

### Error Notifications

```python
from django_extensions.discord_notifications import notify_error

try:
    risky_operation()
except Exception as e:
    notify_error(e, include_traceback=True)
```

## License

MIT
