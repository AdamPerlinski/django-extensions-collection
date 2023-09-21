"""
PhoneNumberField - CharField with phone number validation.

Usage:
    from django_extensions.phone_field import PhoneNumberField

    class Contact(models.Model):
        phone = PhoneNumberField()
"""

import re
from django.core.exceptions import ValidationError
from django.db import models


class PhoneNumberField(models.CharField):
    """
    A CharField that validates and normalizes phone numbers.
    Accepts various formats and stores in E.164-like format.
    """

    # Patterns for common phone formats
    PHONE_PATTERNS = [
        r'^\+?1?\s*\(?(\d{3})\)?[-.\s]*(\d{3})[-.\s]*(\d{4})$',  # US format
        r'^\+?(\d{1,3})[-.\s]?(\d{2,4})[-.\s]?(\d{3,4})[-.\s]?(\d{3,4})$',  # International
        r'^(\d{10,15})$',  # Plain digits
    ]

    def __init__(self, *args, region='US', **kwargs):
        self.region = region
        kwargs.setdefault('max_length', 20)
        super().__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        """Clean and validate the phone number."""
        value = super().clean(value, model_instance)
        if value:
            value = self.normalize_phone(value)
            self.validate_phone(value)
        return value

    def normalize_phone(self, value):
        """Normalize phone number to a standard format."""
        if not value:
            return value

        # Remove all non-digit characters except leading +
        has_plus = value.startswith('+')
        digits = re.sub(r'\D', '', value)

        # Handle US numbers
        if self.region == 'US':
            if len(digits) == 10:
                return f'+1{digits}'
            elif len(digits) == 11 and digits.startswith('1'):
                return f'+{digits}'

        # Return with + prefix if originally had one
        if has_plus:
            return f'+{digits}'

        return digits

    def validate_phone(self, value):
        """Validate the phone number."""
        if not value:
            return

        # Check for valid patterns
        for pattern in self.PHONE_PATTERNS:
            if re.match(pattern, value):
                return

        # Check digit count
        digits = re.sub(r'\D', '', value)
        if len(digits) < 7 or len(digits) > 15:
            raise ValidationError(
                f"Phone number must be between 7 and 15 digits. Got {len(digits)}."
            )

    def formfield(self, **kwargs):
        """Return form field with phone validation."""
        from django import forms

        class PhoneFormField(forms.CharField):
            def clean(self, value):
                value = super().clean(value)
                if value:
                    # Basic validation
                    digits = re.sub(r'\D', '', value)
                    if len(digits) < 7 or len(digits) > 15:
                        raise ValidationError("Invalid phone number")
                return value

        defaults = {'form_class': PhoneFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def deconstruct(self):
        """Return deconstructed field for migrations."""
        name, path, args, kwargs = super().deconstruct()
        if self.region != 'US':
            kwargs['region'] = self.region
        return name, path, args, kwargs


def format_phone(number, format_type='national'):
    """
    Format a phone number for display.

    Args:
        number: Phone number string
        format_type: 'national', 'international', or 'e164'
    """
    if not number:
        return number

    digits = re.sub(r'\D', '', number)

    if format_type == 'e164':
        if not number.startswith('+'):
            return f'+{digits}'
        return f'+{digits}'

    # US formatting
    if len(digits) == 10:
        if format_type == 'national':
            return f'({digits[:3]}) {digits[3:6]}-{digits[6:]}'
        else:
            return f'+1 ({digits[:3]}) {digits[3:6]}-{digits[6:]}'

    if len(digits) == 11 and digits.startswith('1'):
        if format_type == 'national':
            return f'({digits[1:4]}) {digits[4:7]}-{digits[7:]}'
        else:
            return f'+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}'

    return number
