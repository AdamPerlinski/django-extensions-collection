"""Tests for humanize template tags."""

import pytest
from datetime import datetime, timedelta
from django.utils import timezone

from .templatetags import (
    intcomma,
    intword,
    ordinal,
    oxford_comma,
    filesizeformat,
    naturaltime,
    pluralize,
    duration,
)


class TestIntcomma:
    """Test cases for intcomma filter."""

    def test_thousands(self):
        """Test thousands formatting."""
        assert intcomma(1000) == '1,000'
        assert intcomma(1000000) == '1,000,000'

    def test_small_numbers(self):
        """Test small numbers."""
        assert intcomma(100) == '100'
        assert intcomma(0) == '0'

    def test_negative(self):
        """Test negative numbers."""
        assert intcomma(-1000) == '-1,000'

    def test_with_decimals(self):
        """Test with decimal places."""
        assert intcomma(1000.5, 2) == '1,000.50'

    def test_invalid(self):
        """Test invalid input."""
        assert intcomma('invalid') == 'invalid'


class TestIntword:
    """Test cases for intword filter."""

    def test_million(self):
        """Test millions."""
        assert intword(1000000) == '1 million'
        assert intword(1500000) == '1.5 million'

    def test_billion(self):
        """Test billions."""
        assert intword(1000000000) == '1 billion'

    def test_thousand(self):
        """Test thousands."""
        assert intword(1000) == '1 thousand'
        assert intword(10000) == '10 thousand'

    def test_small(self):
        """Test small numbers unchanged."""
        assert intword(999) == '999'

    def test_invalid(self):
        """Test invalid input."""
        assert intword('invalid') == 'invalid'


class TestOrdinal:
    """Test cases for ordinal filter."""

    def test_first_few(self):
        """Test first few ordinals."""
        assert ordinal(1) == '1st'
        assert ordinal(2) == '2nd'
        assert ordinal(3) == '3rd'
        assert ordinal(4) == '4th'

    def test_teens(self):
        """Test teen ordinals."""
        assert ordinal(11) == '11th'
        assert ordinal(12) == '12th'
        assert ordinal(13) == '13th'

    def test_twenty_plus(self):
        """Test 20+ ordinals."""
        assert ordinal(21) == '21st'
        assert ordinal(22) == '22nd'
        assert ordinal(23) == '23rd'
        assert ordinal(24) == '24th'

    def test_invalid(self):
        """Test invalid input."""
        assert ordinal('invalid') == 'invalid'


class TestOxfordComma:
    """Test cases for oxford_comma filter."""

    def test_empty(self):
        """Test empty list."""
        assert oxford_comma([]) == ''

    def test_single(self):
        """Test single item."""
        assert oxford_comma(['a']) == 'a'

    def test_two(self):
        """Test two items."""
        assert oxford_comma(['a', 'b']) == 'a and b'

    def test_three(self):
        """Test three items."""
        assert oxford_comma(['a', 'b', 'c']) == 'a, b, and c'

    def test_many(self):
        """Test many items."""
        result = oxford_comma(['a', 'b', 'c', 'd'])
        assert result == 'a, b, c, and d'


class TestFilesizeformat:
    """Test cases for filesizeformat filter."""

    def test_bytes(self):
        """Test bytes."""
        assert filesizeformat(100) == '100 B'

    def test_kilobytes(self):
        """Test kilobytes."""
        assert 'KiB' in filesizeformat(1024)

    def test_megabytes(self):
        """Test megabytes."""
        assert 'MiB' in filesizeformat(1024 * 1024)

    def test_decimal(self):
        """Test decimal (SI) units."""
        result = filesizeformat(1000, binary=False)
        assert 'KB' in result

    def test_invalid(self):
        """Test invalid input."""
        assert filesizeformat('invalid') == 'invalid'


class TestNaturaltime:
    """Test cases for naturaltime filter."""

    def test_just_now(self):
        """Test just now."""
        now = timezone.now()
        assert 'just now' in naturaltime(now)

    def test_minutes_ago(self):
        """Test minutes ago."""
        past = timezone.now() - timedelta(minutes=5)
        result = naturaltime(past)
        assert 'minute' in result
        assert 'ago' in result

    def test_hours_ago(self):
        """Test hours ago."""
        past = timezone.now() - timedelta(hours=2)
        result = naturaltime(past)
        assert 'hour' in result
        assert 'ago' in result

    def test_empty(self):
        """Test empty value."""
        assert naturaltime(None) == ''


class TestPluralize:
    """Test cases for pluralize filter."""

    def test_singular(self):
        """Test singular."""
        assert pluralize(1) == ''
        assert pluralize(1, 'es') == ''

    def test_plural(self):
        """Test plural."""
        assert pluralize(2) == 's'
        assert pluralize(0) == 's'

    def test_custom_suffix(self):
        """Test custom suffix."""
        assert pluralize(1, 'y,ies') == 'y'
        assert pluralize(2, 'y,ies') == 'ies'

    def test_invalid(self):
        """Test invalid input."""
        assert pluralize('invalid') == ''


class TestDuration:
    """Test cases for duration filter."""

    def test_seconds(self):
        """Test seconds only."""
        assert duration(45) == '45 seconds'
        assert duration(1) == '1 second'

    def test_minutes(self):
        """Test minutes and seconds."""
        assert 'minute' in duration(65)

    def test_hours(self):
        """Test hours."""
        assert 'hour' in duration(3600)

    def test_days(self):
        """Test days."""
        assert 'day' in duration(86400)

    def test_complex(self):
        """Test complex duration."""
        result = duration(90061)  # 1 day, 1 hour, 1 minute, 1 second
        assert 'day' in result
        assert 'hour' in result

    def test_zero(self):
        """Test zero."""
        assert duration(0) == '0 seconds'

    def test_invalid(self):
        """Test invalid input."""
        assert duration('invalid') == 'invalid'
