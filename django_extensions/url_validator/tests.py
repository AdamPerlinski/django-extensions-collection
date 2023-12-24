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
            validator('https://blocked.com')

        with pytest.raises(ValidationError):
            validator('https://sub.blocked.com')

    def test_require_tld(self):
        """Test TLD requirement."""
        validator = URLValidator(require_tld=True)
        with pytest.raises(ValidationError):
            validator('http://localhost')

    def test_no_require_tld(self):
        """Test without TLD requirement."""
        validator = URLValidator(require_tld=False)
        validator('http://localhost')  # OK

    def test_empty_allowed(self):
        """Test empty value is allowed."""
        validator = URLValidator()
        validator('')
        validator(None)

    def test_subdomain_matching(self):
        """Test subdomain matching for allowed domains."""
        validator = URLValidator(allowed_domains=['example.com'])
        validator('https://www.example.com')
        validator('https://sub.example.com')
        validator('https://deep.sub.example.com')

    def test_equality(self):
        """Test validator equality."""
        v1 = URLValidator(allowed_schemes=['https'])
        v2 = URLValidator(allowed_schemes=['https'])
        v3 = URLValidator(allowed_schemes=['http'])

        assert v1 == v2
        assert v1 != v3


class TestValidateUrl:
    """Test cases for validate_url function."""

    def test_valid(self):
        """Test valid URL."""
        validate_url('https://example.com')

    def test_invalid(self):
        """Test invalid URL."""
        with pytest.raises(ValidationError):
            validate_url('not-a-url')


class TestIsValidUrl:
    """Test cases for is_valid_url function."""

    def test_valid(self):
        """Test valid URL returns True."""
        assert is_valid_url('https://example.com') is True

    def test_invalid(self):
        """Test invalid URL returns False."""
        assert is_valid_url('not-a-url') is False

    def test_with_options(self):
        """Test with additional options."""
        assert is_valid_url('http://example.com', allowed_schemes=['https']) is False
        assert is_valid_url('https://example.com', allowed_schemes=['https']) is True


class TestExtractDomain:
    """Test cases for extract_domain function."""

    def test_simple_url(self):
        """Test simple URL."""
        assert extract_domain('https://example.com') == 'example.com'

    def test_with_path(self):
        """Test URL with path."""
        assert extract_domain('https://example.com/path') == 'example.com'

    def test_with_port(self):
        """Test URL with port."""
        assert extract_domain('https://example.com:8080') == 'example.com'

    def test_with_subdomain(self):
        """Test URL with subdomain."""
        assert extract_domain('https://www.example.com') == 'www.example.com'

    def test_invalid(self):
        """Test invalid URL returns None."""
        assert extract_domain('not-a-url') is None
        assert extract_domain('') is None
