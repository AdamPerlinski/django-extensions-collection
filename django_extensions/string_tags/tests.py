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
    """Test cases for split filter."""

    def test_default(self):
        """Test default space split."""
        assert split('a b c') == ['a', 'b', 'c']

    def test_custom(self):
        """Test custom separator."""
        assert split('a,b,c', ',') == ['a', 'b', 'c']


class TestJoinStr:
    """Test cases for join_str filter."""

    def test_basic(self):
        """Test basic join."""
        assert join_str(['a', 'b', 'c'], ', ') == 'a, b, c'

    def test_custom_separator(self):
        """Test custom separator."""
        assert join_str(['a', 'b', 'c'], '-') == 'a-b-c'


class TestCaseFilters:
    """Test cases for case filters."""

    def test_upper(self):
        """Test upper."""
        assert upper('hello') == 'HELLO'

    def test_lower(self):
        """Test lower."""
        assert lower('HELLO') == 'hello'

    def test_title(self):
        """Test title."""
        assert title('hello world') == 'Hello World'


class TestSlugify:
    """Test cases for slugify filter."""

    def test_basic(self):
        """Test basic slugify."""
        assert slugify('Hello World') == 'hello-world'

    def test_special_chars(self):
        """Test special characters."""
        assert slugify('Hello, World!') == 'hello-world'


class TestStringChecks:
    """Test cases for string check filters."""

    def test_startswith(self):
        """Test startswith."""
        assert startswith('hello world', 'hello') is True
        assert startswith('hello world', 'world') is False

    def test_endswith(self):
        """Test endswith."""
        assert endswith('hello world', 'world') is True
        assert endswith('hello world', 'hello') is False

    def test_contains(self):
        """Test contains."""
        assert contains('hello world', 'lo wo') is True
        assert contains('hello world', 'xyz') is False


class TestReverseStr:
    """Test cases for reverse_str filter."""

    def test_basic(self):
        """Test basic reverse."""
        assert reverse_str('hello') == 'olleh'

    def test_palindrome(self):
        """Test palindrome."""
        assert reverse_str('radar') == 'radar'


class TestRepeat:
    """Test cases for repeat filter."""

    def test_basic(self):
        """Test basic repeat."""
        assert repeat('ab', 3) == 'ababab'

    def test_once(self):
        """Test repeat once."""
        assert repeat('hello', 1) == 'hello'


class TestRemoveHtml:
    """Test cases for remove_html filter."""

    def test_basic(self):
        """Test basic HTML removal."""
        assert remove_html('<p>Hello</p>') == 'Hello'

    def test_nested(self):
        """Test nested HTML."""
        assert remove_html('<div><b>Bold</b></div>') == 'Bold'


class TestRegexReplace:
    """Test cases for regex_replace filter."""

    def test_digits(self):
        """Test replacing digits."""
        assert regex_replace('abc123def', '\\d+,XXX') == 'abcXXXdef'

    def test_pattern(self):
        """Test complex pattern."""
        result = regex_replace('2023-01-15', '(\\d{4})-(\\d{2})-(\\d{2}),\\2/\\3/\\1')
        assert result == '01/15/2023'


class TestPadding:
    """Test cases for padding filters."""

    def test_pad_left(self):
        """Test left padding."""
        assert pad_left('42', '5,0') == '00042'

    def test_pad_right(self):
        """Test right padding."""
        assert pad_right('hi', '5,.') == 'hi...'
