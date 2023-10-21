# Random Manager

Manager for random object selection.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.random_manager',
]
```

## Usage

```python
from django.db import models
from django_extensions.random_manager import RandomManager

class Quote(models.Model):
    text = models.TextField()
    author = models.CharField(max_length=100)

    objects = RandomManager()

# Get random quote
quote = Quote.objects.random()

# Get multiple random quotes
quotes = Quote.objects.random(count=5)

# Random from filtered queryset
inspirational = Quote.objects.filter(category='inspiration').random()
```

## Methods

| Method | Description |
|--------|-------------|
| `random()` | Get one random object |
| `random(count=n)` | Get n random objects |
| `random_queryset()` | Get queryset in random order |

## Performance

For large tables, random selection is optimized:

```python
# Efficient random selection using database-specific methods
Quote.objects.random()  # Uses ORDER BY RANDOM() LIMIT 1
```

## Random with Weights

```python
class WeightedQuote(models.Model):
    text = models.TextField()
    weight = models.IntegerField(default=1)

    objects = RandomManager()

# Higher weight = higher probability
quote = WeightedQuote.objects.weighted_random(weight_field='weight')
```

## Database Support

- **PostgreSQL**: `ORDER BY RANDOM()`
- **MySQL**: `ORDER BY RAND()`
- **SQLite**: `ORDER BY RANDOM()`

## License

MIT
