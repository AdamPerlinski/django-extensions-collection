"""
ActiveManager - Manager that filters by is_active field.

Usage:
    from django_extensions.active_manager import ActiveManager

    class MyModel(models.Model):
        name = models.CharField(max_length=100)
        is_active = models.BooleanField(default=True)

        objects = ActiveManager()  # Only returns active by default
        all_objects = models.Manager()  # All objects

    MyModel.objects.all()  # Only active
    MyModel.all_objects.all()  # All including inactive
"""

from django.db import models
from django.utils import timezone


class ActiveQuerySet(models.QuerySet):
    """QuerySet with active/inactive filtering."""

    def active(self):
        """Return only active objects."""
        return self.filter(is_active=True)

    def inactive(self):
        """Return only inactive objects."""
