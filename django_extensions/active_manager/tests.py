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

        qs = ConcreteActiveModel.all_objects.all()
        assert active in qs
        assert inactive in qs

    def test_active_method(self, create_tables):
        """Test active() method."""
        active = ConcreteActiveModel.objects.create(name='active', is_active=True)
        inactive = ConcreteActiveModel.objects.create(name='inactive', is_active=False)

        qs = ConcreteActiveModel.all_objects.active()
        assert active in qs
        assert inactive not in qs

    def test_inactive_method(self, create_tables):
        """Test inactive() method."""
        active = ConcreteActiveModel.objects.create(name='active', is_active=True)
        inactive = ConcreteActiveModel.objects.create(name='inactive', is_active=False)

        qs = ConcreteActiveModel.objects.inactive()
        assert active not in qs
        assert inactive in qs

    def test_activate_queryset(self, create_tables):
        """Test activate() on queryset."""
        obj = ConcreteActiveModel.objects.create(name='test', is_active=False)

        ConcreteActiveModel.all_objects.filter(pk=obj.pk).activate()
        obj.refresh_from_db()

        assert obj.is_active is True

    def test_deactivate_queryset(self, create_tables):
        """Test deactivate() on queryset."""
        obj = ConcreteActiveModel.objects.create(name='test', is_active=True)

        ConcreteActiveModel.all_objects.filter(pk=obj.pk).deactivate()
        obj.refresh_from_db()

        assert obj.is_active is False

    def test_all_objects_method(self, create_tables):
        """Test all_objects() method returns all."""
        active = ConcreteActiveModel.objects.create(name='active', is_active=True)
        inactive = ConcreteActiveModel.objects.create(name='inactive', is_active=False)

        qs = ConcreteActiveModel.objects.all_objects()
        assert active in qs
        assert inactive in qs

    def test_count_only_active(self, create_tables):
        """Test count only counts active objects."""
        ConcreteActiveModel.objects.create(name='active1', is_active=True)
        ConcreteActiveModel.objects.create(name='active2', is_active=True)
        ConcreteActiveModel.objects.create(name='inactive', is_active=False)

        assert ConcreteActiveModel.objects.count() == 2
        assert ConcreteActiveModel.all_objects.count() == 3


class TestActiveQuerySet:
    """Test cases for ActiveQuerySet."""

    def test_toggle(self, create_tables):
        """Test toggle() method."""
        obj1 = ConcreteActiveModel.objects.create(name='obj1', is_active=True)
        obj2 = ConcreteActiveModel.objects.create(name='obj2', is_active=False)

        ConcreteActiveModel.all_objects.all().toggle()

        obj1.refresh_from_db()
        obj2.refresh_from_db()

        assert obj1.is_active is False
        assert obj2.is_active is True

    def test_chaining(self, create_tables):
        """Test queryset method chaining."""
        ConcreteActiveModel.objects.create(name='a_active', is_active=True)
        ConcreteActiveModel.objects.create(name='b_active', is_active=True)
        ConcreteActiveModel.objects.create(name='a_inactive', is_active=False)

        qs = ConcreteActiveModel.all_objects.active().filter(name__startswith='a')
        assert qs.count() == 1
