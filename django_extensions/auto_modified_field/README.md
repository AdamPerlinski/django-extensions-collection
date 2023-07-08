# Auto Modified Field

DateTimeField that automatically updates on every save.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.auto_modified_field',
]
```

## Usage

```python
from django.db import models
from django_extensions.auto_modified_field import AutoModifiedField

class Article(models.Model):
    title = models.CharField(max_length=200)
    modified = AutoModifiedField()

article = Article.objects.create(title="Hello")
print(article.modified)  # 2024-01-15 10:30:00

# Automatically updates on save
article.title = "Updated"
article.save()
print(article.modified)  # 2024-01-15 11:00:00
```

## Comparison with auto_now

| Feature | AutoModifiedField | auto_now=True |
|---------|------------------|---------------|
| Update on save | Yes | Yes |
| Editable | No | No |
| Skip update option | Yes | No |
| Timezone aware | Yes | Yes |

## API

```python
class AutoModifiedField(models.DateTimeField):
    """
    A DateTimeField that automatically sets its value to the current
    datetime every time the model is saved.
    """
```

## Skip Update

```python
# Skip timestamp update for specific save
article.save(update_fields=['title'])  # modified not updated
```

## Combining Fields

```python
from django_extensions.auto_created_field import AutoCreatedField
from django_extensions.auto_modified_field import AutoModifiedField

class Article(models.Model):
    title = models.CharField(max_length=200)
    created = AutoCreatedField()
    modified = AutoModifiedField()
```

## License

MIT
