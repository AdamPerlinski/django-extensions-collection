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
        return self.filter(is_active=False)

    def activate(self):
        """Activate all objects in queryset."""
        return self.update(is_active=True)

    def deactivate(self):
        """Deactivate all objects in queryset."""
        return self.update(is_active=False)

    def toggle(self):
        """Toggle active status of all objects."""
        from django.db.models import Case, When, Value
        return self.update(
            is_active=Case(
                When(is_active=True, then=Value(False)),
                When(is_active=False, then=Value(True)),
            )
        )


class ActiveManager(models.Manager):
    """
    Manager that returns only active objects by default.
    Expects the model to have an 'is_active' boolean field.
    """

    def __init__(self, *args, active_field='is_active', filter_active=True, **kwargs):
        self.active_field = active_field
        self.filter_active = filter_active
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        qs = ActiveQuerySet(self.model, using=self._db)
        if self.filter_active:
            return qs.filter(**{self.active_field: True})
        return qs

    def active(self):
        """Return active objects."""
        return self.get_queryset().filter(**{self.active_field: True})

    def inactive(self):
        """Return inactive objects."""
        return ActiveQuerySet(self.model, using=self._db).filter(**{self.active_field: False})

    def all_objects(self):
        """Return all objects regardless of active status."""
        return ActiveQuerySet(self.model, using=self._db)


class AllActiveManager(ActiveManager):
    """Manager that returns all objects (doesn't filter by default)."""

    def __init__(self, *args, **kwargs):
        kwargs['filter_active'] = False
        super().__init__(*args, **kwargs)
