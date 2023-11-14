"""Tests for PhoneNumberValidator."""

import pytest
from django.core.exceptions import ValidationError

from .validators import PhoneNumberValidator, validate_phone_number, is_valid_phone


class TestPhoneNumberValidator:
    """Test cases for PhoneNumberValidator."""

    def test_valid_us_10_digit(self):
        """Test valid 10-digit US number."""
        validator = PhoneNumberValidator(region='US')
        validator('5551234567')  # Should not raise

    def test_valid_us_with_country_code(self):
        """Test valid US number with country code."""
        validator = PhoneNumberValidator(region='US')
        validator('+15551234567')

    def test_valid_us_formatted(self):
        """Test valid formatted US number."""
        validator = PhoneNumberValidator(region='US')
        validator('(555) 123-4567')

    def test_valid_us_dots(self):
        """Test valid US number with dots."""
        validator = PhoneNumberValidator(region='US')
        validator('555.123.4567')

    def test_invalid_too_short(self):
        """Test invalid too short number."""
        validator = PhoneNumberValidator(region='US')
        with pytest.raises(ValidationError):
            validator('12345')

    def test_invalid_too_long(self):
        """Test invalid too long number."""
        validator = PhoneNumberValidator(region='US')
        with pytest.raises(ValidationError):
            validator('1234567890123456')

    def test_invalid_letters(self):
        """Test invalid number with letters."""
        validator = PhoneNumberValidator(region='US')
        with pytest.raises(ValidationError):
            validator('555-ABC-1234')

    def test_empty_allowed(self):
        """Test empty value is allowed."""
        validator = PhoneNumberValidator(region='US')
        validator('')  # Should not raise
        validator(None)  # Should not raise

    def test_international_format(self):
        """Test international format."""
        validator = PhoneNumberValidator(region='INTERNATIONAL')
        validator('+44 20 7946 0958')

    def test_custom_message(self):
        """Test custom error message."""
        validator = PhoneNumberValidator(message='Bad phone!')
        with pytest.raises(ValidationError) as exc_info:
            validator('123')
        assert 'Bad phone!' in str(exc_info.value)

    def test_custom_code(self):
        """Test custom error code."""
        validator = PhoneNumberValidator(code='bad_phone')
        with pytest.raises(ValidationError) as exc_info:
            validator('123')
        assert exc_info.value.code == 'bad_phone'

    def test_equality(self):
        """Test validator equality."""
        v1 = PhoneNumberValidator(region='US')
        v2 = PhoneNumberValidator(region='US')
        v3 = PhoneNumberValidator(region='UK')

        assert v1 == v2
        assert v1 != v3

    def test_deconstructible(self):
        """Test validator is deconstructible for migrations."""
        validator = PhoneNumberValidator(region='UK')
        path, args, kwargs = validator.deconstruct()

        assert 'PhoneNumberValidator' in path
        assert kwargs.get('region') == 'UK'


class TestValidatePhoneNumber:
    """Test cases for validate_phone_number function."""

    def test_valid_number(self):
        """Test valid number doesn't raise."""
        validate_phone_number('5551234567')  # Should not raise

    def test_invalid_number(self):
        """Test invalid number raises."""
        with pytest.raises(ValidationError):
            validate_phone_number('123')

    def test_with_region(self):
        """Test with specific region."""
        validate_phone_number('+44 20 7946 0958', region='UK')


class TestIsValidPhone:
    """Test cases for is_valid_phone function."""

    def test_valid_returns_true(self):
        """Test valid number returns True."""
        assert is_valid_phone('5551234567') is True

    def test_invalid_returns_false(self):
        """Test invalid number returns False."""
        assert is_valid_phone('123') is False

    def test_with_region(self):
        """Test with specific region."""
        assert is_valid_phone('+44 20 7946 0958', region='UK') is True
