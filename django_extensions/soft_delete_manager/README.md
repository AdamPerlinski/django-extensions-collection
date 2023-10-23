# Soft Delete Manager

Manager that filters out soft-deleted objects by default.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.soft_delete_manager',
]
```

## Usage

```python
from django.db import models
from django_extensions.soft_delete_manager import SoftDeleteManager

class Article(models.Model):
    title = models.CharField(max_length=200)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

# Regular queries exclude deleted
Article.objects.all()        # Only non-deleted
Article.all_objects.all()    # All including deleted

# Soft delete
article = Article.objects.get(pk=1)
article.is_deleted = True
article.deleted_at = timezone.now()
article.save()
```

## Manager Methods

```python
# Get only deleted objects
Article.objects.deleted()

# Get only non-deleted objects (default)
Article.objects.not_deleted()

# Include all objects in a query
Article.objects.with_deleted()
```

## Custom Delete Field

```python
class Article(models.Model):
    title = models.CharField(max_length=200)
    removed = models.BooleanField(default=False)

    objects = SoftDeleteManager(deleted_field='removed')
```

## Queryset Methods

```python
class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        """Soft delete all objects in queryset."""
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        """Permanently delete all objects."""
        return super().delete()

    def restore(self):
        """Restore all soft-deleted objects."""
        return self.update(is_deleted=False, deleted_at=None)
```

## License

MIT
