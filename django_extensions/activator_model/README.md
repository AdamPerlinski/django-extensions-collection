# Activator Model

Date-based activation/deactivation for time-limited content.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.activator_model',
]
```

## Usage

```python
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django_extensions.activator_model import ActivatorModel

class Promotion(ActivatorModel):
    name = models.CharField(max_length=200)
    discount = models.IntegerField()

# Create with date range
promo = Promotion.objects.create(
    name="Summer Sale",
    discount=20,
    activate_date=timezone.now(),
    deactivate_date=timezone.now() + timedelta(days=30)
)

# Check if active
promo.is_active  # True (within date range)

# Filter active items
Promotion.objects.active()   # Currently active
Promotion.objects.inactive() # Not yet active or expired
```

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `activate_date` | `DateTimeField` | When to start (nullable) |
| `deactivate_date` | `DateTimeField` | When to end (nullable) |

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `is_active` | `bool` | True if currently within date range |

## Manager Methods

```python
# Get all currently active
Promotion.objects.active()

# Get inactive (not started or expired)
Promotion.objects.inactive()

# Get upcoming (not yet started)
Promotion.objects.upcoming()

# Get expired
Promotion.objects.expired()
```

## Logic

An item is considered active when:
- `activate_date` is null OR `activate_date <= now`
- AND `deactivate_date` is null OR `deactivate_date > now`

## Examples

```python
# Always active (no dates set)
Promotion.objects.create(name="Evergreen", discount=10)

# Active from specific date
Promotion.objects.create(
    name="Future Sale",
    discount=15,
    activate_date=timezone.now() + timedelta(days=7)
)

# Active until specific date
Promotion.objects.create(
    name="Limited Time",
    discount=25,
    deactivate_date=timezone.now() + timedelta(hours=24)
)
```

## License

MIT
