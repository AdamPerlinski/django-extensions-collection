"""Tests for math template tags."""

import pytest
import math

from .templatetags import (
    add,
    subtract,
    multiply,
    divide,
    modulo,
    power,
    percentage,
    abs_value,
    round_num,
    floor,
    ceil,
    min_value,
    max_value,
    clamp,
    sqrt,
    calculate,
)


class TestAdd:
    """Test cases for add filter."""

    def test_integers(self):
        """Test adding integers."""
        assert add(5, 3) == 8

    def test_floats(self):
        """Test adding floats."""
        assert add(2.5, 1.5) == 4.0

    def test_invalid(self):
        """Test invalid input."""
        assert add('invalid', 5) == 'invalid'


class TestSubtract:
    """Test cases for subtract filter."""

    def test_basic(self):
        """Test basic subtraction."""
        assert subtract(10, 3) == 7

    def test_negative_result(self):
        """Test negative result."""
        assert subtract(3, 10) == -7


class TestMultiply:
    """Test cases for multiply filter."""

    def test_basic(self):
        """Test basic multiplication."""
        assert multiply(5, 3) == 15

    def test_floats(self):
        """Test float multiplication."""
        assert multiply(2.5, 4) == 10.0


class TestDivide:
    """Test cases for divide filter."""

    def test_basic(self):
        """Test basic division."""
        assert divide(10, 2) == 5.0

    def test_float_result(self):
        """Test float result."""
        assert divide(10, 3) == pytest.approx(3.333, rel=0.01)

    def test_division_by_zero(self):
        """Test division by zero returns original value."""
        assert divide(10, 0) == 10


class TestModulo:
    """Test cases for modulo filter."""

    def test_basic(self):
        """Test basic modulo."""
        assert modulo(10, 3) == 1

    def test_no_remainder(self):
        """Test no remainder."""
        assert modulo(10, 5) == 0


class TestPower:
    """Test cases for power filter."""

    def test_basic(self):
        """Test basic power."""
        assert power(2, 3) == 8

