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

    def test_move_down(self, create_tables):
        """Test moving an item down."""
        obj1 = ConcreteOrderedModel.objects.create(name='first')
        obj2 = ConcreteOrderedModel.objects.create(name='second')
        obj3 = ConcreteOrderedModel.objects.create(name='third')

        obj1.move_down()
        obj1.refresh_from_db()
        obj2.refresh_from_db()

        assert obj1.order == 2
        assert obj2.order == 1

    def test_move_to(self, create_tables):
        """Test moving to a specific position."""
        obj1 = ConcreteOrderedModel.objects.create(name='first')
        obj2 = ConcreteOrderedModel.objects.create(name='second')
        obj3 = ConcreteOrderedModel.objects.create(name='third')
        obj4 = ConcreteOrderedModel.objects.create(name='fourth')

        obj4.move_to(2)
        obj1.refresh_from_db()
        obj2.refresh_from_db()
        obj3.refresh_from_db()
        obj4.refresh_from_db()

        assert obj4.order == 2
        assert obj2.order == 3
        assert obj3.order == 4

    def test_move_to_top(self, create_tables):
        """Test moving to top."""
        obj1 = ConcreteOrderedModel.objects.create(name='first')
        obj2 = ConcreteOrderedModel.objects.create(name='second')
        obj3 = ConcreteOrderedModel.objects.create(name='third')

        obj3.move_to_top()
        obj1.refresh_from_db()
        obj2.refresh_from_db()
        obj3.refresh_from_db()

        assert obj3.order == 1
        assert obj1.order == 2
        assert obj2.order == 3

    def test_move_to_bottom(self, create_tables):
        """Test moving to bottom."""
        obj1 = ConcreteOrderedModel.objects.create(name='first')
        obj2 = ConcreteOrderedModel.objects.create(name='second')
        obj3 = ConcreteOrderedModel.objects.create(name='third')

        obj1.move_to_bottom()
        obj1.refresh_from_db()
        obj2.refresh_from_db()
        obj3.refresh_from_db()

        assert obj1.order == 3
        assert obj2.order == 1
        assert obj3.order == 2

    def test_is_first_property(self, create_tables):
        """Test is_first property."""
        obj1 = ConcreteOrderedModel.objects.create(name='first')
        obj2 = ConcreteOrderedModel.objects.create(name='second')

        assert obj1.is_first is True
        assert obj2.is_first is False

    def test_is_last_property(self, create_tables):
        """Test is_last property."""
        obj1 = ConcreteOrderedModel.objects.create(name='first')
        obj2 = ConcreteOrderedModel.objects.create(name='second')

        assert obj1.is_last is False
        assert obj2.is_last is True

    def test_get_previous(self, create_tables):
        """Test get_previous method."""
        obj1 = ConcreteOrderedModel.objects.create(name='first')
        obj2 = ConcreteOrderedModel.objects.create(name='second')

        assert obj1.get_previous() is None
        assert obj2.get_previous() == obj1

    def test_get_next(self, create_tables):
        """Test get_next method."""
        obj1 = ConcreteOrderedModel.objects.create(name='first')
        obj2 = ConcreteOrderedModel.objects.create(name='second')

        assert obj1.get_next() == obj2
        assert obj2.get_next() is None

    def test_move_up_at_top_does_nothing(self, create_tables):
        """Test move_up when already at top."""
        obj1 = ConcreteOrderedModel.objects.create(name='first')
        original_order = obj1.order

        obj1.move_up()
        obj1.refresh_from_db()

        assert obj1.order == original_order

    def test_move_down_at_bottom_does_nothing(self, create_tables):
        """Test move_down when already at bottom."""
        obj1 = ConcreteOrderedModel.objects.create(name='first')
        obj2 = ConcreteOrderedModel.objects.create(name='second')
        original_order = obj2.order

        obj2.move_down()
        obj2.refresh_from_db()

        assert obj2.order == original_order
