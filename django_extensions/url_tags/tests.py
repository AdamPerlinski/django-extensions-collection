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
        assert path('https://example.com/') == '/'


class TestQueryString:
    """Test cases for query_string filter."""

    def test_with_query(self):
        """Test URL with query string."""
        assert query_string('https://example.com?foo=bar') == 'foo=bar'

    def test_no_query(self):
        """Test URL without query string."""
        assert query_string('https://example.com/path') == ''


class TestAddQuery:
    """Test cases for add_query filter."""

    def test_add_to_empty(self):
        """Test adding to URL without query."""
        result = add_query('https://example.com', 'foo=bar')
        assert 'foo=bar' in result

    def test_add_to_existing(self):
        """Test adding to URL with existing query."""
        result = add_query('https://example.com?existing=value', 'new=param')
        assert 'existing=value' in result
        assert 'new=param' in result


class TestRemoveQuery:
    """Test cases for remove_query filter."""

    def test_remove_existing(self):
        """Test removing existing parameter."""
        result = remove_query('https://example.com?foo=bar&baz=qux', 'foo')
        assert 'foo' not in result
        assert 'baz=qux' in result

    def test_remove_nonexistent(self):
        """Test removing non-existent parameter."""
        result = remove_query('https://example.com?foo=bar', 'nonexistent')
        assert 'foo=bar' in result


class TestStripProtocol:
    """Test cases for strip_protocol filter."""

    def test_https(self):
        """Test stripping HTTPS."""
        assert strip_protocol('https://example.com') == 'example.com'

    def test_http(self):
        """Test stripping HTTP."""
        assert strip_protocol('http://example.com') == 'example.com'


class TestEnsureProtocol:
    """Test cases for ensure_protocol filter."""

    def test_add_protocol(self):
        """Test adding protocol."""
        assert ensure_protocol('example.com') == 'https://example.com'

    def test_keep_existing(self):
        """Test keeping existing protocol."""
        assert ensure_protocol('http://example.com') == 'http://example.com'

    def test_custom_protocol(self):
        """Test custom protocol."""
        assert ensure_protocol('example.com', 'http') == 'http://example.com'


class TestExternalLink:
    """Test cases for external_link filter."""

    def test_creates_link(self):
        """Test creating external link."""
        result = external_link('https://example.com')
        assert 'href="https://example.com"' in result
        assert 'target="_blank"' in result
        assert 'rel="noopener noreferrer"' in result
