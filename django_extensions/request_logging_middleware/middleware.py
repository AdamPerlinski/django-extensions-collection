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
        if not self.enabled or self.should_exclude(request.path):
            return self.get_response(request)

        start_time = time.time()

        # Log request
        self.log_request(request)

        response = self.get_response(request)

        # Log response
        duration = time.time() - start_time
        self.log_response(request, response, duration)

        return response

    def should_exclude(self, path):
        """Check if path should be excluded from logging."""
        return any(path.startswith(excluded) for excluded in self.exclude_paths)

    def log_request(self, request):
        """Log incoming request details."""
        user = getattr(request, 'user', None)
        user_str = str(user) if user and user.is_authenticated else 'anonymous'

        log_data = {
            'method': request.method,
            'path': request.path,
            'user': user_str,
            'ip': self.get_client_ip(request),
        }

        if self.log_headers:
            log_data['headers'] = dict(request.headers)

        if self.log_body and request.method in ('POST', 'PUT', 'PATCH'):
            log_data['body'] = self.get_request_body(request)

        logger.info(f"Request: {request.method} {request.path}", extra=log_data)

    def log_response(self, request, response, duration):
        """Log response details."""
        log_data = {
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
        }

        log_level = logging.INFO if response.status_code < 400 else logging.WARNING

        logger.log(
            log_level,
            f"Response: {request.method} {request.path} - {response.status_code} ({log_data['duration_ms']}ms)",
            extra=log_data
        )

    def get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    def get_request_body(self, request):
        """Get request body (truncated for safety)."""
        try:
            body = request.body.decode('utf-8')
            if len(body) > 1000:
                return body[:1000] + '... (truncated)'
            return body
        except Exception:
            return '<unable to decode>'
