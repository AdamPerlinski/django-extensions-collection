"""Tests for MoneyField and Money class."""

import pytest
from decimal import Decimal
from django.db import models

from .fields import MoneyField, Money


class ConcreteMoneyModel(models.Model):
    """Concrete model for testing."""
    price = MoneyField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'money_field'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteMoneyModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteMoneyModel)
        except Exception:
            pass


class TestMoney:
    """Test cases for Money class."""

    def test_creation_with_decimal(self):
        """Test Money creation with Decimal."""
        m = Money(Decimal('99.99'), 'USD')
        assert m.amount == Decimal('99.99')
        assert m.currency == 'USD'

    def test_creation_with_float(self):
        """Test Money creation with float."""
        m = Money(99.99, 'USD')
        assert m.amount == Decimal('99.99')

    def test_creation_with_int(self):
        """Test Money creation with int."""
        m = Money(100, 'USD')
        assert m.amount == Decimal('100')

    def test_creation_with_string(self):
        """Test Money creation with string."""
        m = Money('99.99', 'USD')
        assert m.amount == Decimal('99.99')

    def test_currency_uppercase(self):
        """Test currency is uppercased."""
        m = Money(100, 'usd')
        assert m.currency == 'USD'

    def test_str(self):
        """Test string representation."""
        m = Money(99.99, 'USD')
        assert str(m) == 'USD 99.99'

    def test_repr(self):
        """Test repr."""
        m = Money(Decimal('99.99'), 'USD')
        assert "Money" in repr(m)
        assert "99.99" in repr(m)

    def test_equality(self):
        """Test equality comparison."""
        m1 = Money(100, 'USD')
        m2 = Money(100, 'USD')
        m3 = Money(100, 'EUR')
        m4 = Money(50, 'USD')

        assert m1 == m2
        assert m1 != m3
        assert m1 != m4

    def test_hash(self):
        """Test Money is hashable."""
