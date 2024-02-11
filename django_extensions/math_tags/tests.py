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

    def test_square(self):
        """Test squaring."""
        assert power(5, 2) == 25


class TestPercentage:
    """Test cases for percentage filter."""

    def test_basic(self):
        """Test basic percentage."""
        assert percentage(25, 100) == 25.0

    def test_half(self):
        """Test 50%."""
        assert percentage(50, 100) == 50.0

    def test_division_by_zero(self):
        """Test division by zero returns 0."""
        assert percentage(10, 0) == 0


class TestAbsValue:
    """Test cases for abs_value filter."""

    def test_positive(self):
        """Test positive number unchanged."""
        assert abs_value(5) == 5

    def test_negative(self):
        """Test negative becomes positive."""
        assert abs_value(-5) == 5


class TestRoundNum:
    """Test cases for round_num filter."""

    def test_no_decimals(self):
        """Test rounding to integer."""
        assert round_num(3.7) == 4
        assert round_num(3.2) == 3

    def test_with_decimals(self):
        """Test rounding with decimals."""
        assert round_num(3.14159, 2) == 3.14


class TestFloor:
    """Test cases for floor filter."""

    def test_basic(self):
        """Test floor."""
        assert floor(3.7) == 3
        assert floor(3.2) == 3

    def test_negative(self):
        """Test negative floor."""
        assert floor(-3.2) == -4


class TestCeil:
    """Test cases for ceil filter."""

    def test_basic(self):
        """Test ceil."""
        assert ceil(3.2) == 4
        assert ceil(3.7) == 4

    def test_negative(self):
        """Test negative ceil."""
        assert ceil(-3.7) == -3


class TestMinValue:
    """Test cases for min_value filter."""

    def test_first_smaller(self):
        """Test when first value is smaller."""
        assert min_value(5, 10) == 5

    def test_second_smaller(self):
        """Test when second value is smaller."""
        assert min_value(10, 5) == 5


class TestMaxValue:
    """Test cases for max_value filter."""

    def test_first_larger(self):
        """Test when first value is larger."""
        assert max_value(10, 5) == 10

    def test_second_larger(self):
        """Test when second value is larger."""
        assert max_value(5, 10) == 10


class TestClamp:
    """Test cases for clamp filter."""

    def test_within_bounds(self):
        """Test value within bounds."""
        assert clamp(5, "0,10") == 5

    def test_below_min(self):
        """Test value below minimum."""
        assert clamp(-5, "0,10") == 0

    def test_above_max(self):
        """Test value above maximum."""
        assert clamp(15, "0,10") == 10


class TestSqrt:
    """Test cases for sqrt filter."""

    def test_perfect_square(self):
        """Test perfect square."""
        assert sqrt(16) == 4.0
        assert sqrt(25) == 5.0

    def test_non_perfect(self):
        """Test non-perfect square."""
        assert sqrt(2) == pytest.approx(1.414, rel=0.01)


class TestCalculate:
    """Test cases for calculate tag."""

    def test_addition(self):
        """Test addition expression."""
        assert calculate("2 + 3") == 5

    def test_multiplication(self):
        """Test multiplication expression."""
        assert calculate("4 * 5") == 20

    def test_order_of_operations(self):
        """Test order of operations."""
        assert calculate("2 + 3 * 4") == 14

    def test_parentheses(self):
        """Test parentheses."""
        assert calculate("(2 + 3) * 4") == 20

    def test_invalid_chars(self):
        """Test invalid characters rejected."""
        assert calculate("import os") == 'Invalid expression'

    def test_division(self):
        """Test division."""
        assert calculate("10 / 2") == 5.0
