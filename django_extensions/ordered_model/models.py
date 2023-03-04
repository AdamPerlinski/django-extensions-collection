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
