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
