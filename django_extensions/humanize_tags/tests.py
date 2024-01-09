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
