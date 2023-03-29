# Status Model

Status field with state machine transitions for Django models.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.status_model',
]
```

## Usage

```python
from django.db import models
from django_extensions.status_model import StatusModel

class Order(StatusModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.CharField(max_length=200)

order = Order.objects.create(customer="John", status='pending')

# Check status
order.is_pending      # True
order.is_processing   # False

# Change status
order.set_status('processing')
order.status_changed_at  # Timestamp of last change

# Filter by status
Order.objects.filter(status='pending')
Order.objects.pending()  # If using StatusQuerySet
```

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | `CharField` | Current status |
| `status_changed_at` | `DateTimeField` | Last status change time |

## Dynamic Properties

For each status choice, a property `is_<status>` is available:

```python
order.is_pending     # True if status == 'pending'
order.is_processing  # True if status == 'processing'
```

## Methods

| Method | Description |
|--------|-------------|
| `set_status(status)` | Change status and update timestamp |
| `get_status_display()` | Human-readable status name |

## Status Transitions

Define allowed transitions:

```python
class Order(StatusModel):
    TRANSITIONS = {
        'pending': ['processing', 'cancelled'],
        'processing': ['shipped', 'cancelled'],
        'shipped': ['delivered'],
    }

    def set_status(self, new_status):
        allowed = self.TRANSITIONS.get(self.status, [])
        if new_status not in allowed:
            raise ValueError(f"Cannot transition from {self.status} to {new_status}")
        super().set_status(new_status)
```

## License

MIT
