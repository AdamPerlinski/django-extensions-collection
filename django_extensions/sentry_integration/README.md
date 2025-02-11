# Sentry Integration

Sentry error tracking integration.

## Installation

```bash
pip install sentry-sdk
```

```python
INSTALLED_APPS = [
    'django_extensions.sentry_integration',
]
```

## Configuration

```python
# settings.py
SENTRY_DSN = 'https://...@sentry.io/...'

# Optional settings
SENTRY_ENVIRONMENT = 'production'
SENTRY_RELEASE = 'myapp@1.0.0'
SENTRY_TRACES_SAMPLE_RATE = 0.1
SENTRY_PROFILES_SAMPLE_RATE = 0.1
```

## Usage

### Automatic Setup

```python
from django_extensions.sentry_integration import init_sentry

# Call in settings.py or wsgi.py
init_sentry()
```

### Capture Exceptions

```python
from django_extensions.sentry_integration import capture_exception

try:
    risky_operation()
except Exception as e:
    capture_exception(e)
```

### Capture Messages

```python
from django_extensions.sentry_integration import capture_message

capture_message('Something happened', level='warning')
```

### Add Context

```python
from django_extensions.sentry_integration import set_user, set_context, set_tag

# User context
set_user({
    'id': user.id,
    'email': user.email,
    'username': user.username
})

# Custom context
set_context('order', {
    'order_id': order.id,
    'total': order.total
})

# Tags
set_tag('feature', 'checkout')
```

### Breadcrumbs

```python
from django_extensions.sentry_integration import add_breadcrumb

add_breadcrumb(
    category='user.action',
    message='User clicked checkout',
    level='info'
)
```

### Performance Monitoring

```python
from django_extensions.sentry_integration import start_transaction

with start_transaction(op='task', name='process_order') as transaction:
    with transaction.start_child(op='db', description='fetch order'):
        order = Order.objects.get(pk=order_id)

    with transaction.start_child(op='http', description='call payment API'):
        process_payment(order)
```

### SentryClient Class

```python
from django_extensions.sentry_integration import SentryClient

sentry = SentryClient()

sentry.capture_exception(exception)
sentry.capture_message('Alert!')
sentry.set_user({'id': 123})
sentry.add_breadcrumb(category='auth', message='User logged in')
```

## Django Integration

Automatically captures:
- Unhandled exceptions
- 500 errors
- Slow database queries
- Request/response data

## License

MIT
