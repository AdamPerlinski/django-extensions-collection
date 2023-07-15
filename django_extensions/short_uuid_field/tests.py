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
