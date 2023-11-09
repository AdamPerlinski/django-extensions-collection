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

