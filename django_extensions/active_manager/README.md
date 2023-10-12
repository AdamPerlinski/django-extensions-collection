# Active Manager

Manager that filters objects by is_active field.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.active_manager',
]
```

## Usage

```python
from django.db import models
from django_extensions.active_manager import ActiveManager

class User(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active = ActiveManager()

# Filter active users
User.active.all()     # Only is_active=True
User.objects.all()    # All users
```

## Custom Field Name

```python
class Product(models.Model):
    name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)

    objects = models.Manager()
    active = ActiveManager(active_field='enabled')

Product.active.all()  # Only enabled=True
```

## As Default Manager

```python
class User(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    objects = ActiveManager()
    all_objects = models.Manager()

# Default queries return only active
User.objects.all()        # Only active
User.all_objects.all()    # All users
```

## Manager Methods

```python
# Get inactive objects
User.active.inactive()

# Toggle active status
user = User.objects.get(pk=1)
user.is_active = not user.is_active
user.save()
```

## License

MIT
