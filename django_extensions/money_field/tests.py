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
        m1 = Money(100, 'USD')
        m2 = Money(100, 'USD')
        assert hash(m1) == hash(m2)

    def test_addition(self):
        """Test addition."""
        m1 = Money(100, 'USD')
        m2 = Money(50, 'USD')
        result = m1 + m2
        assert result.amount == Decimal('150')
        assert result.currency == 'USD'

    def test_addition_different_currency(self):
        """Test addition with different currencies raises error."""
        m1 = Money(100, 'USD')
        m2 = Money(50, 'EUR')
        with pytest.raises(ValueError):
            m1 + m2

    def test_subtraction(self):
        """Test subtraction."""
        m1 = Money(100, 'USD')
        m2 = Money(30, 'USD')
        result = m1 - m2
        assert result.amount == Decimal('70')

    def test_multiplication(self):
        """Test multiplication."""
        m = Money(100, 'USD')
        result = m * 2
        assert result.amount == Decimal('200')

    def test_division(self):
        """Test division."""
        m = Money(100, 'USD')
        result = m / 4
        assert result.amount == Decimal('25')

    def test_comparison(self):
        """Test comparison operators."""
        m1 = Money(100, 'USD')
        m2 = Money(50, 'USD')

        assert m1 > m2
        assert m2 < m1
        assert m1 >= m1
        assert m1 <= m1

    def test_negation(self):
        """Test negation."""
        m = Money(100, 'USD')
        neg = -m
        assert neg.amount == Decimal('-100')

    def test_abs(self):
        """Test absolute value."""
        m = Money(-100, 'USD')
        result = abs(m)
        assert result.amount == Decimal('100')

    def test_bool(self):
        """Test boolean conversion."""
        assert bool(Money(100, 'USD')) is True
        assert bool(Money(0, 'USD')) is False

    def test_round(self):
        """Test rounding."""
        m = Money('99.999', 'USD')
        result = m.round(2)
        assert result.amount == Decimal('100.00')

    def test_is_positive(self):
        """Test is_positive property."""
        assert Money(100, 'USD').is_positive is True
        assert Money(-100, 'USD').is_positive is False
        assert Money(0, 'USD').is_positive is False

    def test_is_negative(self):
        """Test is_negative property."""
        assert Money(-100, 'USD').is_negative is True
        assert Money(100, 'USD').is_negative is False

    def test_is_zero(self):
        """Test is_zero property."""
        assert Money(0, 'USD').is_zero is True
        assert Money(100, 'USD').is_zero is False


class TestMoneyField:
    """Test cases for MoneyField."""

    def test_is_decimal_field(self):
        """Test MoneyField is a DecimalField."""
        field = MoneyField()
        assert isinstance(field, models.DecimalField)

    def test_default_currency(self):
        """Test default currency is USD."""
        field = MoneyField()
        assert field.default_currency == 'USD'

    def test_custom_default_currency(self):
        """Test custom default currency."""
        field = MoneyField(default_currency='EUR')
        assert field.default_currency == 'EUR'

    def test_save_and_retrieve(self, create_tables):
        """Test saving and retrieving money values."""
        obj = ConcreteMoneyModel.objects.create(
            name='test',
            price=Decimal('99.99')
        )
        obj.refresh_from_db()
        assert obj.price == Decimal('99.99')

    def test_currency_field_created(self, create_tables):
        """Test currency field is automatically created."""
        assert hasattr(ConcreteMoneyModel, 'price_currency')

    def test_money_property(self, create_tables):
        """Test money property getter."""
        obj = ConcreteMoneyModel.objects.create(
            name='test',
            price=Decimal('99.99')
        )
        money = obj.price_money
        assert isinstance(money, Money)
        assert money.amount == Decimal('99.99')

    def test_deconstruct(self):
        """Test field deconstruction."""
        field = MoneyField(default_currency='EUR')
        name, path, args, kwargs = field.deconstruct()
        assert kwargs.get('default_currency') == 'EUR'
