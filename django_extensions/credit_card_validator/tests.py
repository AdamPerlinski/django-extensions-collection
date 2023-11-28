"""Tests for CreditCardValidator."""

import pytest
from django.core.exceptions import ValidationError

from .validators import (
    CreditCardValidator,
    validate_credit_card,
    get_card_type,
    is_valid_credit_card,
    mask_card_number,
    luhn_checksum,
)


class TestLuhnChecksum:
    """Test cases for Luhn checksum."""

    def test_valid_checksum(self):
        """Test valid Luhn checksum."""
        assert luhn_checksum('4111111111111111') is True  # Visa test number
        assert luhn_checksum('5500000000000004') is True  # Mastercard test

    def test_invalid_checksum(self):
        """Test invalid Luhn checksum."""
        assert luhn_checksum('4111111111111112') is False
        assert luhn_checksum('1234567890123456') is False


class TestGetCardType:
    """Test cases for get_card_type function."""

    def test_visa(self):
        """Test Visa detection."""
        assert get_card_type('4111111111111111') == 'visa'
        assert get_card_type('4012888888881881') == 'visa'

    def test_mastercard(self):
        """Test Mastercard detection."""
        assert get_card_type('5500000000000004') == 'mastercard'
        assert get_card_type('5105105105105100') == 'mastercard'

    def test_amex(self):
        """Test American Express detection."""
        assert get_card_type('378282246310005') == 'amex'
        assert get_card_type('371449635398431') == 'amex'

    def test_discover(self):
        """Test Discover detection."""
        assert get_card_type('6011111111111117') == 'discover'
        assert get_card_type('6011000990139424') == 'discover'

    def test_unknown(self):
        """Test unknown card type."""
        assert get_card_type('9999999999999999') is None

    def test_with_formatting(self):
        """Test with formatted number."""
        assert get_card_type('4111-1111-1111-1111') == 'visa'


class TestCreditCardValidator:
    """Test cases for CreditCardValidator."""

    def test_valid_visa(self):
        """Test valid Visa number."""
        validator = CreditCardValidator()
        validator('4111111111111111')  # Should not raise

    def test_valid_mastercard(self):
        """Test valid Mastercard number."""
        validator = CreditCardValidator()
        validator('5500000000000004')

    def test_valid_amex(self):
        """Test valid Amex number."""
        validator = CreditCardValidator()
        validator('378282246310005')

    def test_valid_with_spaces(self):
        """Test valid number with spaces."""
        validator = CreditCardValidator()
        validator('4111 1111 1111 1111')

    def test_valid_with_dashes(self):
        """Test valid number with dashes."""
        validator = CreditCardValidator()
        validator('4111-1111-1111-1111')

    def test_invalid_luhn(self):
        """Test invalid Luhn checksum."""
        validator = CreditCardValidator()
        with pytest.raises(ValidationError):
            validator('4111111111111112')

    def test_too_short(self):
        """Test too short number."""
        validator = CreditCardValidator()
        with pytest.raises(ValidationError):
            validator('411111111111')

    def test_too_long(self):
        """Test too long number."""
        validator = CreditCardValidator()
        with pytest.raises(ValidationError):
            validator('41111111111111111111')

    def test_empty_allowed(self):
        """Test empty value is allowed."""
        validator = CreditCardValidator()
        validator('')
        validator(None)

    def test_accepted_types(self):
        """Test accepted card types restriction."""
        validator = CreditCardValidator(accepted_types=['visa', 'mastercard'])
        validator('4111111111111111')  # Visa - ok
        validator('5500000000000004')  # Mastercard - ok

        with pytest.raises(ValidationError):
            validator('378282246310005')  # Amex - not accepted

    def test_custom_message(self):
        """Test custom error message."""
        validator = CreditCardValidator(message='Bad card!')
        with pytest.raises(ValidationError) as exc_info:
            validator('1234567890123456')
        assert 'Bad card!' in str(exc_info.value)

    def test_equality(self):
        """Test validator equality."""
        v1 = CreditCardValidator(accepted_types=['visa'])
        v2 = CreditCardValidator(accepted_types=['visa'])
        v3 = CreditCardValidator(accepted_types=['mastercard'])

        assert v1 == v2
        assert v1 != v3


class TestValidateCreditCard:
    """Test cases for validate_credit_card function."""

    def test_valid(self):
        """Test valid card."""
        validate_credit_card('4111111111111111')

    def test_invalid(self):
        """Test invalid card."""
        with pytest.raises(ValidationError):
            validate_credit_card('1234')

    def test_with_accepted_types(self):
        """Test with accepted types."""
        validate_credit_card('4111111111111111', accepted_types=['visa'])


class TestIsValidCreditCard:
    """Test cases for is_valid_credit_card function."""

    def test_valid(self):
        """Test valid card returns True."""
        assert is_valid_credit_card('4111111111111111') is True

    def test_invalid(self):
        """Test invalid card returns False."""
        assert is_valid_credit_card('1234') is False


class TestMaskCardNumber:
    """Test cases for mask_card_number function."""

    def test_mask_default(self):
        """Test default masking (last 4 visible)."""
        result = mask_card_number('4111111111111111')
        assert result == '************1111'

    def test_mask_custom_visible(self):
        """Test custom visible digits."""
        result = mask_card_number('4111111111111111', visible_digits=6)
        assert result == '**********111111'

    def test_mask_with_formatting(self):
        """Test masking removes formatting."""
        result = mask_card_number('4111-1111-1111-1111')
        assert result == '************1111'

    def test_mask_short_number(self):
        """Test masking very short number."""
        result = mask_card_number('1234', visible_digits=4)
        assert result == '1234'
