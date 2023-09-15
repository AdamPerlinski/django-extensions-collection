# Money Field

Currency-aware money storage for Django models.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.money_field',
]
```

## Usage

```python
from django.db import models
from django_extensions.money_field import MoneyField

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')

product = Product.objects.create(name="Widget", price=19.99)
print(product.price)           # Decimal('19.99')
print(product.price_currency)  # 'USD'
```

## Fields Created

MoneyField creates two database columns:

| Field | Type | Description |
|-------|------|-------------|
| `<name>` | `DecimalField` | Amount value |
| `<name>_currency` | `CharField(3)` | ISO 4217 currency code |

## Configuration

```python
# With specific currency
price = MoneyField(
    max_digits=10,
    decimal_places=2,
    default_currency='EUR'
)

# Multi-currency support
price = MoneyField(
    max_digits=10,
    decimal_places=2,
    currency_choices=[
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
    ]
)
```

## Formatting

```python
from django_extensions.money_field import format_money

product = Product.objects.get(pk=1)
formatted = format_money(product.price, product.price_currency)
print(formatted)  # "$19.99"
```

## Arithmetic

```python
from decimal import Decimal

product.price += Decimal('5.00')
product.save()
```

## Template Usage

```django
{{ product.price|format_money:product.price_currency }}
```

## Supported Currencies

ISO 4217 currency codes: USD, EUR, GBP, JPY, CAD, AUD, CHF, CNY, etc.

## License

MIT
