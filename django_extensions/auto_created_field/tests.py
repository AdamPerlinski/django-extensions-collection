"""Tests for AutoCreatedField."""

import pytest
from django.db import models
from django.utils import timezone
from datetime import timedelta

from .fields import AutoCreatedField


class ConcreteAutoCreatedModel(models.Model):
    """Concrete model for testing."""
    created = AutoCreatedField()
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'auto_created_field'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteAutoCreatedModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteAutoCreatedModel)
        except Exception:
            pass


class TestAutoCreatedField:
    """Test cases for AutoCreatedField."""

    def test_is_datetime_field(self):
        """Test AutoCreatedField is a DateTimeField."""
        field = AutoCreatedField()
        assert isinstance(field, models.DateTimeField)

    def test_default_not_editable(self):
        """Test field is not editable by default."""
        field = AutoCreatedField()
        assert field.editable is False

    def test_default_db_index(self):
        """Test field has db_index by default."""
        field = AutoCreatedField()
        assert field.db_index is True

    def test_auto_set_on_create(self, create_tables):
        """Test field is auto-set on create."""
        before = timezone.now()
        obj = ConcreteAutoCreatedModel.objects.create(name='test')
        after = timezone.now()

        assert obj.created is not None
        assert before <= obj.created <= after

    def test_not_updated_on_save(self, create_tables):
        """Test field is not updated on subsequent saves."""
        obj = ConcreteAutoCreatedModel.objects.create(name='test')
        original_created = obj.created

        obj.name = 'updated'
        obj.save()
        obj.refresh_from_db()

        assert obj.created == original_created

    def test_multiple_objects_different_times(self, create_tables):
        """Test different objects get different timestamps."""
        obj1 = ConcreteAutoCreatedModel.objects.create(name='first')
        obj2 = ConcreteAutoCreatedModel.objects.create(name='second')

        # They might be equal if created in same millisecond
        assert obj1.created <= obj2.created

    def test_deconstruct(self):
        """Test field deconstruction for migrations."""
        field = AutoCreatedField()
        name, path, args, kwargs = field.deconstruct()

        assert 'editable' not in kwargs
        assert 'db_index' not in kwargs

    def test_custom_db_index_false(self):
        """Test custom db_index can be set to False."""
        field = AutoCreatedField(db_index=False)
        assert field.db_index is False

    def test_custom_editable_true(self):
        """Test custom editable can be set to True."""
        field = AutoCreatedField(editable=True)
        assert field.editable is True
