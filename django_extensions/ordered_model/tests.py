"""Tests for OrderedModel."""

import pytest
from django.db import models

from .models import OrderedModel


class ConcreteOrderedModel(OrderedModel):
    """Concrete model for testing."""
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'ordered_model'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteOrderedModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteOrderedModel)
        except Exception:
            pass


class TestOrderedModel:
    """Test cases for OrderedModel."""

    def test_model_is_abstract(self):
        """Test that OrderedModel is abstract."""
        assert OrderedModel._meta.abstract is True

    def test_order_field_exists(self):
        """Test that order field is defined."""
        field = ConcreteOrderedModel._meta.get_field('order')
        assert field is not None
        assert field.db_index is True

    def test_default_ordering(self):
        """Test default ordering is by order in abstract model."""
        # Abstract model defines the ordering; concrete models can override
        assert OrderedModel._meta.ordering == ['order']

    def test_auto_order_on_create(self, create_tables):
        """Test order is auto-set on creation."""
        obj1 = ConcreteOrderedModel.objects.create(name='first')
        obj2 = ConcreteOrderedModel.objects.create(name='second')
        obj3 = ConcreteOrderedModel.objects.create(name='third')

        assert obj1.order == 1
        assert obj2.order == 2
        assert obj3.order == 3

    def test_move_up(self, create_tables):
        """Test moving an item up."""
        obj1 = ConcreteOrderedModel.objects.create(name='first')
        obj2 = ConcreteOrderedModel.objects.create(name='second')
        obj3 = ConcreteOrderedModel.objects.create(name='third')

        obj3.move_up()
        obj1.refresh_from_db()
        obj2.refresh_from_db()
        obj3.refresh_from_db()

        assert obj3.order == 2
        assert obj2.order == 3
