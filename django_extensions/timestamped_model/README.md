# TimeStamped Model

Auto-managed `created` and `modified` timestamp fields for Django models.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.timestamped_model',
]
```

## Usage

```python
from django.db import models
from django_extensions.timestamped_model import TimeStampedModel

class Article(TimeStampedModel):
    title = models.CharField(max_length=200)
    content = models.TextField()

# Fields are automatically managed
article = Article.objects.create(title="Hello", content="World")
print(article.created)   # 2024-01-15 10:30:00
print(article.modified)  # 2024-01-15 10:30:00

article.title = "Updated"
article.save()
print(article.modified)  # 2024-01-15 11:00:00 (auto-updated)
```

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `created` | `DateTimeField` | Set once on creation, never changes |
| `modified` | `DateTimeField` | Updated on every save |

## API

### TimeStampedModel

Abstract base model with timestamp fields.

```python
class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

## Combining with Other Mixins

```python
from django_extensions.timestamped_model import TimeStampedModel
from django_extensions.uuid_model import UUIDModel
from django_extensions.soft_delete_model import SoftDeleteModel

class MyModel(TimeStampedModel, UUIDModel, SoftDeleteModel):
    name = models.CharField(max_length=100)
```

## License

MIT
