"""
TimeStampedModel - Abstract model with automatic created and modified timestamps.

Usage:
    from django_extensions.timestamped_model import TimeStampedModel

    class MyModel(TimeStampedModel):
        name = models.CharField(max_length=100)
"""

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    An abstract base model that provides self-updating
    'created' and 'modified' fields.
    """
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when this record was created."
    )
    modified = models.DateTimeField(
        auto_now=True,
        db_index=True,
        help_text="Timestamp when this record was last modified."
    )

    class Meta:
        abstract = True
        ordering = ['-created']
        get_latest_by = 'created'

    def save(self, *args, **kwargs):
        """Override save to handle update_fields properly."""
        update_fields = kwargs.get('update_fields')
        if update_fields is not None:
            kwargs['update_fields'] = set(update_fields) | {'modified'}
        super().save(*args, **kwargs)

    @property
    def was_modified(self):
        """Check if the model was modified after creation."""
        if self.created and self.modified:
            return self.modified > self.created
        return False
