# Slugged Model

Auto-generated URL-safe slugs from a source field.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.slugged_model',
]
```

## Usage

```python
from django.db import models
from django_extensions.slugged_model import SluggedModel

class Article(SluggedModel):
    title = models.CharField(max_length=200)

    # Specify which field to generate slug from
    slug_source_field = 'title'

article = Article.objects.create(title="Hello World!")
print(article.slug)  # "hello-world"

# Duplicate titles get unique slugs
article2 = Article.objects.create(title="Hello World!")
print(article2.slug)  # "hello-world-1"
```

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `slug` | `SlugField` | URL-safe identifier |

## Configuration

```python
class Article(SluggedModel):
    title = models.CharField(max_length=200)

    # Required: field to generate slug from
    slug_source_field = 'title'

    # Optional: max length (default: 50)
    slug_max_length = 100

    # Optional: allow blank slugs (default: False)
    slug_allow_blank = False
```

## Unique Slugs

The model automatically handles duplicate slugs by appending numbers:

```
hello-world
hello-world-1
hello-world-2
```

## URL Patterns

```python
# urls.py
urlpatterns = [
    path('articles/<slug:slug>/', ArticleDetailView.as_view()),
]

# views.py
class ArticleDetailView(DetailView):
    model = Article
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
```

## Manual Slug Override

```python
article = Article.objects.create(
    title="Hello World!",
    slug="custom-slug"  # Uses provided slug instead of generating
)
```

## License

MIT
