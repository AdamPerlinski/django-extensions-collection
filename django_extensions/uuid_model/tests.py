"""Tests for UUIDModel."""

import uuid
import pytest
from django.db import models

from .models import UUIDModel


class ConcreteUUIDModel(UUIDModel):
    """Concrete model for testing."""
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'uuid_model'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteUUIDModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteUUIDModel)
        except Exception:
            pass


class TestUUIDModel:
    """Test cases for UUIDModel."""

    def test_model_is_abstract(self):
        """Test that UUIDModel is abstract."""
        assert UUIDModel._meta.abstract is True

    def test_id_field_is_uuid(self):
        """Test that id field is a UUIDField."""
        field = ConcreteUUIDModel._meta.get_field('id')
        assert isinstance(field, models.UUIDField)
        assert field.primary_key is True
        assert field.editable is False

    def test_id_has_default(self):
        """Test that id has uuid4 as default."""
        field = ConcreteUUIDModel._meta.get_field('id')
        assert field.default == uuid.uuid4

    def test_uuid_auto_generated(self, create_tables):
        """Test that UUID is automatically generated."""
        obj = ConcreteUUIDModel.objects.create(name='test')
        assert obj.id is not None
        assert isinstance(obj.id, uuid.UUID)

    def test_uuid_is_unique(self, create_tables):
        """Test that each object gets a unique UUID."""
        obj1 = ConcreteUUIDModel.objects.create(name='test1')
        obj2 = ConcreteUUIDModel.objects.create(name='test2')
        assert obj1.id != obj2.id

    def test_short_id_property(self, create_tables):
        """Test short_id returns first 8 characters."""
        obj = ConcreteUUIDModel.objects.create(name='test')
        assert obj.short_id == str(obj.id)[:8]
        assert len(obj.short_id) == 8

    def test_hex_id_property(self, create_tables):
        """Test hex_id returns 32-character hex string."""
        obj = ConcreteUUIDModel.objects.create(name='test')
        assert obj.hex_id == obj.id.hex
        assert len(obj.hex_id) == 32
        assert all(c in '0123456789abcdef' for c in obj.hex_id)

    def test_get_by_short_id(self, create_tables):
        """Test get_by_short_id classmethod."""
        obj = ConcreteUUIDModel.objects.create(name='test')
        found = ConcreteUUIDModel.get_by_short_id(obj.short_id)
        assert found == obj

    def test_get_by_short_id_not_found(self, create_tables):
        """Test get_by_short_id returns None when not found."""
        found = ConcreteUUIDModel.get_by_short_id('nonexist')
        assert found is None

    def test_can_set_custom_uuid(self, create_tables):
        """Test that custom UUID can be set on creation."""
        custom_uuid = uuid.uuid4()
        obj = ConcreteUUIDModel(id=custom_uuid, name='test')
        obj.save()
        assert obj.id == custom_uuid

    def test_uuid_preserved_on_save(self, create_tables):
        """Test that UUID is preserved on save."""
        obj = ConcreteUUIDModel.objects.create(name='test')
        original_id = obj.id
        obj.name = 'updated'
        obj.save()
        assert obj.id == original_id
