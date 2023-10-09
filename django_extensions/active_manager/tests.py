"""Tests for ActiveManager."""

import pytest
from django.db import models

from .managers import ActiveManager, ActiveQuerySet


class ConcreteActiveModel(models.Model):
    """Concrete model for testing."""
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    objects = ActiveManager()
    all_objects = ActiveManager(filter_active=False)

    class Meta:
        app_label = 'active_manager'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteActiveModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteActiveModel)
        except Exception:
            pass


class TestActiveManager:
    """Test cases for ActiveManager."""

    def test_default_returns_active_only(self, create_tables):
        """Test default queryset returns only active objects."""
        active = ConcreteActiveModel.objects.create(name='active', is_active=True)
        inactive = ConcreteActiveModel.objects.create(name='inactive', is_active=False)

        qs = ConcreteActiveModel.objects.all()
        assert active in qs
        assert inactive not in qs

    def test_all_objects_returns_everything(self, create_tables):
        """Test all_objects returns active and inactive."""
        active = ConcreteActiveModel.objects.create(name='active', is_active=True)
        inactive = ConcreteActiveModel.objects.create(name='inactive', is_active=False)

