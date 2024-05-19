"""
RequestLoggingMiddleware - Log request/response details.

Usage:
    # settings.py
    MIDDLEWARE = [
        ...
        'django_extensions.request_logging_middleware.RequestLoggingMiddleware',
    ]

    # Optional settings
    REQUEST_LOGGING_ENABLED = True
    REQUEST_LOGGING_EXCLUDE_PATHS = ['/health/', '/static/']
"""

import logging
import time
from django.conf import settings


logger = logging.getLogger('django.request')


class RequestLoggingMiddleware:
    """
    Middleware that logs request and response information.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'REQUEST_LOGGING_ENABLED', True)
        self.exclude_paths = getattr(settings, 'REQUEST_LOGGING_EXCLUDE_PATHS', [
            '/static/', '/media/', '/favicon.ico', '/health/'
        ])
        self.log_headers = getattr(settings, 'REQUEST_LOGGING_HEADERS', False)
        self.log_body = getattr(settings, 'REQUEST_LOGGING_BODY', False)

    def __call__(self, request):
