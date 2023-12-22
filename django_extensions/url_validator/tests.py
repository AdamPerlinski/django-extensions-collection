"""Tests for URLValidator."""

import pytest
from django.core.exceptions import ValidationError

from .validators import URLValidator, validate_url, is_valid_url, extract_domain


class TestURLValidator:
    """Test cases for URLValidator."""

    def test_valid_http(self):
        """Test valid HTTP URL."""
        validator = URLValidator()
        validator('http://example.com')

    def test_valid_https(self):
        """Test valid HTTPS URL."""
        validator = URLValidator()
        validator('https://example.com')

    def test_valid_with_path(self):
        """Test valid URL with path."""
        validator = URLValidator()
        validator('https://example.com/path/to/page')

    def test_valid_with_query(self):
        """Test valid URL with query string."""
        validator = URLValidator()
        validator('https://example.com?foo=bar')

    def test_invalid_scheme(self):
        """Test invalid scheme."""
        validator = URLValidator(allowed_schemes=['https'])
        with pytest.raises(ValidationError):
            validator('http://example.com')

    def test_allowed_schemes(self):
        """Test allowed schemes restriction."""
        validator = URLValidator(allowed_schemes=['https'])
        validator('https://example.com')  # OK

        with pytest.raises(ValidationError):
            validator('http://example.com')

    def test_allowed_domains(self):
        """Test allowed domains whitelist."""
        validator = URLValidator(allowed_domains=['example.com', 'test.com'])
        validator('https://example.com')
        validator('https://sub.example.com')

        with pytest.raises(ValidationError):
            validator('https://other.com')

    def test_blocked_domains(self):
        """Test blocked domains blacklist."""
        validator = URLValidator(blocked_domains=['blocked.com'])
        validator('https://allowed.com')  # OK

        with pytest.raises(ValidationError):
