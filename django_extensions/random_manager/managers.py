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

    def order_by_random(self):
        """Return queryset ordered randomly."""
        return self.order_by('?')

    def random_slice(self, start, end):
        """
        Get a random slice of the queryset.

        This is more efficient than slicing after random ordering
        for large querysets.
        """
        total = self.count()
        if total == 0:
            return []

        # Ensure valid range
        start = max(0, start)
        end = min(total, end)
        count = end - start

        if count <= 0:
            return []

        return list(self.order_by('?')[:count])

    def exclude_pks(self, *pks):
        """Exclude specific primary keys from random selection."""
        return self.exclude(pk__in=pks)

    def weighted_random(self, weight_field):
        """
        Get a random object weighted by a field value.
        Objects with higher weight values are more likely to be selected.

        Note: This loads all objects into memory, use with caution on large querysets.
        """
        import random

        items = list(self.values_list('pk', weight_field))
        if not items:
            return None

        pks, weights = zip(*items)
        # Normalize negative weights to 0
        weights = [max(0, w) for w in weights]

        if sum(weights) == 0:
            # All weights are 0, fall back to uniform random
            selected_pk = random.choice(pks)
        else:
            selected_pk = random.choices(pks, weights=weights, k=1)[0]

        return self.get(pk=selected_pk)


class RandomManager(models.Manager):
    """Manager with random selection methods."""

    def get_queryset(self):
        return RandomQuerySet(self.model, using=self._db)

    def random(self, count=1):
        """Get random object(s)."""
        return self.get_queryset().random(count)

    def order_by_random(self):
        """Get queryset ordered randomly."""
        return self.get_queryset().order_by_random()

    def random_excluding(self, *pks):
        """Get a random object excluding specific PKs."""
        return self.get_queryset().exclude_pks(*pks).random()

    def weighted_random(self, weight_field):
        """Get a weighted random object."""
        return self.get_queryset().weighted_random(weight_field)
