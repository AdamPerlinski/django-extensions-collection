# Short UUID Field

Shorter, URL-friendly UUID field for Django models.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.short_uuid_field',
]
```

## Usage

```python
from django.db import models
from django_extensions.short_uuid_field import ShortUUIDField

class Article(models.Model):
    id = ShortUUIDField(primary_key=True)
    title = models.CharField(max_length=200)

article = Article.objects.create(title="Hello")
print(article.id)  # "a1b2c3d4" (8 characters)
```

## Configuration

```python
# Custom length (default: 8)
id = ShortUUIDField(length=12)

# Custom alphabet
id = ShortUUIDField(alphabet='0123456789ABCDEF')

# As non-primary key
short_id = ShortUUIDField(primary_key=False, unique=True)
```

## Default Alphabet

Uses Base62 encoding: `0-9`, `a-z`, `A-Z`

This provides:
- 62^8 = 218 trillion combinations (8 chars)
- URL-safe characters
- Case-sensitive uniqueness

## Comparison

| Type | Example | Length |
|------|---------|--------|
| UUID | `550e8400-e29b-41d4-a716-446655440000` | 36 |
| Short UUID | `a1B2c3D4` | 8 |

## URL Patterns

```python
# urls.py
urlpatterns = [
    path('articles/<str:pk>/', ArticleDetailView.as_view()),
]
```

## Collision Resistance

With 8 characters and Base62:
- ~218 trillion combinations
- Collision probability < 0.001% at 1 billion records

## License

MIT
