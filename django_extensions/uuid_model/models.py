"""
UUIDModel - Abstract model with UUID as primary key.

Usage:
    from django_extensions.uuid_model import UUIDModel

    class MyModel(UUIDModel):
        name = models.CharField(max_length=100)
"""

import uuid
from django.db import models


class UUIDModel(models.Model):
    """
    An abstract base model that uses UUID as the primary key
    instead of auto-incrementing integers.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this record."
    )

    class Meta:
        abstract = True

    @property
    def short_id(self):
        """Return a shortened version of the UUID (first 8 characters)."""
        return str(self.id)[:8]

    @property
    def hex_id(self):
        """Return the UUID as a 32-character hexadecimal string."""
        return self.id.hex

    @classmethod
    def get_by_short_id(cls, short_id):
        """
        Get an object by its short ID prefix.
        Returns the first match if multiple objects share the prefix.
        """
        return cls.objects.filter(id__startswith=short_id).first()
