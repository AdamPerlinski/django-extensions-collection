# Request Logging Middleware

Log HTTP requests and responses.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.request_logging_middleware',
]

MIDDLEWARE = [
    'django_extensions.request_logging_middleware.RequestLoggingMiddleware',
    ...  # Place early in middleware stack
]
```

## Log Output

```
[2024-01-15 10:30:00] GET /api/users/ 200 0.045s 1.2KB
[2024-01-15 10:30:01] POST /api/users/ 201 0.123s 0.5KB
[2024-01-15 10:30:02] GET /api/users/1/ 404 0.012s 0.1KB
```

## Configuration

```python
# settings.py

REQUEST_LOGGING = {
    # Log level
    'LOG_LEVEL': 'INFO',

    # Log slow requests (seconds)
    'SLOW_REQUEST_THRESHOLD': 1.0,

    # Include request body
    'LOG_REQUEST_BODY': False,

    # Include response body
    'LOG_RESPONSE_BODY': False,

    # Max body size to log
    'MAX_BODY_LENGTH': 1000,

    # Exclude paths
    'EXCLUDE_PATHS': ['/health/', '/static/'],

    # Exclude by status code
    'EXCLUDE_STATUS_CODES': [200, 301, 302],

    # Custom logger name
    'LOGGER_NAME': 'django.request',
}
```

## Log Format

Default format includes:
- Timestamp
- HTTP method
- Path
- Status code
- Response time
- Response size

## Custom Formatter

```python
REQUEST_LOGGING = {
    'FORMAT': '[{timestamp}] {method} {path} {status} {duration}s {size}',
}
```

## Sensitive Data

Automatically redacts:
- Authorization headers
- Password fields
- Credit card numbers

```python
REQUEST_LOGGING = {
    'SENSITIVE_FIELDS': ['password', 'token', 'secret', 'credit_card'],
}
```

## File Logging

```python
LOGGING = {
    'handlers': {
        'request_file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/requests.log',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['request_file'],
            'level': 'INFO',
        },
    },
}
```

## License

MIT
