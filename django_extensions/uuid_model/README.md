# UUID Model

UUID primary key with short ID support for Django models.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.uuid_model',
]
```

## Usage

```python
from django.db import models
from django_extensions.uuid_model import UUIDModel

class Article(UUIDModel):
    title = models.CharField(max_length=200)

article = Article.objects.create(title="Hello")
print(article.id)        # 550e8400-e29b-41d4-a716-446655440000
print(article.short_id)  # 550e8400
```

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUIDField` | Primary key, auto-generated |

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `short_id` | `str` | First 8 characters of UUID |

## API

### UUIDModel

```python
class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    @property
    def short_id(self):
        return str(self.id)[:8]

    class Meta:
        abstract = True
```

## Benefits

- **No ID enumeration**: UUIDs prevent sequential ID guessing
- **Distributed systems**: Generate IDs without database coordination
- **Merge-friendly**: No conflicts when merging databases

## License

MIT
