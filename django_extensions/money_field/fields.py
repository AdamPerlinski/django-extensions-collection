"""
MoneyField - Field for handling monetary values with currency.

Usage:
    from django_extensions.money_field import MoneyField, Money

    class Product(models.Model):
        price = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')

    product.price = Money(99.99, 'USD')
    product.price.amount  # Decimal('99.99')
    product.price.currency  # 'USD'
"""

from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from django.db import models


class Money:
    """Represents a monetary value with currency."""

    def __init__(self, amount, currency='USD'):
        if isinstance(amount, str):
            try:
                amount = Decimal(amount)
            except InvalidOperation:
                raise ValueError(f"Invalid amount: {amount}")
        elif isinstance(amount, float):
            amount = Decimal(str(amount))
        elif isinstance(amount, int):
            amount = Decimal(amount)
        elif not isinstance(amount, Decimal):
            raise TypeError(f"Amount must be a number, got {type(amount)}")

        self.amount = amount
        self.currency = currency.upper()

    def __str__(self):
        return f"{self.currency} {self.amount:.2f}"

    def __repr__(self):
        return f"Money({self.amount!r}, {self.currency!r})"

    def __eq__(self, other):
        if isinstance(other, Money):
            return self.amount == other.amount and self.currency == other.currency
        return False

    def __hash__(self):
        return hash((self.amount, self.currency))

    def __add__(self, other):
        if isinstance(other, Money):
            if self.currency != other.currency:
                raise ValueError(f"Cannot add {self.currency} and {other.currency}")
            return Money(self.amount + other.amount, self.currency)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Money):
            if self.currency != other.currency:
                raise ValueError(f"Cannot subtract {self.currency} and {other.currency}")
            return Money(self.amount - other.amount, self.currency)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float, Decimal)):
            return Money(self.amount * Decimal(str(other)), self.currency)
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (int, float, Decimal)):
            return Money(self.amount / Decimal(str(other)), self.currency)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Money):
            if self.currency != other.currency:
                raise ValueError(f"Cannot compare {self.currency} and {other.currency}")
            return self.amount < other.amount
        return NotImplemented

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        if isinstance(other, Money):
            if self.currency != other.currency:
                raise ValueError(f"Cannot compare {self.currency} and {other.currency}")
            return self.amount > other.amount
        return NotImplemented

    def __ge__(self, other):
        return self == other or self > other

    def __neg__(self):
        return Money(-self.amount, self.currency)

    def __abs__(self):
        return Money(abs(self.amount), self.currency)

    def __bool__(self):
        return self.amount != 0

    def round(self, decimal_places=2):
        """Round the amount to specified decimal places."""
        return Money(round(self.amount, decimal_places), self.currency)

    @property
    def is_positive(self):
        return self.amount > 0

    @property
    def is_negative(self):
        return self.amount < 0

    @property
    def is_zero(self):
        return self.amount == 0


class MoneyField(models.DecimalField):
    """
    A DecimalField that stores monetary values with currency support.
    Currency is stored in a separate field.
    """

    def __init__(self, *args, default_currency='USD', **kwargs):
        self.default_currency = default_currency
        kwargs.setdefault('max_digits', 19)
        kwargs.setdefault('decimal_places', 4)
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super().contribute_to_class(cls, name)

        # Add currency field
        currency_field_name = f'{name}_currency'
        if not hasattr(cls, currency_field_name):
            currency_field = models.CharField(
                max_length=3,
                default=self.default_currency,
                help_text=f"Currency for {name}"
            )
            currency_field.contribute_to_class(cls, currency_field_name)

        # Add property to get Money object
        def get_money(instance):
            amount = getattr(instance, name)
            currency = getattr(instance, currency_field_name)
            if amount is None:
                return None
            return Money(amount, currency)

        def set_money(instance, value):
            if value is None:
                setattr(instance, name, None)
            elif isinstance(value, Money):
                setattr(instance, name, value.amount)
                setattr(instance, currency_field_name, value.currency)
            else:
                setattr(instance, name, value)

        setattr(cls, f'{name}_money', property(get_money, set_money))

    def deconstruct(self):
        """Return deconstructed field for migrations."""
        name, path, args, kwargs = super().deconstruct()
        if self.default_currency != 'USD':
            kwargs['default_currency'] = self.default_currency
        return name, path, args, kwargs
