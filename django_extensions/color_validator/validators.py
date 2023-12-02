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

    if color_format == 'hex3':
        # Expand #RGB to #RRGGBB
        hex_val = value[1:]
        return f'#{hex_val[0]*2}{hex_val[1]*2}{hex_val[2]*2}'

    if color_format == 'hex8':
        return value.lower()

    if color_format == 'rgb':
        match = re.match(COLOR_PATTERNS['rgb'], value, re.IGNORECASE)
        if match:
            r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
            if all(0 <= c <= 255 for c in (r, g, b)):
                return f'#{r:02x}{g:02x}{b:02x}'

    return None


@deconstructible
class ColorValidator:
    """
    Validator for color codes.
    Supports hex, rgb, rgba, hsl, hsla, and named colors.
    """

    message = "Enter a valid color code."
    code = 'invalid_color'

    def __init__(self, formats=None, allow_named=True, message=None, code=None):
        """
        Initialize the validator.

        Args:
            formats: List of accepted formats. If None, all formats accepted.
            allow_named: Whether to accept named colors.
            message: Custom error message.
            code: Custom error code.
        """
        self.formats = formats
        self.allow_named = allow_named
        if message:
            self.message = message
        if code:
            self.code = code

    def __call__(self, value):
        if not value:
            return

        value = str(value).strip()
        color_format = get_color_format(value)

        if color_format is None:
            raise ValidationError(self.message, code=self.code)

        if color_format == 'named' and not self.allow_named:
            raise ValidationError(
                "Named colors are not allowed.",
                code='named_color_not_allowed'
            )

        if self.formats and color_format not in self.formats:
            if color_format != 'named' or 'named' not in self.formats:
                accepted = ', '.join(self.formats)
                raise ValidationError(
                    f"Color format not accepted. Accepted formats: {accepted}",
                    code='format_not_accepted'
                )

        # Validate RGB/HSL values are in range
        if color_format in ('rgb', 'rgba'):
            self._validate_rgb(value)
        elif color_format in ('hsl', 'hsla'):
            self._validate_hsl(value)

    def _validate_rgb(self, value):
        """Validate RGB values are 0-255."""
        match = re.match(COLOR_PATTERNS['rgb'], value, re.IGNORECASE)
        if not match:
            match = re.match(COLOR_PATTERNS['rgba'], value, re.IGNORECASE)

        if match:
            r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
            if not all(0 <= c <= 255 for c in (r, g, b)):
                raise ValidationError(
                    "RGB values must be between 0 and 255.",
                    code='rgb_out_of_range'
                )

    def _validate_hsl(self, value):
        """Validate HSL values are in range."""
        match = re.match(COLOR_PATTERNS['hsl'], value, re.IGNORECASE)
        if not match:
            match = re.match(COLOR_PATTERNS['hsla'], value, re.IGNORECASE)

        if match:
            h, s, l = int(match.group(1)), int(match.group(2)), int(match.group(3))
            if not (0 <= h <= 360):
                raise ValidationError(
                    "Hue must be between 0 and 360.",
                    code='hue_out_of_range'
                )
            if not all(0 <= c <= 100 for c in (s, l)):
                raise ValidationError(
                    "Saturation and lightness must be between 0 and 100.",
                    code='sl_out_of_range'
                )

    def __eq__(self, other):
        return (
            isinstance(other, ColorValidator) and
            self.formats == other.formats and
            self.allow_named == other.allow_named
        )


def validate_color(value, formats=None, allow_named=True):
    """
    Validate a color value.

    Args:
        value: The color value to validate.
        formats: Optional list of accepted formats.
        allow_named: Whether to accept named colors.

    Raises:
        ValidationError: If the color is invalid.
    """
    validator = ColorValidator(formats=formats, allow_named=allow_named)
    validator(value)


def is_valid_color(value):
    """
    Check if a color value is valid.

    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        validate_color(value)
        return True
    except ValidationError:
        return False
