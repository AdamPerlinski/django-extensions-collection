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

