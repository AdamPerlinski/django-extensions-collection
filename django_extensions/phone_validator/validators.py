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
