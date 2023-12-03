"""Tests for ColorValidator."""

import pytest
from django.core.exceptions import ValidationError

from .validators import (
    ColorValidator,
    validate_color,
    get_color_format,
    normalize_color,
    is_valid_color,
)


class TestGetColorFormat:
    """Test cases for get_color_format function."""

    def test_hex3(self):
        """Test 3-digit hex format."""
        assert get_color_format('#FFF') == 'hex3'
        assert get_color_format('#abc') == 'hex3'

    def test_hex6(self):
        """Test 6-digit hex format."""
        assert get_color_format('#FFFFFF') == 'hex6'
        assert get_color_format('#abcdef') == 'hex6'

    def test_hex8(self):
        """Test 8-digit hex format (with alpha)."""
        assert get_color_format('#FFFFFFFF') == 'hex8'

    def test_rgb(self):
        """Test rgb format."""
        assert get_color_format('rgb(255, 255, 255)') == 'rgb'
        assert get_color_format('rgb(0,0,0)') == 'rgb'

    def test_rgba(self):
        """Test rgba format."""
        assert get_color_format('rgba(255, 255, 255, 0.5)') == 'rgba'
        assert get_color_format('rgba(0,0,0,1)') == 'rgba'

    def test_hsl(self):
        """Test hsl format."""
        assert get_color_format('hsl(360, 100%, 50%)') == 'hsl'

    def test_hsla(self):
        """Test hsla format."""
        assert get_color_format('hsla(360, 100%, 50%, 0.5)') == 'hsla'

    def test_named(self):
        """Test named colors."""
        assert get_color_format('red') == 'named'
        assert get_color_format('blue') == 'named'

    def test_invalid(self):
        """Test invalid formats."""
        assert get_color_format('invalid') is None
        assert get_color_format('#GGG') is None
        assert get_color_format('') is None


class TestNormalizeColor:
    """Test cases for normalize_color function."""

    def test_hex6(self):
        """Test hex6 normalization."""
        assert normalize_color('#FFFFFF') == '#ffffff'

    def test_hex3_to_hex6(self):
        """Test hex3 expansion to hex6."""
        assert normalize_color('#FFF') == '#ffffff'
        assert normalize_color('#abc') == '#aabbcc'

    def test_rgb_to_hex(self):
        """Test rgb to hex conversion."""
        assert normalize_color('rgb(255, 255, 255)') == '#ffffff'
        assert normalize_color('rgb(0, 0, 0)') == '#000000'
        assert normalize_color('rgb(255, 128, 0)') == '#ff8000'

    def test_invalid(self):
