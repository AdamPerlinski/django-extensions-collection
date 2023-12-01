"""
ColorValidator - Validator for color codes (hex, rgb, rgba, hsl).

Usage:
    from django_extensions.color_validator import ColorValidator

    class Theme(models.Model):
        primary_color = models.CharField(
            max_length=25,
            validators=[ColorValidator()]
        )
"""

import re
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


# Color format patterns
COLOR_PATTERNS = {
    'hex3': r'^#([0-9a-fA-F]{3})$',
    'hex6': r'^#([0-9a-fA-F]{6})$',
    'hex8': r'^#([0-9a-fA-F]{8})$',  # With alpha
    'rgb': r'^rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$',
    'rgba': r'^rgba\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(0|1|0?\.\d+)\s*\)$',
    'hsl': r'^hsl\(\s*(\d{1,3})\s*,\s*(\d{1,3})%\s*,\s*(\d{1,3})%\s*\)$',
    'hsla': r'^hsla\(\s*(\d{1,3})\s*,\s*(\d{1,3})%\s*,\s*(\d{1,3})%\s*,\s*(0|1|0?\.\d+)\s*\)$',
}

# Named colors
NAMED_COLORS = {
    'black', 'white', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta',
    'gray', 'grey', 'orange', 'pink', 'purple', 'brown', 'navy', 'teal',
    'olive', 'maroon', 'aqua', 'fuchsia', 'lime', 'silver',
}


def get_color_format(value):
    """
    Determine the format of a color value.

    Returns:
        The format name ('hex3', 'hex6', 'rgb', etc.) or 'named' or None.
    """
    if not value:
        return None

    value = str(value).strip().lower()

    if value in NAMED_COLORS:
        return 'named'

    for format_name, pattern in COLOR_PATTERNS.items():
        if re.match(pattern, value, re.IGNORECASE):
            return format_name

    return None


def normalize_color(value):
    """
    Normalize a color value to lowercase hex format.

    Args:
        value: A color value in any supported format.

    Returns:
        Normalized hex color string, or None if invalid.
    """
    if not value:
        return None

    value = str(value).strip().lower()
    color_format = get_color_format(value)

    if color_format == 'hex6':
        return value.lower()
