"""
Math template tags - Perform mathematical operations in templates.

Usage:
    {% load math_ext %}

    {{ value|add:10 }}
    {{ value|multiply:2 }}
    {{ value|divide:3 }}
    {{ value|percentage:total }}
"""

from django import template
from decimal import Decimal, InvalidOperation
import math

register = template.Library()


@register.filter
def add(value, arg):
    """
    Add a number to the value.

    Usage: {{ 5|add:3 }} -> 8
    """
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return value


@register.filter
def subtract(value, arg):
    """
    Subtract a number from the value.

    Usage: {{ 10|subtract:3 }} -> 7
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value


@register.filter
def multiply(value, arg):
    """
    Multiply the value by a number.

    Usage: {{ 5|multiply:3 }} -> 15
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value


@register.filter
def divide(value, arg):
    """
    Divide the value by a number.

    Usage: {{ 10|divide:2 }} -> 5.0
    """
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return value


@register.filter
def modulo(value, arg):
    """
    Return the remainder of division.

    Usage: {{ 10|modulo:3 }} -> 1
    """
    try:
        return int(value) % int(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return value


@register.filter
def power(value, arg):
    """
    Raise value to a power.

    Usage: {{ 2|power:3 }} -> 8
    """
    try:
        return float(value) ** float(arg)
    except (ValueError, TypeError):
        return value


@register.filter
def percentage(value, total):
    """
    Calculate percentage of value relative to total.

    Usage: {{ 25|percentage:100 }} -> 25.0
    """
    try:
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def abs_value(value):
    """
    Return absolute value.

    Usage: {{ -5|abs_value }} -> 5
    """
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return value


@register.filter
def round_num(value, places=0):
    """
    Round to specified decimal places.

    Usage: {{ 3.14159|round_num:2 }} -> 3.14
    """
    try:
        if places == 0:
            return int(round(float(value)))
        return round(float(value), int(places))
    except (ValueError, TypeError):
        return value


@register.filter
def floor(value):
    """
    Round down to nearest integer.

    Usage: {{ 3.7|floor }} -> 3
    """
    try:
        return math.floor(float(value))
    except (ValueError, TypeError):
        return value


@register.filter
def ceil(value):
    """
    Round up to nearest integer.

    Usage: {{ 3.2|ceil }} -> 4
    """
    try:
        return math.ceil(float(value))
    except (ValueError, TypeError):
        return value


@register.filter
def min_value(value, arg):
    """
    Return the minimum of value and arg.

    Usage: {{ 10|min_value:5 }} -> 5
    """
    try:
        return min(float(value), float(arg))
    except (ValueError, TypeError):
        return value


@register.filter
def max_value(value, arg):
    """
    Return the maximum of value and arg.

    Usage: {{ 10|max_value:15 }} -> 15
    """
    try:
        return max(float(value), float(arg))
    except (ValueError, TypeError):
        return value


@register.filter
def clamp(value, bounds):
    """
    Clamp value between min and max.

    Usage: {{ 15|clamp:"0,10" }} -> 10
    """
    try:
        min_val, max_val = bounds.split(',')
        val = float(value)
        return max(float(min_val), min(float(max_val), val))
    except (ValueError, TypeError, AttributeError):
        return value


@register.filter
def sqrt(value):
    """
    Calculate square root.

    Usage: {{ 16|sqrt }} -> 4.0
    """
    try:
        return math.sqrt(float(value))
    except (ValueError, TypeError):
        return value


@register.simple_tag
def calculate(expression):
    """
    Evaluate a simple math expression.

    Usage: {% calculate "2 + 3 * 4" %}

    Note: Only supports basic operators for safety.
    """
    # Only allow safe characters
    allowed = set('0123456789+-*/.() ')
    if not all(c in allowed for c in expression):
        return 'Invalid expression'

    try:
        # Use eval with restricted globals for safety
        result = eval(expression, {"__builtins__": {}}, {})
        return result
    except Exception:
        return 'Error'
