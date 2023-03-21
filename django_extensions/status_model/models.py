"""
StatusModel - Abstract model with status field and transitions.

Usage:
    from django_extensions.status_model import StatusModel

    class Order(StatusModel):
        STATUS_CHOICES = [
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('shipped', 'Shipped'),
            ('delivered', 'Delivered'),
        ]
        status = StatusField(choices=STATUS_CHOICES, default='pending')
        name = models.CharField(max_length=100)

    order.set_status('processing')
    order.is_pending  # Auto-generated property
"""

from django.db import models
from django.utils import timezone


class StatusField(models.CharField):
    """CharField that tracks status changes."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 50)
        kwargs.setdefault('db_index', True)
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super().contribute_to_class(cls, name)

        # Add is_<status> properties for each choice
        if self.choices:
            for value, label in self.choices:
                prop_name = f'is_{value}'
                if not hasattr(cls, prop_name):
                    setattr(cls, prop_name, self._make_status_property(name, value))

    def _make_status_property(self, field_name, status_value):
        """Create a property to check if status equals a value."""
        def getter(self):
            return getattr(self, field_name) == status_value
        return property(getter)


class StatusModel(models.Model):
    """
    An abstract base model that provides status tracking functionality.
    Subclasses should define STATUS_CHOICES and a status field.
    """
    status_changed = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when status was last changed."
    )

    class Meta:
        abstract = True

    def set_status(self, new_status, save=True):
        """
        Set a new status and update status_changed timestamp.

        Args:
            new_status: The new status value.
            save: Whether to save the model after setting status.

        Returns:
            The previous status value.
        """
        status_field = self._get_status_field_name()
        old_status = getattr(self, status_field)

        if old_status != new_status:
            setattr(self, status_field, new_status)
            self.status_changed = timezone.now()

            if save:
                self.save(update_fields=[status_field, 'status_changed'])

        return old_status

    def _get_status_field_name(self):
        """Get the name of the status field."""
        for field in self._meta.fields:
            if isinstance(field, StatusField):
                return field.name
        # Default to 'status' if no StatusField found
        return 'status'

    @property
    def status_age(self):
        """Return time since last status change."""
        if self.status_changed:
            return timezone.now() - self.status_changed
        return None

    def get_available_statuses(self):
        """Get list of available status values."""
        status_field = self._get_status_field_name()
        field = self._meta.get_field(status_field)
        if field.choices:
            return [choice[0] for choice in field.choices]
        return []

    def get_status_display_name(self):
        """Get the display name of the current status."""
        status_field = self._get_status_field_name()
        return getattr(self, f'get_{status_field}_display')()
