"""
Sentry Error Tracking Integration for Django.

Usage:
    # settings.py
    SENTRY_DSN = 'https://xxx@xxx.ingest.sentry.io/xxx'
    SENTRY_ENVIRONMENT = 'production'
    SENTRY_RELEASE = 'myapp@1.0.0'

    # Initialize in wsgi.py or manage.py
    from django_extensions.sentry_integration import init_sentry
    init_sentry()

    # Capture exceptions
    from django_extensions.sentry_integration import capture_exception

    try:
        risky_operation()
    except Exception as e:
        capture_exception(e)
"""

from functools import wraps
from django.conf import settings


_sentry_initialized = False


def get_sentry():
    """Get sentry_sdk module."""
    try:
        import sentry_sdk
    except ImportError:
        raise ImportError("sentry-sdk is required. Install it with: pip install sentry-sdk")
    return sentry_sdk


def init_sentry(dsn=None, environment=None, release=None, **kwargs):
    """
    Initialize Sentry SDK.

    Args:
        dsn: Sentry DSN (defaults to SENTRY_DSN setting)
        environment: Environment name (defaults to SENTRY_ENVIRONMENT)
        release: Release version (defaults to SENTRY_RELEASE)
        **kwargs: Additional Sentry init options
    """
    global _sentry_initialized

    if _sentry_initialized:
        return

    sentry_sdk = get_sentry()

    dsn = dsn or getattr(settings, 'SENTRY_DSN', None)
    if not dsn:
        return  # Sentry not configured

    environment = environment or getattr(settings, 'SENTRY_ENVIRONMENT', None)
    release = release or getattr(settings, 'SENTRY_RELEASE', None)

    init_kwargs = {
        'dsn': dsn,
        'traces_sample_rate': getattr(settings, 'SENTRY_TRACES_SAMPLE_RATE', 0.1),
        'profiles_sample_rate': getattr(settings, 'SENTRY_PROFILES_SAMPLE_RATE', 0.1),
        'send_default_pii': getattr(settings, 'SENTRY_SEND_PII', False),
    }

    if environment:
        init_kwargs['environment'] = environment
    if release:
        init_kwargs['release'] = release

    # Add Django integration
    try:
        from sentry_sdk.integrations.django import DjangoIntegration
        init_kwargs.setdefault('integrations', [])
        init_kwargs['integrations'].append(DjangoIntegration())
    except ImportError:
        pass

    init_kwargs.update(kwargs)
    sentry_sdk.init(**init_kwargs)

    _sentry_initialized = True


def capture_exception(exception=None, **kwargs):
    """
    Capture an exception and send to Sentry.

    Args:
        exception: Exception instance (uses current if None)
        **kwargs: Additional context

    Returns:
        str: Event ID
    """
    sentry_sdk = get_sentry()

    with sentry_sdk.push_scope() as scope:
        for key, value in kwargs.items():
            scope.set_extra(key, value)

        return sentry_sdk.capture_exception(exception)


def capture_message(message, level='info', **kwargs):
    """
    Capture a message and send to Sentry.

    Args:
        message: Message text
        level: Log level ('debug', 'info', 'warning', 'error', 'fatal')
        **kwargs: Additional context

    Returns:
        str: Event ID
    """
    sentry_sdk = get_sentry()

    with sentry_sdk.push_scope() as scope:
        for key, value in kwargs.items():
            scope.set_extra(key, value)

        return sentry_sdk.capture_message(message, level=level)


def set_user(user_info):
    """
    Set user context.

    Args:
        user_info: Dict with user info (id, email, username, etc.)
                   or Django User instance
    """
    sentry_sdk = get_sentry()

    if hasattr(user_info, 'id'):
        # Django User instance
        info = {
            'id': str(user_info.id),
        }
        if hasattr(user_info, 'email'):
            info['email'] = user_info.email
        if hasattr(user_info, 'username'):
            info['username'] = user_info.username
        user_info = info

    sentry_sdk.set_user(user_info)


def set_tag(key, value):
    """
    Set a tag on the current scope.

    Args:
        key: Tag name
        value: Tag value
    """
    sentry_sdk = get_sentry()
    sentry_sdk.set_tag(key, value)


def set_context(name, context):
    """
    Set context on the current scope.

    Args:
        name: Context name
        context: Dict of context data
    """
    sentry_sdk = get_sentry()
    sentry_sdk.set_context(name, context)


def add_breadcrumb(message, category=None, level='info', data=None):
    """
    Add a breadcrumb.

    Args:
        message: Breadcrumb message
        category: Breadcrumb category
        level: Log level
        data: Additional data dict
    """
    sentry_sdk = get_sentry()

    crumb = {
        'message': message,
        'level': level,
    }

    if category:
        crumb['category'] = category
    if data:
        crumb['data'] = data

    sentry_sdk.add_breadcrumb(crumb)


def sentry_trace(op=None, name=None, description=None):
    """
    Decorator to trace a function with Sentry.

    Args:
        op: Operation type
        name: Transaction name
        description: Description

    Usage:
        @sentry_trace(op='task', name='process_order')
        def process_order(order_id):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sentry_sdk = get_sentry()

            transaction_name = name or func.__name__
            transaction_op = op or 'function'

            with sentry_sdk.start_transaction(
                op=transaction_op,
                name=transaction_name,
                description=description
            ):
                return func(*args, **kwargs)

        return wrapper
    return decorator


def sentry_span(op=None, description=None):
    """
    Decorator to create a span within a transaction.

    Args:
        op: Operation type
        description: Description

    Usage:
        @sentry_span(op='db', description='Fetch user data')
        def get_user_data(user_id):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sentry_sdk = get_sentry()

            with sentry_sdk.start_span(
                op=op or 'function',
                description=description or func.__name__
            ):
                return func(*args, **kwargs)

        return wrapper
    return decorator


class SentryContextManager:
    """
    Context manager for Sentry scope.

    Usage:
        with SentryContextManager() as scope:
            scope.set_tag('key', 'value')
            scope.set_extra('data', {'key': 'value'})
            risky_operation()
    """

    def __init__(self, **context):
        self.context = context
        self._scope = None

    def __enter__(self):
        sentry_sdk = get_sentry()
        self._scope = sentry_sdk.push_scope().__enter__()

        for key, value in self.context.items():
            if key == 'user':
                self._scope.set_user(value)
            elif key == 'tags':
                for tag_key, tag_value in value.items():
                    self._scope.set_tag(tag_key, tag_value)
            else:
                self._scope.set_extra(key, value)

        return self._scope

    def __exit__(self, exc_type, exc_val, exc_tb):
        sentry_sdk = get_sentry()
        sentry_sdk.pop_scope_unsafe()
        return False


def ignore_exception(*exception_classes):
    """
    Decorator to ignore specific exceptions in Sentry.

    Usage:
        @ignore_exception(ValueError, KeyError)
        def might_fail():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_classes:
                raise  # Re-raise but Sentry won't capture

        return wrapper
    return decorator
