# Ordered Model

Maintain explicit ordering of model instances with move operations.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.ordered_model',
]
```

## Usage

```python
from django.db import models
from django_extensions.ordered_model import OrderedModel

class Task(OrderedModel):
    title = models.CharField(max_length=200)

# Create items (order auto-assigned)
task1 = Task.objects.create(title="First")   # order=0
task2 = Task.objects.create(title="Second")  # order=1
task3 = Task.objects.create(title="Third")   # order=2

# Move operations
task3.move_up()     # Now order=1
task1.move_down()   # Now order=1
task2.move_to(0)    # Now order=0

# Swap positions
task1.swap(task3)

# Get ordered queryset
Task.objects.ordered()  # Returns queryset ordered by 'order' field
```

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `order` | `PositiveIntegerField` | Position in sequence |

## Methods

| Method | Description |
|--------|-------------|
| `move_up()` | Move one position up (lower order) |
| `move_down()` | Move one position down (higher order) |
| `move_to(position)` | Move to specific position |
| `swap(other)` | Swap position with another instance |
| `save()` | Auto-assigns order if not set |

## Queryset Methods

```python
Task.objects.ordered()      # Order by 'order' field
Task.objects.max_order()    # Get highest order value
```

## Scoped Ordering

For ordering within a category:

```python
class Task(OrderedModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)

    class Meta:
        ordering = ['category', 'order']
```

## License

MIT
