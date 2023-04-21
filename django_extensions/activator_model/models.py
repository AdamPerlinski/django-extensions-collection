"""
ActivatorModel - Abstract model with activation date ranges.

Usage:
    from django_extensions.activator_model import ActivatorModel

    class Promotion(ActivatorModel):
        name = models.CharField(max_length=100)
        discount = models.IntegerField()

    # Check if active now
    promo.is_active

    # Query active items
    Promotion.objects.active()
"""

from django.db import models
from django.utils import timezone


class ActivatorQuerySet(models.QuerySet):
    """QuerySet with activation filtering."""

    def active(self, at=None):
        """Return objects that are active at the given time (default: now)."""
        at = at or timezone.now()
        return self.filter(
            models.Q(activate_date__isnull=True) | models.Q(activate_date__lte=at),
            models.Q(deactivate_date__isnull=True) | models.Q(deactivate_date__gt=at),
            is_enabled=True
        )

    def inactive(self, at=None):
        """Return objects that are inactive at the given time."""
        at = at or timezone.now()
        return self.exclude(pk__in=self.active(at).values_list('pk', flat=True))

    def enabled(self):
        """Return objects where is_enabled is True."""
        return self.filter(is_enabled=True)

    def disabled(self):
        """Return objects where is_enabled is False."""
        return self.filter(is_enabled=False)


class ActivatorManager(models.Manager):
    """Manager using ActivatorQuerySet."""

    def get_queryset(self):
        return ActivatorQuerySet(self.model, using=self._db)

    def active(self, at=None):
        return self.get_queryset().active(at)

    def inactive(self, at=None):
