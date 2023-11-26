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
