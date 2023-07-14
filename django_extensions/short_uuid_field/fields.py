"""
ShortUUIDField - CharField that generates short unique IDs.

Usage:
    from django_extensions.short_uuid_field import ShortUUIDField

    class MyModel(models.Model):
        short_id = ShortUUIDField()
        name = models.CharField(max_length=100)
"""

import uuid
import string
from django.db import models


class ShortUUIDField(models.CharField):
    """
    A CharField that automatically generates a short unique identifier.
    Uses base62 encoding (alphanumeric) for shorter, URL-friendly IDs.
    """

    ALPHABET = string.ascii_letters + string.digits  # a-zA-Z0-9

    def __init__(self, *args, length=8, **kwargs):
        self.short_length = length
        kwargs.setdefault('max_length', length)
        kwargs.setdefault('unique', True)
        kwargs.setdefault('editable', False)
        kwargs.setdefault('db_index', True)
        super().__init__(*args, **kwargs)

    def generate_short_uuid(self):
        """Generate a short UUID using base62 encoding."""
        # Use UUID4 as source of randomness
        uuid_int = uuid.uuid4().int

        result = []
        base = len(self.ALPHABET)

        while uuid_int and len(result) < self.short_length:
            uuid_int, remainder = divmod(uuid_int, base)
            result.append(self.ALPHABET[remainder])

        # Pad if necessary
        while len(result) < self.short_length:
            result.append(self.ALPHABET[0])

        return ''.join(result)

    def pre_save(self, model_instance, add):
        """Generate value if not set."""
        value = getattr(model_instance, self.attname)
        if not value:
            value = self.generate_short_uuid()
            setattr(model_instance, self.attname, value)
        return value

    def deconstruct(self):
        """Return deconstructed field for migrations."""
        name, path, args, kwargs = super().deconstruct()
        if self.short_length != 8:
            kwargs['length'] = self.short_length
        if kwargs.get('unique') is True:
            del kwargs['unique']
        if kwargs.get('editable') is False:
            del kwargs['editable']
        if kwargs.get('db_index') is True:
            del kwargs['db_index']
        if kwargs.get('max_length') == self.short_length:
            del kwargs['max_length']
        return name, path, args, kwargs


def generate_short_uuid(length=8):
    """Utility function to generate a short UUID."""
    field = ShortUUIDField(length=length)
    return field.generate_short_uuid()
