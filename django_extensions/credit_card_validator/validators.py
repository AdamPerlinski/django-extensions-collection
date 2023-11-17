"""
CreditCardValidator - Validator for credit card numbers.

Usage:
    from django_extensions.credit_card_validator import CreditCardValidator

    class Payment(models.Model):
        card_number = models.CharField(
            max_length=19,
            validators=[CreditCardValidator()]
        )

    # Or use functions directly
    from django_extensions.credit_card_validator import validate_credit_card, get_card_type
    validate_credit_card('4111111111111111')
    get_card_type('4111111111111111')  # Returns 'visa'
"""

import re
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


# Card type patterns (prefix, length ranges)
CARD_TYPES = {
    'visa': {
        'pattern': r'^4',
        'lengths': [13, 16, 19],
    },
    'mastercard': {
        'pattern': r'^(5[1-5]|222[1-9]|22[3-9]|2[3-6]|27[0-1]|2720)',
        'lengths': [16],
    },
    'amex': {
        'pattern': r'^3[47]',
        'lengths': [15],
    },
    'discover': {
        'pattern': r'^(6011|65|64[4-9]|622)',
        'lengths': [16, 19],
    },
    'diners': {
        'pattern': r'^(36|38|30[0-5])',
        'lengths': [14],
    },
    'jcb': {
        'pattern': r'^35',
        'lengths': [16],
    },
}


def luhn_checksum(card_number):
    """
    Calculate the Luhn checksum for a card number.
    Returns True if valid, False otherwise.
    """
    digits = [int(d) for d in str(card_number)]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]

    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(divmod(d * 2, 10))

    return checksum % 10 == 0


def get_card_type(card_number):
    """
    Determine the card type from the card number.

