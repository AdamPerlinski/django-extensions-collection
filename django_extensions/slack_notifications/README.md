# Slack Notifications

Slack webhook integration for notifications.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.slack_notifications',
]
```

## Configuration

```python
# settings.py
SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/T.../B.../...'
SLACK_DEFAULT_CHANNEL = '#general'
SLACK_DEFAULT_USERNAME = 'Django Bot'
SLACK_DEFAULT_ICON = ':robot_face:'
```

## Usage

### Simple Message

```python
from django_extensions.slack_notifications import send_message

send_message('Hello from Django!')

# With channel
send_message('Alert!', channel='#alerts')
```

### Webhook Function

```python
from django_extensions.slack_notifications import send_webhook

send_webhook(
    text='Deployment complete!',
    channel='#deployments',
    username='Deploy Bot',
    icon_emoji=':rocket:'
)
```

### Rich Messages

```python
from django_extensions.slack_notifications import send_blocks

send_blocks([
    {
        'type': 'header',
        'text': {'type': 'plain_text', 'text': 'New Order'}
    },
    {
        'type': 'section',
        'fields': [
            {'type': 'mrkdwn', 'text': '*Order ID:*\n#12345'},
            {'type': 'mrkdwn', 'text': '*Amount:*\n$99.99'}
        ]
    }
])
```

### Attachments

```python
send_webhook(
    text='Build status',
    attachments=[
        {
            'color': '#36a64f',
            'title': 'Build #123 Passed',
            'fields': [
                {'title': 'Branch', 'value': 'main', 'short': True},
                {'title': 'Duration', 'value': '2m 30s', 'short': True}
            ]
        }
    ]
)
```

### SlackNotifier Class

```python
from django_extensions.slack_notifications import SlackNotifier

notifier = SlackNotifier(channel='#alerts')

notifier.info('Info message')
notifier.success('Success!')
notifier.warning('Warning!')
notifier.error('Error occurred!')
```

### Error Notifications

```python
from django_extensions.slack_notifications import notify_error

try:
    risky_operation()
except Exception as e:
    notify_error(e, context={'user_id': 123})
```

## Channel Targeting

```python
# Public channel
send_message('Hello', channel='#general')

# Private channel
send_message('Hello', channel='#private-channel')

# Direct message
send_message('Hello', channel='@username')
```

## License

MIT
