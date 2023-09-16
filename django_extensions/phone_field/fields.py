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
