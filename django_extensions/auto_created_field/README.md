# Auto Created Field

DateTimeField that automatically sets on model creation.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.auto_created_field',
]
```

## Usage

```python
from django.db import models
from django_extensions.auto_created_field import AutoCreatedField

class Article(models.Model):
    title = models.CharField(max_length=200)
    created = AutoCreatedField()

article = Article.objects.create(title="Hello")
print(article.created)  # 2024-01-15 10:30:00.123456

# Field is immutable after creation
article.created = timezone.now()  # This will be ignored on save
article.save()
```

## Comparison with auto_now_add

| Feature | AutoCreatedField | auto_now_add=True |
|---------|-----------------|-------------------|
| Set on create | Yes | Yes |
| Editable | No | No |
| Customizable | Yes | Limited |
| Timezone aware | Yes | Yes |

## API

```python
class AutoCreatedField(models.DateTimeField):
    """
    A DateTimeField that automatically sets its value to the current
    datetime when the model is first created.
    """
```

## Options

```python
# Custom default timezone
created = AutoCreatedField(default=timezone.now)

# With database index
created = AutoCreatedField(db_index=True)
```

## License

MIT
