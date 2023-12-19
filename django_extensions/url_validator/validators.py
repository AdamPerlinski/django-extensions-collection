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

        if code:
            self.code = code

    def __call__(self, value):
        if not value:
            return

        # Run parent validation
        super().__call__(value)

        # Parse URL
        parsed = urlparse(value)
        domain = parsed.netloc.lower()

        # Remove port if present
        if ':' in domain:
            domain = domain.split(':')[0]

        # Check TLD requirement
        if self.require_tld and '.' not in domain:
            raise ValidationError(
                "URL must contain a valid domain with TLD.",
                code='no_tld'
            )

        # Check allowed domains
        if self.allowed_domains:
            if not self._domain_matches(domain, self.allowed_domains):
                raise ValidationError(
                    f"Domain not allowed. Allowed domains: {', '.join(self.allowed_domains)}",
                    code='domain_not_allowed'
                )

        # Check blocked domains
        if self.blocked_domains:
            if self._domain_matches(domain, self.blocked_domains):
                raise ValidationError(
                    "This domain is not allowed.",
                    code='domain_blocked'
                )

    def _domain_matches(self, domain, domain_list):
        """Check if domain matches any in the list (including subdomains)."""
        for allowed in domain_list:
            allowed = allowed.lower()
            if domain == allowed or domain.endswith('.' + allowed):
                return True
        return False

    def __eq__(self, other):
        return (
            isinstance(other, URLValidator) and
            self.schemes == other.schemes and
            self.allowed_domains == other.allowed_domains and
            self.blocked_domains == other.blocked_domains and
            self.require_tld == other.require_tld
        )


def validate_url(value, **kwargs):
    """
    Validate a URL value.

    Args:
        value: The URL to validate.
        **kwargs: Additional arguments passed to URLValidator.

    Raises:
        ValidationError: If the URL is invalid.
    """
    validator = URLValidator(**kwargs)
    validator(value)


def is_valid_url(value, **kwargs):
    """
    Check if a URL is valid.

    Args:
        value: The URL to check.
        **kwargs: Additional arguments passed to URLValidator.

    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        validate_url(value, **kwargs)
        return True
    except ValidationError:
        return False


def extract_domain(url):
    """
    Extract the domain from a URL.

    Args:
        url: The URL to extract domain from.

    Returns:
        The domain string, or None if invalid.
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if ':' in domain:
            domain = domain.split(':')[0]
        return domain or None
    except Exception:
        return None
