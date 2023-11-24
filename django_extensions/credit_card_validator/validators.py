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

    Args:
        card_number: The credit card number (string or int).

    Returns:
        The card type as a string, or None if unknown.
    """
    # Clean the number
    cleaned = re.sub(r'\D', '', str(card_number))

    for card_type, info in CARD_TYPES.items():
        if re.match(info['pattern'], cleaned):
            return card_type

    return None


@deconstructible
class CreditCardValidator:
    """
    Validator for credit card numbers.
    Validates format, length, and Luhn checksum.
    """

    message = "Enter a valid credit card number."
    code = 'invalid_card'

    def __init__(self, accepted_types=None, message=None, code=None):
        """
        Initialize the validator.

        Args:
            accepted_types: List of accepted card types. If None, all types accepted.
            message: Custom error message.
            code: Custom error code.
        """
        self.accepted_types = accepted_types
        if message:
            self.message = message
        if code:
            self.code = code

    def __call__(self, value):
        if not value:
            return

        # Clean the number
        cleaned = re.sub(r'\D', '', str(value))

        # Check minimum length
        if len(cleaned) < 13:
            raise ValidationError(
                "Credit card number must be at least 13 digits.",
                code=self.code
            )

        # Check maximum length
        if len(cleaned) > 19:
            raise ValidationError(
                "Credit card number must be at most 19 digits.",
                code=self.code
            )

        # Validate Luhn checksum
        if not luhn_checksum(cleaned):
            raise ValidationError(self.message, code=self.code)

        # Check card type if restricted
        if self.accepted_types:
            card_type = get_card_type(cleaned)
            if card_type not in self.accepted_types:
                accepted = ', '.join(self.accepted_types)
                raise ValidationError(
                    f"Card type not accepted. Accepted types: {accepted}",
                    code='card_type_not_accepted'
                )

    def __eq__(self, other):
        return (
            isinstance(other, CreditCardValidator) and
            self.accepted_types == other.accepted_types and
            self.message == other.message and
            self.code == other.code
        )


def validate_credit_card(value, accepted_types=None):
    """
    Validate a credit card number.

    Args:
        value: The credit card number to validate.
        accepted_types: Optional list of accepted card types.

    Raises:
        ValidationError: If the card number is invalid.
    """
    validator = CreditCardValidator(accepted_types=accepted_types)
    validator(value)


def is_valid_credit_card(value):
    """
    Check if a credit card number is valid.

    Args:
        value: The credit card number to check.

    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        validate_credit_card(value)
        return True
    except ValidationError:
        return False


def mask_card_number(card_number, visible_digits=4):
    """
    Mask a credit card number, showing only the last few digits.

    Args:
        card_number: The card number to mask.
        visible_digits: Number of digits to keep visible at the end.

    Returns:
        Masked card number string.
    """
    cleaned = re.sub(r'\D', '', str(card_number))
    if len(cleaned) <= visible_digits:
        return cleaned

    masked_length = len(cleaned) - visible_digits
    return '*' * masked_length + cleaned[-visible_digits:]
