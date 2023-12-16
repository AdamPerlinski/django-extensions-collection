"""
URLValidator - Extended URL validator with additional options.

Usage:
    from django_extensions.url_validator import URLValidator

    class Bookmark(models.Model):
        url = models.URLField(validators=[URLValidator(
            allowed_schemes=['https'],
            blocked_domains=['example.com']
        )])
"""

import re
from urllib.parse import urlparse
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator as DjangoURLValidator
from django.utils.deconstruct import deconstructible


@deconstructible
class URLValidator(DjangoURLValidator):
    """
    Extended URL validator with additional features.
    """

    def __init__(
        self,
        schemes=None,
        allowed_schemes=None,
        allowed_domains=None,
        blocked_domains=None,
        require_tld=True,
        message=None,
        code=None,
    ):
        """
        Initialize the validator.

        Args:
            schemes: Deprecated, use allowed_schemes instead.
            allowed_schemes: List of allowed URL schemes (e.g., ['http', 'https']).
            allowed_domains: List of allowed domains (whitelist).
            blocked_domains: List of blocked domains (blacklist).
            require_tld: Whether to require a top-level domain.
            message: Custom error message.
            code: Custom error code.
        """
        self.allowed_domains = allowed_domains
        self.blocked_domains = blocked_domains
        self.require_tld = require_tld

        # Handle schemes
        if allowed_schemes:
            schemes = allowed_schemes
        elif schemes is None:
            schemes = ['http', 'https']

        super().__init__(schemes=schemes, message=message or self.message)
