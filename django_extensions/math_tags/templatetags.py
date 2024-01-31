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

