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
