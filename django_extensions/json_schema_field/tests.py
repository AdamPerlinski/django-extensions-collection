"""Tests for JSONSchemaField."""

import pytest
from django.core.exceptions import ValidationError
from django.db import models

from .fields import JSONSchemaField


class ConcreteJSONSchemaModel(models.Model):
    """Concrete model for testing."""
    config = JSONSchemaField(
        schema={
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'count': {'type': 'integer', 'minimum': 0},
                'tags': {
                    'type': 'array',
                    'items': {'type': 'string'}
                }
            },
            'required': ['name']
        },
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'json_schema_field'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteJSONSchemaModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteJSONSchemaModel)
        except Exception:
            pass


class TestJSONSchemaField:
    """Test cases for JSONSchemaField."""

    def test_is_json_field(self):
        """Test JSONSchemaField is a JSONField."""
        field = JSONSchemaField()
        assert isinstance(field, models.JSONField)

    def test_valid_data(self, create_tables):
        """Test saving valid JSON data."""
        obj = ConcreteJSONSchemaModel(
            name='test',
            config={'name': 'Test', 'count': 5, 'tags': ['a', 'b']}
        )
        obj.full_clean()  # Should not raise
        obj.save()

    def test_missing_required_field(self, create_tables):
        """Test validation fails for missing required field."""
        obj = ConcreteJSONSchemaModel(
            name='test',
            config={'count': 5}  # Missing 'name'
        )
        with pytest.raises(ValidationError):
            obj.full_clean()

    def test_wrong_type(self, create_tables):
        """Test validation fails for wrong type."""
        obj = ConcreteJSONSchemaModel(
            name='test',
            config={'name': 123}  # Should be string
        )
        with pytest.raises(ValidationError):
            obj.full_clean()

    def test_minimum_validation(self, create_tables):
        """Test minimum value validation."""
        obj = ConcreteJSONSchemaModel(
            name='test',
            config={'name': 'Test', 'count': -5}  # Below minimum
