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
