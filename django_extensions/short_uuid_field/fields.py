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
