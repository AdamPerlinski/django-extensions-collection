"""Tests for AutoModifiedField."""

import pytest
from django.db import models
from django.utils import timezone
from datetime import timedelta
import time

from .fields import AutoModifiedField


class ConcreteAutoModifiedModel(models.Model):
    """Concrete model for testing."""
    modified = AutoModifiedField()
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'auto_modified_field'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteAutoModifiedModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteAutoModifiedModel)
        except Exception:
            pass


class TestAutoModifiedField:
    """Test cases for AutoModifiedField."""

    def test_is_datetime_field(self):
        """Test AutoModifiedField is a DateTimeField."""
        field = AutoModifiedField()
        assert isinstance(field, models.DateTimeField)

    def test_default_not_editable(self):
        """Test field is not editable by default."""
        field = AutoModifiedField()
        assert field.editable is False

    def test_default_db_index(self):
        """Test field has db_index by default."""
        field = AutoModifiedField()
        assert field.db_index is True

    def test_auto_set_on_create(self, create_tables):
        """Test field is auto-set on create."""
        before = timezone.now()
        obj = ConcreteAutoModifiedModel.objects.create(name='test')
        after = timezone.now()

        assert obj.modified is not None
        assert before <= obj.modified <= after

    def test_updated_on_every_save(self, create_tables):
        """Test field is updated on subsequent saves."""
        obj = ConcreteAutoModifiedModel.objects.create(name='test')
        original_modified = obj.modified

        time.sleep(0.01)  # Small delay to ensure different timestamp
        obj.name = 'updated'
        obj.save()

        assert obj.modified > original_modified

    def test_updated_even_without_changes(self, create_tables):
        """Test field is updated even when no other fields change."""
        obj = ConcreteAutoModifiedModel.objects.create(name='test')
        original_modified = obj.modified

        time.sleep(0.01)
        obj.save()

        assert obj.modified > original_modified

    def test_deconstruct(self):
        """Test field deconstruction for migrations."""
        field = AutoModifiedField()
        name, path, args, kwargs = field.deconstruct()

        assert 'editable' not in kwargs
        assert 'db_index' not in kwargs

    def test_custom_db_index_false(self):
        """Test custom db_index can be set to False."""
        field = AutoModifiedField(db_index=False)
        assert field.db_index is False

    def test_custom_editable_true(self):
        """Test custom editable can be set to True."""
        field = AutoModifiedField(editable=True)
        assert field.editable is True
