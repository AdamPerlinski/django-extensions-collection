# AWS SNS Notifications

Amazon Simple Notification Service integration.

## Installation

```bash
pip install boto3
```

```python
INSTALLED_APPS = [
    'django_extensions.aws_sns_notifications',
]
```

## Configuration

```python
# settings.py
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_SNS_REGION = 'us-east-1'
AWS_SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:123456789:my-topic'
```

## Usage

### Publish to Topic

```python
from django_extensions.aws_sns_notifications import publish_message

# Simple message
publish_message('Hello, World!')

# With subject
publish_message('Order confirmed', subject='Order #12345')

# To specific topic
publish_message(
    'Alert!',
    topic_arn='arn:aws:sns:us-east-1:123456789:alerts'
)
```

### Send SMS

```python
from django_extensions.aws_sns_notifications import publish_sms

publish_sms(
    phone_number='+15551234567',
    message='Your verification code is 123456'
)

# With sender ID
publish_sms(
    phone_number='+15551234567',
    message='Your code is 123456',
    sender_id='MyApp'
)
```

### Push Notifications

```python
from django_extensions.aws_sns_notifications import publish_to_endpoint

publish_to_endpoint(
    endpoint_arn='arn:aws:sns:...:endpoint/APNS/...',
    message={
        'APNS': json.dumps({
            'aps': {'alert': 'New message!', 'badge': 1}
        })
    }
)
```

### SNS Notifier Class

```python
from django_extensions.aws_sns_notifications import SNSNotifier

notifier = SNSNotifier(topic_arn='arn:aws:sns:...')
notifier.publish('Hello!')
notifier.publish_json({'event': 'user_created', 'user_id': 123})
```

## Topic Management

```python
from django_extensions.aws_sns_notifications import (
    create_topic,
    subscribe_email,
    subscribe_sms
)

topic_arn = create_topic('my-notifications')
subscribe_email(topic_arn, 'user@example.com')
subscribe_sms(topic_arn, '+15551234567')
```

## License

MIT
