"""Tests for ShortUUIDField."""

import pytest
from django.db import models
import string

from .fields import ShortUUIDField, generate_short_uuid


class ConcreteShortUUIDModel(models.Model):
    """Concrete model for testing."""
    short_id = ShortUUIDField()
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'short_uuid_field'


class CustomLengthModel(models.Model):
    """Model with custom length short UUID."""
    short_id = ShortUUIDField(length=12)
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'short_uuid_field'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteShortUUIDModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteShortUUIDModel)
        except Exception:
            pass


class TestShortUUIDField:
    """Test cases for ShortUUIDField."""

    def test_is_char_field(self):
        """Test ShortUUIDField is a CharField."""
        field = ShortUUIDField()
        assert isinstance(field, models.CharField)

    def test_default_length(self):
        """Test default length is 8."""
        field = ShortUUIDField()
        assert field.short_length == 8
        assert field.max_length == 8

    def test_custom_length(self):
        """Test custom length is respected."""
        field = ShortUUIDField(length=12)
        assert field.short_length == 12
        assert field.max_length == 12

    def test_default_unique(self):
        """Test field is unique by default."""
        field = ShortUUIDField()
        assert field.unique is True

    def test_default_not_editable(self):
        """Test field is not editable by default."""
        field = ShortUUIDField()
        assert field.editable is False

    def test_default_db_index(self):
        """Test field has db_index by default."""
        field = ShortUUIDField()
        assert field.db_index is True

    def test_auto_generate_on_create(self, create_tables):
        """Test short UUID is auto-generated on create."""
        obj = ConcreteShortUUIDModel.objects.create(name='test')
        assert obj.short_id is not None
        assert len(obj.short_id) == 8

    def test_generated_value_is_alphanumeric(self, create_tables):
        """Test generated value contains only alphanumeric characters."""
        obj = ConcreteShortUUIDModel.objects.create(name='test')
        valid_chars = string.ascii_letters + string.digits
        assert all(c in valid_chars for c in obj.short_id)

    def test_unique_values(self, create_tables):
        """Test multiple objects get unique values."""
        obj1 = ConcreteShortUUIDModel.objects.create(name='first')
        obj2 = ConcreteShortUUIDModel.objects.create(name='second')
        obj3 = ConcreteShortUUIDModel.objects.create(name='third')

        assert obj1.short_id != obj2.short_id
        assert obj2.short_id != obj3.short_id
        assert obj1.short_id != obj3.short_id

    def test_preserve_custom_value(self, create_tables):
        """Test that custom value is preserved."""
        obj = ConcreteShortUUIDModel(name='test', short_id='custom12')
        obj.save()
        assert obj.short_id == 'custom12'

    def test_not_regenerated_on_save(self, create_tables):
        """Test short UUID is not regenerated on subsequent saves."""
        obj = ConcreteShortUUIDModel.objects.create(name='test')
        original_id = obj.short_id

        obj.name = 'updated'
        obj.save()

        assert obj.short_id == original_id

    def test_deconstruct(self):
        """Test field deconstruction for migrations."""
        field = ShortUUIDField()
        name, path, args, kwargs = field.deconstruct()

        assert 'length' not in kwargs  # Default length
        assert 'unique' not in kwargs
        assert 'editable' not in kwargs
        assert 'db_index' not in kwargs

    def test_deconstruct_custom_length(self):
        """Test field deconstruction with custom length."""
        field = ShortUUIDField(length=12)
        name, path, args, kwargs = field.deconstruct()

        assert kwargs.get('length') == 12


class TestGenerateShortUUID:
    """Test cases for generate_short_uuid utility function."""

    def test_default_length(self):
        """Test default length is 8."""
        short_uuid = generate_short_uuid()
        assert len(short_uuid) == 8

    def test_custom_length(self):
        """Test custom length is respected."""
        short_uuid = generate_short_uuid(length=16)
        assert len(short_uuid) == 16

    def test_alphanumeric_only(self):
        """Test generated value is alphanumeric."""
        valid_chars = string.ascii_letters + string.digits
        for _ in range(100):
            short_uuid = generate_short_uuid()
            assert all(c in valid_chars for c in short_uuid)

    def test_uniqueness(self):
        """Test generated values are unique."""
        values = set(generate_short_uuid() for _ in range(1000))
        assert len(values) == 1000  # All unique
