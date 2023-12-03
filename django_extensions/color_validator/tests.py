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
        """Test invalid color returns None."""
        assert normalize_color('invalid') is None
        assert normalize_color('') is None


class TestColorValidator:
    """Test cases for ColorValidator."""

    def test_valid_hex3(self):
        """Test valid 3-digit hex."""
        validator = ColorValidator()
        validator('#FFF')

    def test_valid_hex6(self):
        """Test valid 6-digit hex."""
        validator = ColorValidator()
        validator('#FFFFFF')

    def test_valid_rgb(self):
        """Test valid rgb."""
        validator = ColorValidator()
        validator('rgb(255, 255, 255)')

    def test_valid_rgba(self):
        """Test valid rgba."""
        validator = ColorValidator()
        validator('rgba(255, 255, 255, 0.5)')

    def test_valid_hsl(self):
        """Test valid hsl."""
        validator = ColorValidator()
        validator('hsl(360, 100%, 50%)')

    def test_valid_hsla(self):
        """Test valid hsla."""
        validator = ColorValidator()
        validator('hsla(360, 100%, 50%, 0.5)')

    def test_valid_named(self):
        """Test valid named color."""
        validator = ColorValidator()
        validator('red')
        validator('blue')

    def test_invalid_format(self):
        """Test invalid format."""
        validator = ColorValidator()
        with pytest.raises(ValidationError):
            validator('invalid')

    def test_invalid_hex(self):
        """Test invalid hex."""
        validator = ColorValidator()
        with pytest.raises(ValidationError):
            validator('#GGG')

    def test_rgb_out_of_range(self):
        """Test rgb values out of range."""
        validator = ColorValidator()
        with pytest.raises(ValidationError):
            validator('rgb(256, 0, 0)')

    def test_hsl_hue_out_of_range(self):
        """Test hsl hue out of range."""
        validator = ColorValidator()
        with pytest.raises(ValidationError):
            validator('hsl(400, 50%, 50%)')

    def test_empty_allowed(self):
        """Test empty value is allowed."""
        validator = ColorValidator()
        validator('')
        validator(None)

    def test_disallow_named(self):
        """Test disallowing named colors."""
        validator = ColorValidator(allow_named=False)
        with pytest.raises(ValidationError):
            validator('red')

    def test_restrict_formats(self):
        """Test restricting formats."""
        validator = ColorValidator(formats=['hex6'])
        validator('#FFFFFF')  # OK

        with pytest.raises(ValidationError):
            validator('#FFF')  # hex3 not allowed

    def test_equality(self):
        """Test validator equality."""
        v1 = ColorValidator(formats=['hex6'])
        v2 = ColorValidator(formats=['hex6'])
        v3 = ColorValidator(formats=['rgb'])

        assert v1 == v2
        assert v1 != v3


class TestValidateColor:
    """Test cases for validate_color function."""

    def test_valid(self):
        """Test valid color."""
        validate_color('#FFFFFF')

    def test_invalid(self):
        """Test invalid color."""
        with pytest.raises(ValidationError):
            validate_color('invalid')


class TestIsValidColor:
    """Test cases for is_valid_color function."""

    def test_valid(self):
        """Test valid color returns True."""
        assert is_valid_color('#FFFFFF') is True
        assert is_valid_color('rgb(255, 0, 0)') is True

    def test_invalid(self):
        """Test invalid color returns False."""
        assert is_valid_color('invalid') is False
