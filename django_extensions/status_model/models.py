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
