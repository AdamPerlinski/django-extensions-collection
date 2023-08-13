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
        )
        with pytest.raises(ValidationError):
            obj.full_clean()

    def test_array_items_validation(self, create_tables):
        """Test array items type validation."""
        obj = ConcreteJSONSchemaModel(
            name='test',
            config={'name': 'Test', 'tags': ['valid', 123]}  # Invalid item
        )
        with pytest.raises(ValidationError):
            obj.full_clean()

    def test_null_value_allowed(self, create_tables):
        """Test null value is allowed when field is nullable."""
        obj = ConcreteJSONSchemaModel(name='test', config=None)
        obj.full_clean()  # Should not raise
        obj.save()

    def test_no_schema_validation(self, create_tables):
        """Test field without schema accepts any JSON."""
        class NoSchemaModel(models.Model):
            data = JSONSchemaField()

            class Meta:
                app_label = 'json_schema_field'

        field = NoSchemaModel._meta.get_field('data')
        # Should not raise for any value
        field.validate({'any': 'data', 'nested': {'value': 123}}, None)

    def test_deconstruct_with_schema(self):
        """Test field deconstruction includes schema."""
        schema = {'type': 'object'}
        field = JSONSchemaField(schema=schema)
        name, path, args, kwargs = field.deconstruct()
        assert kwargs.get('schema') == schema

    def test_deconstruct_without_schema(self):
        """Test field deconstruction without schema."""
        field = JSONSchemaField()
        name, path, args, kwargs = field.deconstruct()
        assert 'schema' not in kwargs


class TestJSONSchemaValidation:
    """Test cases for schema validation logic."""

    def test_string_min_length(self):
        """Test string minLength validation."""
        field = JSONSchemaField(schema={
            'type': 'string',
            'minLength': 5
        })
        with pytest.raises(ValidationError):
            field.validate_schema('abc')

    def test_string_max_length(self):
        """Test string maxLength validation."""
        field = JSONSchemaField(schema={
            'type': 'string',
            'maxLength': 5
        })
        with pytest.raises(ValidationError):
            field.validate_schema('abcdefgh')

    def test_string_pattern(self):
        """Test string pattern validation."""
        field = JSONSchemaField(schema={
            'type': 'string',
            'pattern': r'^\d{3}-\d{4}$'
        })
        field.validate_schema('123-4567')  # Valid
        with pytest.raises(ValidationError):
            field.validate_schema('invalid')

    def test_number_maximum(self):
        """Test number maximum validation."""
        field = JSONSchemaField(schema={
            'type': 'number',
            'maximum': 100
        })
        with pytest.raises(ValidationError):
            field.validate_schema(150)

    def test_array_min_items(self):
        """Test array minItems validation."""
        field = JSONSchemaField(schema={
            'type': 'array',
            'minItems': 2
        })
        with pytest.raises(ValidationError):
            field.validate_schema([1])

    def test_array_max_items(self):
        """Test array maxItems validation."""
        field = JSONSchemaField(schema={
            'type': 'array',
            'maxItems': 2
        })
        with pytest.raises(ValidationError):
            field.validate_schema([1, 2, 3])

    def test_enum_validation(self):
        """Test enum validation."""
        field = JSONSchemaField(schema={
            'enum': ['red', 'green', 'blue']
        })
        field.validate_schema('red')  # Valid
        with pytest.raises(ValidationError):
            field.validate_schema('yellow')

    def test_boolean_type(self):
        """Test boolean type validation."""
        field = JSONSchemaField(schema={'type': 'boolean'})
        field.validate_schema(True)
        field.validate_schema(False)
        with pytest.raises(ValidationError):
            field.validate_schema(1)  # Integer is not boolean

    def test_nested_object_validation(self):
        """Test nested object validation."""
        field = JSONSchemaField(schema={
            'type': 'object',
            'properties': {
                'nested': {
                    'type': 'object',
                    'properties': {
                        'value': {'type': 'integer'}
                    }
                }
            }
        })
        field.validate_schema({'nested': {'value': 123}})  # Valid
        with pytest.raises(ValidationError):
            field.validate_schema({'nested': {'value': 'string'}})
