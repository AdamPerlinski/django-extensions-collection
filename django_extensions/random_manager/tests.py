"""Tests for RandomManager."""

import pytest
from django.db import models

from .managers import RandomManager, RandomQuerySet


class ConcreteRandomModel(models.Model):
    """Concrete model for testing."""
    name = models.CharField(max_length=100)
    weight = models.IntegerField(default=1)

    objects = RandomManager()

    class Meta:
        app_label = 'random_manager'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteRandomModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteRandomModel)
        except Exception:
            pass


class TestRandomManager:
    """Test cases for RandomManager."""

    def test_random_single(self, create_tables):
        """Test getting a single random object."""
        obj1 = ConcreteRandomModel.objects.create(name='obj1')
        obj2 = ConcreteRandomModel.objects.create(name='obj2')

        result = ConcreteRandomModel.objects.random()
        assert result in [obj1, obj2]

    def test_random_multiple(self, create_tables):
        """Test getting multiple random objects."""
        for i in range(10):
            ConcreteRandomModel.objects.create(name=f'obj{i}')

        result = ConcreteRandomModel.objects.random(5)
        assert len(result) == 5
        assert len(set(result)) == 5  # All unique

    def test_random_empty(self, create_tables):
        """Test random on empty queryset."""
        result = ConcreteRandomModel.objects.random()
        assert result is None

    def test_random_more_than_available(self, create_tables):
        """Test requesting more random items than available."""
        ConcreteRandomModel.objects.create(name='obj1')
        ConcreteRandomModel.objects.create(name='obj2')

        result = ConcreteRandomModel.objects.random(10)
        assert len(result) == 2

    def test_order_by_random(self, create_tables):
        """Test random ordering."""
        for i in range(5):
            ConcreteRandomModel.objects.create(name=f'obj{i}')

        qs = ConcreteRandomModel.objects.order_by_random()
        assert qs.count() == 5

    def test_random_excluding(self, create_tables):
        """Test random with exclusions."""
        obj1 = ConcreteRandomModel.objects.create(name='obj1')
        obj2 = ConcreteRandomModel.objects.create(name='obj2')
        obj3 = ConcreteRandomModel.objects.create(name='obj3')

        # Exclude obj1 and obj2
        for _ in range(20):
            result = ConcreteRandomModel.objects.random_excluding(obj1.pk, obj2.pk)
            assert result == obj3

    def test_random_slice(self, create_tables):
        """Test random_slice method."""
        for i in range(10):
            ConcreteRandomModel.objects.create(name=f'obj{i}')

        result = ConcreteRandomModel.objects.all().random_slice(0, 3)
        assert len(result) == 3

    def test_random_slice_empty(self, create_tables):
        """Test random_slice on empty queryset."""
        result = ConcreteRandomModel.objects.all().random_slice(0, 5)
        assert result == []

    def test_weighted_random(self, create_tables):
        """Test weighted random selection."""
        # Create objects with different weights
        heavy = ConcreteRandomModel.objects.create(name='heavy', weight=100)
        light = ConcreteRandomModel.objects.create(name='light', weight=1)

        # Run many times and count
        heavy_count = 0
        total = 100
        for _ in range(total):
            result = ConcreteRandomModel.objects.weighted_random('weight')
            if result == heavy:
                heavy_count += 1

        # Heavy should be selected much more often (statistically)
        assert heavy_count > 50  # Should be around 99

    def test_weighted_random_zero_weights(self, create_tables):
        """Test weighted random with zero weights."""
        obj1 = ConcreteRandomModel.objects.create(name='obj1', weight=0)
        obj2 = ConcreteRandomModel.objects.create(name='obj2', weight=0)

        result = ConcreteRandomModel.objects.weighted_random('weight')
        assert result in [obj1, obj2]

    def test_weighted_random_empty(self, create_tables):
        """Test weighted random on empty queryset."""
        result = ConcreteRandomModel.objects.weighted_random('weight')
        assert result is None

    def test_chaining(self, create_tables):
        """Test method chaining with filters."""
        for i in range(5):
            ConcreteRandomModel.objects.create(name=f'group_a_{i}', weight=1)
        for i in range(5):
            ConcreteRandomModel.objects.create(name=f'group_b_{i}', weight=1)

        result = ConcreteRandomModel.objects.filter(name__startswith='group_a').random()
        assert result.name.startswith('group_a')

    def test_randomness(self, create_tables):
        """Test that results are actually random."""
        for i in range(10):
            ConcreteRandomModel.objects.create(name=f'obj{i}')

        # Get random results multiple times
        results = [ConcreteRandomModel.objects.random().pk for _ in range(20)]

        # Should have some variety (not all the same)
        assert len(set(results)) > 1
