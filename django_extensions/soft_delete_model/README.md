# Soft Delete Model

Soft deletion support for Django models - mark records as deleted without removing them.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.soft_delete_model',
]
```

## Usage

```python
from django.db import models
from django_extensions.soft_delete_model import SoftDeleteModel

class Article(SoftDeleteModel):
    title = models.CharField(max_length=200)

# Create and soft delete
article = Article.objects.create(title="Hello")
article.delete()  # Soft delete - sets is_deleted=True

# Queries exclude deleted by default
Article.objects.count()      # 0
Article.all_objects.count()  # 1

# Restore deleted objects
article.restore()
Article.objects.count()      # 1

# Hard delete (permanently remove)
article.hard_delete()
```

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `is_deleted` | `BooleanField` | Deletion flag (default: False) |
| `deleted_at` | `DateTimeField` | When deleted (nullable) |

## Managers

| Manager | Description |
|---------|-------------|
| `objects` | Excludes deleted records |
| `all_objects` | Includes all records |

## Methods

| Method | Description |
|--------|-------------|
| `delete()` | Soft delete the record |
| `restore()` | Restore a soft-deleted record |
| `hard_delete()` | Permanently delete from database |

## Queryset Methods

```python
# Filter deleted
Article.all_objects.deleted()      # Only deleted
Article.all_objects.not_deleted()  # Only active
```

## License

MIT
