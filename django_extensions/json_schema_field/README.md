# JSON Schema Field

JSONField with JSON Schema validation.

## Installation

```bash
pip install jsonschema
```

```python
INSTALLED_APPS = [
    'django_extensions.json_schema_field',
]
```

## Usage

```python
from django.db import models
from django_extensions.json_schema_field import JSONSchemaField

class Product(models.Model):
    name = models.CharField(max_length=200)
    attributes = JSONSchemaField(schema={
        "type": "object",
        "properties": {
            "color": {"type": "string"},
            "size": {"type": "string", "enum": ["S", "M", "L", "XL"]},
            "weight": {"type": "number", "minimum": 0}
        },
        "required": ["color", "size"]
    })

# Valid data
product = Product.objects.create(
    name="T-Shirt",
    attributes={"color": "blue", "size": "M", "weight": 0.3}
)

# Invalid data raises ValidationError
Product.objects.create(
    name="T-Shirt",
    attributes={"color": "blue"}  # Missing required 'size'
)
# ValidationError: 'size' is a required property
```

## Schema Definition

Uses JSON Schema Draft 7:

```python
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "age": {"type": "integer", "minimum": 0},
        "email": {"type": "string", "format": "email"},
        "tags": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["name", "email"],
    "additionalProperties": False
}
```

## Validation Types

| Type | Description |
|------|-------------|
| `string` | Text values |
| `integer` | Whole numbers |
| `number` | Decimal numbers |
| `boolean` | True/False |
| `array` | Lists |
| `object` | Nested objects |
| `null` | Null values |

## Common Constraints

```python
{
    "type": "string",
    "minLength": 1,
    "maxLength": 100,
    "pattern": "^[a-z]+$"
}

{
    "type": "number",
    "minimum": 0,
    "maximum": 100,
    "multipleOf": 0.01
}

{
    "type": "array",
    "minItems": 1,
    "maxItems": 10,
    "uniqueItems": True
}
```

## License

MIT
