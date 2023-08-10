"""
JSONSchemaField - JSONField with schema validation.

Usage:
    from django_extensions.json_schema_field import JSONSchemaField

    class MyModel(models.Model):
        config = JSONSchemaField(schema={
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'count': {'type': 'integer', 'minimum': 0}
            },
            'required': ['name']
        })
"""

import json
from django.core.exceptions import ValidationError
from django.db import models


class JSONSchemaField(models.JSONField):
    """
    A JSONField that validates data against a JSON schema.
    """

    def __init__(self, *args, schema=None, **kwargs):
        self.schema = schema
        super().__init__(*args, **kwargs)

    def validate_schema(self, value):
        """Validate value against the JSON schema."""
        if self.schema is None or value is None:
            return

        errors = []
        self._validate_node(value, self.schema, '', errors)

        if errors:
            raise ValidationError(errors)

    def _validate_node(self, value, schema, path, errors):
        """Recursively validate a value against a schema node."""
        schema_type = schema.get('type')

        # Type validation
        if schema_type:
            if not self._check_type(value, schema_type):
                errors.append(f"{path or 'root'}: Expected {schema_type}, got {type(value).__name__}")
                return

        # Object validation
        if schema_type == 'object' and isinstance(value, dict):
            # Check required fields
            required = schema.get('required', [])
            for req_field in required:
                if req_field not in value:
                    errors.append(f"{path}.{req_field}: Required field is missing")

            # Validate properties
            properties = schema.get('properties', {})
            for prop_name, prop_schema in properties.items():
                if prop_name in value:
                    prop_path = f"{path}.{prop_name}" if path else prop_name
                    self._validate_node(value[prop_name], prop_schema, prop_path, errors)

        # Array validation
        if schema_type == 'array' and isinstance(value, list):
            items_schema = schema.get('items')
            if items_schema:
                for i, item in enumerate(value):
                    item_path = f"{path}[{i}]"
                    self._validate_node(item, items_schema, item_path, errors)

            # Min/max items
            if 'minItems' in schema and len(value) < schema['minItems']:
                errors.append(f"{path}: Array has fewer than {schema['minItems']} items")
            if 'maxItems' in schema and len(value) > schema['maxItems']:
                errors.append(f"{path}: Array has more than {schema['maxItems']} items")

        # Number validation
        if schema_type in ('integer', 'number') and isinstance(value, (int, float)):
            if 'minimum' in schema and value < schema['minimum']:
                errors.append(f"{path}: Value {value} is less than minimum {schema['minimum']}")
            if 'maximum' in schema and value > schema['maximum']:
                errors.append(f"{path}: Value {value} is greater than maximum {schema['maximum']}")

        # String validation
        if schema_type == 'string' and isinstance(value, str):
            if 'minLength' in schema and len(value) < schema['minLength']:
                errors.append(f"{path}: String is shorter than {schema['minLength']} characters")
            if 'maxLength' in schema and len(value) > schema['maxLength']:
                errors.append(f"{path}: String is longer than {schema['maxLength']} characters")
            if 'pattern' in schema:
                import re
                if not re.match(schema['pattern'], value):
                    errors.append(f"{path}: String does not match pattern {schema['pattern']}")

        # Enum validation
        if 'enum' in schema and value not in schema['enum']:
            errors.append(f"{path}: Value must be one of {schema['enum']}")

    def _check_type(self, value, schema_type):
        """Check if value matches the schema type."""
        type_map = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict,
            'null': type(None),
        }

        if schema_type == 'integer' and isinstance(value, bool):
            return False

        expected = type_map.get(schema_type)
        if expected:
            return isinstance(value, expected)
        return True

    def validate(self, value, model_instance):
        """Validate the field value."""
        super().validate(value, model_instance)
        self.validate_schema(value)

    def deconstruct(self):
        """Return deconstructed field for migrations."""
        name, path, args, kwargs = super().deconstruct()
        if self.schema is not None:
            kwargs['schema'] = self.schema
        return name, path, args, kwargs
