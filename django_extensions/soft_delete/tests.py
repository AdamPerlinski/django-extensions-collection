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
