"""
OrderedModel - Abstract model with ordering support.

Usage:
    from django_extensions.ordered_model import OrderedModel

    class MyModel(OrderedModel):
        name = models.CharField(max_length=100)

    # Move items
    obj.move_up()
    obj.move_down()
    obj.move_to(3)
    obj.move_to_top()
    obj.move_to_bottom()
"""

from django.db import models, transaction


class OrderedModel(models.Model):
    """
    An abstract base model that provides ordering functionality.
    """
    order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Order position of this record."
    )

    class Meta:
        abstract = True
        ordering = ['order']

    def save(self, *args, **kwargs):
        """Set order to end if not specified."""
        if self.pk is None and self.order == 0:
            max_order = self.__class__.objects.aggregate(
                max_order=models.Max('order')
            )['max_order']
            self.order = (max_order or 0) + 1
        super().save(*args, **kwargs)

    def _get_ordering_queryset(self):
        """Override this to change the queryset used for ordering."""
        return self.__class__.objects.all()

    @transaction.atomic
    def move_up(self):
        """Move this item up one position."""
        qs = self._get_ordering_queryset()
        previous = qs.filter(order__lt=self.order).order_by('-order').first()
        if previous:
            self._swap_order(previous)

    @transaction.atomic
    def move_down(self):
        """Move this item down one position."""
        qs = self._get_ordering_queryset()
        next_item = qs.filter(order__gt=self.order).order_by('order').first()
        if next_item:
            self._swap_order(next_item)

    def _swap_order(self, other):
        """Swap order with another item."""
        self.order, other.order = other.order, self.order
        self.save(update_fields=['order'])
        other.save(update_fields=['order'])

    @transaction.atomic
    def move_to(self, position):
        """Move this item to a specific position."""
        if position < 1:
            position = 1

        qs = self._get_ordering_queryset().exclude(pk=self.pk)

        if position > self.order:
            # Moving down
            items_to_shift = qs.filter(
                order__gt=self.order,
                order__lte=position
            )
            items_to_shift.update(order=models.F('order') - 1)
        else:
            # Moving up
            items_to_shift = qs.filter(
                order__gte=position,
                order__lt=self.order
            )
            items_to_shift.update(order=models.F('order') + 1)

        self.order = position
        self.save(update_fields=['order'])

    @transaction.atomic
    def move_to_top(self):
        """Move this item to the first position."""
        if self.order > 1:
            self.move_to(1)

    @transaction.atomic
    def move_to_bottom(self):
        """Move this item to the last position."""
        qs = self._get_ordering_queryset()
        max_order = qs.aggregate(max_order=models.Max('order'))['max_order'] or 0
        if self.order < max_order:
            self.move_to(max_order)

    @property
    def is_first(self):
        """Check if this item is first in order."""
        qs = self._get_ordering_queryset()
        return not qs.filter(order__lt=self.order).exists()

    @property
    def is_last(self):
        """Check if this item is last in order."""
        qs = self._get_ordering_queryset()
        return not qs.filter(order__gt=self.order).exists()

    def get_previous(self):
        """Get the previous item in order."""
        qs = self._get_ordering_queryset()
        return qs.filter(order__lt=self.order).order_by('-order').first()

    def get_next(self):
        """Get the next item in order."""
        qs = self._get_ordering_queryset()
        return qs.filter(order__gt=self.order).order_by('order').first()
