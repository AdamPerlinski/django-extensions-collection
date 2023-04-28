"""Tests for ActivatorModel."""

import pytest
from django.db import models
from django.utils import timezone
from datetime import timedelta

from .models import ActivatorModel


class ConcreteActivatorModel(ActivatorModel):
    """Concrete model for testing."""
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'activator_model'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteActivatorModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteActivatorModel)
        except Exception:
            pass


class TestActivatorModel:
    """Test cases for ActivatorModel."""

    def test_model_is_abstract(self):
        """Test that ActivatorModel is abstract."""
        assert ActivatorModel._meta.abstract is True

    def test_fields_exist(self):
        """Test that all fields are defined."""
        assert ConcreteActivatorModel._meta.get_field('is_enabled') is not None
        assert ConcreteActivatorModel._meta.get_field('activate_date') is not None
        assert ConcreteActivatorModel._meta.get_field('deactivate_date') is not None

    def test_default_is_enabled(self, create_tables):
        """Test default is_enabled is True."""
        obj = ConcreteActivatorModel.objects.create(name='test')
        assert obj.is_enabled is True

    def test_is_active_when_enabled(self, create_tables):
        """Test is_active when enabled with no date restrictions."""
        obj = ConcreteActivatorModel.objects.create(name='test')
        assert obj.is_active is True

    def test_is_active_when_disabled(self, create_tables):
        """Test is_active when disabled."""
        obj = ConcreteActivatorModel.objects.create(name='test', is_enabled=False)
        assert obj.is_active is False

    def test_is_active_before_activate_date(self, create_tables):
        """Test is_active before activate_date."""
        future = timezone.now() + timedelta(days=1)
        obj = ConcreteActivatorModel.objects.create(
            name='test',
            activate_date=future
        )
        assert obj.is_active is False

    def test_is_active_after_activate_date(self, create_tables):
        """Test is_active after activate_date."""
        past = timezone.now() - timedelta(days=1)
