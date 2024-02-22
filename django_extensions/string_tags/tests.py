"""Tests for string template tags."""

import pytest

from .templatetags import (
    truncate_chars,
    truncate_words,
    strip_whitespace,
    replace,
    split,
    join_str,
    upper,
    lower,
    title,
    slugify,
    startswith,
    endswith,
    contains,
    reverse_str,
    repeat,
    remove_html,
    regex_replace,
    pad_left,
    pad_right,
)


class TestTruncateChars:
    """Test cases for truncate_chars filter."""

    def test_short_string(self):
        """Test string shorter than limit."""
        assert truncate_chars('hello', 10) == 'hello'

    def test_long_string(self):
        """Test string longer than limit."""
        assert truncate_chars('hello world', 8) == 'hello...'

    def test_exact_length(self):
        """Test string exactly at limit."""
        assert truncate_chars('hello', 5) == 'hello'


class TestTruncateWords:
    """Test cases for truncate_words filter."""

    def test_short_text(self):
        """Test text with fewer words."""
        assert truncate_words('hello world', 5) == 'hello world'

    def test_long_text(self):
        """Test text with more words."""
        result = truncate_words('one two three four five', 3)
        assert result == 'one two three...'


class TestStripWhitespace:
    """Test cases for strip filter."""

    def test_leading(self):
        """Test stripping leading whitespace."""
        assert strip_whitespace('  hello') == 'hello'

    def test_trailing(self):
        """Test stripping trailing whitespace."""
        assert strip_whitespace('hello  ') == 'hello'

    def test_both(self):
        """Test stripping both."""
        assert strip_whitespace('  hello  ') == 'hello'


class TestReplace:
    """Test cases for replace filter."""

    def test_basic(self):
        """Test basic replacement."""
        assert replace('hello world', 'world,universe') == 'hello universe'

    def test_multiple(self):
        """Test multiple occurrences."""
        assert replace('a a a', 'a,b') == 'b b b'


class TestSplit:
