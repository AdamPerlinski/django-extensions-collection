"""Tests for URL template tags."""

import pytest

from .templatetags import (
    domain,
    scheme,
    path,
    query_string,
    add_query,
    remove_query,
    strip_protocol,
    ensure_protocol,
    external_link,
)


class TestDomain:
    """Test cases for domain filter."""

    def test_basic(self):
        """Test basic domain extraction."""
        assert domain('https://example.com/path') == 'example.com'

    def test_with_port(self):
        """Test domain with port."""
        assert domain('https://example.com:8080/path') == 'example.com:8080'

    def test_subdomain(self):
        """Test with subdomain."""
        assert domain('https://www.example.com/path') == 'www.example.com'


class TestScheme:
    """Test cases for scheme filter."""

    def test_https(self):
        """Test HTTPS scheme."""
        assert scheme('https://example.com') == 'https'

    def test_http(self):
        """Test HTTP scheme."""
        assert scheme('http://example.com') == 'http'


class TestPath:
    """Test cases for path filter."""

    def test_with_path(self):
        """Test URL with path."""
        assert path('https://example.com/path/to/page') == '/path/to/page'

    def test_root(self):
        """Test URL with root path."""
