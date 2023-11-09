"""
PhoneNumberValidator - Validator for phone numbers.

Usage:
    from django_extensions.phone_validator import PhoneNumberValidator

    class Contact(models.Model):
        phone = models.CharField(
            max_length=20,
            validators=[PhoneNumberValidator()]
        )

    # Or use the function directly
    from django_extensions.phone_validator import validate_phone_number
    validate_phone_number('+15551234567')
"""

import re
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class PhoneNumberValidator:
    """
    Validator for phone numbers.
    Supports various formats and validates based on region.
    """

    # Common phone patterns
    PATTERNS = {
        'US': [
            r'^\+?1?\s*\(?(\d{3})\)?[-.\s]*(\d{3})[-.\s]*(\d{4})$',
        ],
        'UK': [
            r'^\+?44?\s*\(?0?\)?(\d{2,5})\)?[-.\s]*(\d{3,4})[-.\s]*(\d{3,4})$',
        ],
        'INTERNATIONAL': [
            r'^\+(\d{1,3})[-.\s]?(\d{1,4})[-.\s]?(\d{1,4})[-.\s]?(\d{1,4})[-.\s]?(\d{0,4})$',
            r'^(\d{7,15})$',
        ],
    }

    message = "Enter a valid phone number."
    code = 'invalid_phone'

    def __init__(self, region='US', message=None, code=None):
        self.region = region
        if message:
            self.message = message
        if code:
            self.code = code

    def __call__(self, value):
        if not value:
            return

        # Clean the value
        cleaned = str(value).strip()

        # Get patterns for region
        patterns = self.PATTERNS.get(self.region, [])
        patterns.extend(self.PATTERNS.get('INTERNATIONAL', []))

        # Check against patterns
        for pattern in patterns:
            if re.match(pattern, cleaned):
                return

        # Check digit count as fallback, but only if no letters present
        if not re.search(r'[a-zA-Z]', cleaned):
            digits = re.sub(r'\D', '', cleaned)
            if 7 <= len(digits) <= 15:
                return

        raise ValidationError(self.message, code=self.code)

    def __eq__(self, other):
        return (
            isinstance(other, PhoneNumberValidator) and
            self.region == other.region and
            self.message == other.message and
            self.code == other.code
        )


def validate_phone_number(value, region='US'):
    """
    Validate a phone number value.

    Args:
        value: The phone number to validate.
        region: The region for validation rules (default 'US').

    Raises:
        ValidationError: If the phone number is invalid.
    """
    validator = PhoneNumberValidator(region=region)
    validator(value)


def is_valid_phone(value, region='US'):
    """
    Check if a phone number is valid.

    Args:
        value: The phone number to check.
        region: The region for validation rules.

    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        validate_phone_number(value, region)
        return True
    except ValidationError:
        return False
