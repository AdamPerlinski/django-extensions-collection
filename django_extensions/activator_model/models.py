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
        return self.get_queryset().inactive(at)


class ActivatorModel(models.Model):
    """
    An abstract base model that provides activation/deactivation
    functionality with date ranges.
    """
    is_enabled = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Master switch to enable/disable this item."
    )
    activate_date = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Date/time when this item becomes active."
    )
    deactivate_date = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Date/time when this item becomes inactive."
    )

    objects = ActivatorManager()

    class Meta:
        abstract = True

    @property
    def is_active(self):
        """Check if the object is currently active."""
        if not self.is_enabled:
            return False

        now = timezone.now()

        if self.activate_date and now < self.activate_date:
            return False

        if self.deactivate_date and now >= self.deactivate_date:
            return False

        return True

    def activate(self, save=True):
        """Enable and clear date restrictions."""
        self.is_enabled = True
        self.activate_date = None
        self.deactivate_date = None
        if save:
            self.save(update_fields=['is_enabled', 'activate_date', 'deactivate_date'])

    def deactivate(self, save=True):
        """Disable the object."""
        self.is_enabled = False
        if save:
            self.save(update_fields=['is_enabled'])

    def schedule_activation(self, start, end=None, save=True):
        """Schedule activation between start and end dates."""
        self.is_enabled = True
        self.activate_date = start
        self.deactivate_date = end
        if save:
            self.save(update_fields=['is_enabled', 'activate_date', 'deactivate_date'])

    @property
    def activation_status(self):
        """Return a string describing the activation status."""
        if not self.is_enabled:
            return 'disabled'

        now = timezone.now()

        if self.activate_date and now < self.activate_date:
            return 'scheduled'

        if self.deactivate_date and now >= self.deactivate_date:
            return 'expired'

        return 'active'

    @property
    def time_until_active(self):
        """Return time until activation, or None if already active or disabled."""
        if not self.is_enabled:
            return None

        now = timezone.now()

        if self.activate_date and now < self.activate_date:
            return self.activate_date - now

        return None

    @property
    def time_until_inactive(self):
        """Return time until deactivation, or None if no deactivation scheduled."""
        if not self.is_active:
            return None

        if self.deactivate_date:
            return self.deactivate_date - timezone.now()

        return None
