# Title Slug Model

Combined title, slug, and description fields for content models.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.title_slug_model',
]
```

## Usage

```python
from django.db import models
from django_extensions.title_slug_model import TitleSlugModel

class Article(TitleSlugModel):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)

article = Article.objects.create(
    title="Getting Started with Django",
    description="A beginner's guide to Django web framework",
    content="...",
    author=user
)

print(article.slug)  # "getting-started-with-django"
print(article.title)
print(article.description)
```

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | `CharField(255)` | Main title |
| `slug` | `SlugField` | URL-safe identifier (auto-generated) |
| `description` | `TextField` | Optional description (blank allowed) |

## Auto-Generated Slugs

Slugs are automatically generated from the title:

```python
article = Article(title="Hello World!")
article.save()
print(article.slug)  # "hello-world"
```

## URL Patterns

```python
# urls.py
from django.urls import path

urlpatterns = [
    path('articles/<slug:slug>/', ArticleDetailView.as_view()),
]
```

## Admin Integration

```python
from django.contrib import admin

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'created']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'description']
```

## Combining with Other Mixins

```python
from django_extensions.title_slug_model import TitleSlugModel
from django_extensions.timestamped_model import TimeStampedModel

class Article(TitleSlugModel, TimeStampedModel):
    content = models.TextField()

# Now has: title, slug, description, created, modified
```

## License

MIT
