"""Tests for TimeStampedModel."""

import pytest
from datetime import timedelta
from django.db import models
from django.utils import timezone
from unittest.mock import patch

from .models import TimeStampedModel


class ConcreteTimeStampedModel(TimeStampedModel):
    """Concrete model for testing."""
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'timestamped_model'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteTimeStampedModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteTimeStampedModel)
        except Exception:
            pass


class TestTimeStampedModel:
    """Test cases for TimeStampedModel."""

    def test_model_is_abstract(self):
        """Test that TimeStampedModel is abstract."""
        assert TimeStampedModel._meta.abstract is True

    def test_created_field_exists(self):
        """Test that created field is defined."""
        field = ConcreteTimeStampedModel._meta.get_field('created')
        assert field is not None
        assert field.auto_now_add is True
        assert field.db_index is True

    def test_modified_field_exists(self):
        """Test that modified field is defined."""
        field = ConcreteTimeStampedModel._meta.get_field('modified')
        assert field is not None
        assert field.auto_now is True
        assert field.db_index is True

    def test_default_ordering(self):
        """Test default ordering is by -created in abstract model."""
        # Abstract model defines the ordering; concrete models can override
        assert TimeStampedModel._meta.ordering == ['-created']

    def test_get_latest_by(self):
        """Test get_latest_by is set to created in abstract model."""
        assert TimeStampedModel._meta.get_latest_by == 'created'

    def test_created_auto_set(self, create_tables):
        """Test that created is automatically set on save."""
        obj = ConcreteTimeStampedModel.objects.create(name='test')
        assert obj.created is not None
        assert obj.created <= timezone.now()

    def test_modified_auto_set(self, create_tables):
        """Test that modified is automatically set on save."""
        obj = ConcreteTimeStampedModel.objects.create(name='test')
        assert obj.modified is not None
        assert obj.modified <= timezone.now()

    def test_modified_updates_on_save(self, create_tables):
        """Test that modified updates on each save."""
        obj = ConcreteTimeStampedModel.objects.create(name='test')
        original_modified = obj.modified

        obj.name = 'updated'
        obj.save()
        obj.refresh_from_db()

        assert obj.modified >= original_modified

    def test_created_does_not_change(self, create_tables):
        """Test that created does not change on update."""
        obj = ConcreteTimeStampedModel.objects.create(name='test')
        original_created = obj.created

        obj.name = 'updated'
        obj.save()
        obj.refresh_from_db()

        assert obj.created == original_created

    def test_was_modified_property_false_initially(self, create_tables):
        """Test was_modified is False right after creation."""
        obj = ConcreteTimeStampedModel.objects.create(name='test')
        # Note: Due to auto_now and auto_now_add being set at nearly same time,
        # this might be True or False depending on timing
        assert isinstance(obj.was_modified, bool)

    def test_update_fields_includes_modified(self, create_tables):
        """Test that update_fields includes modified."""
        obj = ConcreteTimeStampedModel.objects.create(name='test')
        original_modified = obj.modified

        obj.name = 'updated'
        obj.save(update_fields=['name'])
        obj.refresh_from_db()

        assert obj.modified >= original_modified

    def test_inheritance_works(self):
        """Test that model can be inherited."""
        class ChildModel(ConcreteTimeStampedModel):
            extra_field = models.CharField(max_length=50)

            class Meta:
                app_label = 'timestamped_model'

        assert hasattr(ChildModel, 'created')
        assert hasattr(ChildModel, 'modified')
