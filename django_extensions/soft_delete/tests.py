"""Tests for SoftDeleteModel."""

import pytest
from django.db import models
from django.utils import timezone
from datetime import timedelta

from .models import SoftDeleteModel
from .managers import SoftDeleteManager, DeletedManager, AllObjectsManager


class ConcreteSoftDeleteModel(SoftDeleteModel):
    """Concrete model for testing."""
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'soft_delete'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteSoftDeleteModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteSoftDeleteModel)
        except Exception:
            pass


class TestSoftDeleteModel:
    """Test cases for SoftDeleteModel."""

    def test_model_is_abstract(self):
        """Test that SoftDeleteModel is abstract."""
        assert SoftDeleteModel._meta.abstract is True

    def test_deleted_at_field_exists(self):
        """Test that deleted_at field is defined."""
        field = ConcreteSoftDeleteModel._meta.get_field('deleted_at')
        assert field is not None
        assert field.null is True
        assert field.blank is True
        assert field.db_index is True

    def test_has_correct_managers(self):
        """Test that all managers are attached."""
        assert hasattr(ConcreteSoftDeleteModel, 'objects')
        assert hasattr(ConcreteSoftDeleteModel, 'deleted')
        assert hasattr(ConcreteSoftDeleteModel, 'all_objects')

    def test_soft_delete(self, create_tables):
        """Test soft delete sets deleted_at."""
        obj = ConcreteSoftDeleteModel.objects.create(name='test')
        assert obj.deleted_at is None

        obj.delete()
        obj.refresh_from_db()

        assert obj.deleted_at is not None
        assert obj.is_deleted is True
        assert obj.is_alive is False

    def test_soft_delete_excludes_from_default_manager(self, create_tables):
        """Test that soft-deleted objects are excluded from default queryset."""
        obj = ConcreteSoftDeleteModel.objects.create(name='test')
        obj.delete()

        assert ConcreteSoftDeleteModel.objects.filter(pk=obj.pk).count() == 0

    def test_soft_deleted_visible_in_all_objects(self, create_tables):
        """Test that soft-deleted objects are visible in all_objects."""
        obj = ConcreteSoftDeleteModel.objects.create(name='test')
        obj.delete()

        assert ConcreteSoftDeleteModel.all_objects.filter(pk=obj.pk).count() == 1

    def test_soft_deleted_visible_in_deleted_manager(self, create_tables):
        """Test that soft-deleted objects are visible in deleted manager."""
        obj = ConcreteSoftDeleteModel.objects.create(name='test')
        obj.delete()

        assert ConcreteSoftDeleteModel.deleted.filter(pk=obj.pk).count() == 1

    def test_restore(self, create_tables):
        """Test restoring a soft-deleted object."""
        obj = ConcreteSoftDeleteModel.objects.create(name='test')
        obj.delete()
        assert obj.is_deleted is True

        obj.restore()
        obj.refresh_from_db()

        assert obj.deleted_at is None
        assert obj.is_deleted is False
        assert obj.is_alive is True

    def test_hard_delete(self, create_tables):
        """Test hard delete permanently removes object."""
        obj = ConcreteSoftDeleteModel.objects.create(name='test')
        pk = obj.pk

        obj.hard_delete()

        assert ConcreteSoftDeleteModel.all_objects.filter(pk=pk).count() == 0

    def test_delete_with_hard_flag(self, create_tables):
        """Test delete with hard=True permanently removes object."""
        obj = ConcreteSoftDeleteModel.objects.create(name='test')
        pk = obj.pk

        obj.delete(hard=True)

        assert ConcreteSoftDeleteModel.all_objects.filter(pk=pk).count() == 0

    def test_queryset_delete(self, create_tables):
        """Test queryset delete soft-deletes all objects."""
        ConcreteSoftDeleteModel.objects.create(name='test1')
        ConcreteSoftDeleteModel.objects.create(name='test2')

        ConcreteSoftDeleteModel.objects.all().delete()

        assert ConcreteSoftDeleteModel.objects.count() == 0
        assert ConcreteSoftDeleteModel.all_objects.count() == 2

    def test_queryset_hard_delete(self, create_tables):
        """Test queryset hard_delete permanently removes all objects."""
        ConcreteSoftDeleteModel.objects.create(name='test1')
        ConcreteSoftDeleteModel.objects.create(name='test2')

        ConcreteSoftDeleteModel.all_objects.all().hard_delete()

        assert ConcreteSoftDeleteModel.all_objects.count() == 0

    def test_queryset_restore(self, create_tables):
        """Test queryset restore restores all soft-deleted objects."""
        obj1 = ConcreteSoftDeleteModel.objects.create(name='test1')
        obj2 = ConcreteSoftDeleteModel.objects.create(name='test2')
        obj1.delete()
        obj2.delete()

        ConcreteSoftDeleteModel.all_objects.all().restore()

        assert ConcreteSoftDeleteModel.objects.count() == 2

    def test_is_deleted_property(self, create_tables):
        """Test is_deleted property."""
        obj = ConcreteSoftDeleteModel.objects.create(name='test')
        assert obj.is_deleted is False

        obj.delete()
        assert obj.is_deleted is True

    def test_is_alive_property(self, create_tables):
        """Test is_alive property."""
        obj = ConcreteSoftDeleteModel.objects.create(name='test')
        assert obj.is_alive is True

        obj.delete()
        assert obj.is_alive is False
