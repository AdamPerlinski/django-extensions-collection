"""
RandomManager - Manager with random ordering support.

Usage:
    from django_extensions.random_manager import RandomManager

    class Quote(models.Model):
        text = models.TextField()

        objects = RandomManager()

    # Get random quote
    Quote.objects.random()

    # Get 5 random quotes
    Quote.objects.random(5)

    # Random ordering
    Quote.objects.order_by_random()
"""

from django.db import models


class RandomQuerySet(models.QuerySet):
    """QuerySet with random selection methods."""

    def random(self, count=1):
        """
        Get random object(s) from the queryset.

        Args:
            count: Number of random objects to return (default 1).

        Returns:
            A single object if count=1, otherwise a list of objects.
        """
        if count == 1:
            return self.order_by('?').first()
        return list(self.order_by('?')[:count])
