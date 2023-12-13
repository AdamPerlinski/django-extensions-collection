# Color Validator

CSS color validation and normalization.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.color_validator',
]
```

## Usage

### Form Validation

```python
from django import forms
from django_extensions.color_validator import ColorValidator

class ThemeForm(forms.Form):
    primary_color = forms.CharField(validators=[ColorValidator()])
```

### Utility Functions

```python
from django_extensions.color_validator import (
    is_valid_color,
    validate_color,
    normalize_color
)

# Quick validation
is_valid_color('#FF5733')           # True
is_valid_color('#fff')              # True
is_valid_color('rgb(255, 100, 50)') # True
is_valid_color('hsl(120, 50%, 50%)') # True
is_valid_color('invalid')           # False

# Validate with exception
validate_color('#FF5733')  # Returns True
validate_color('invalid')  # Raises ValidationError

# Normalize to hex
normalize_color('#fff')              # '#FFFFFF'
normalize_color('rgb(255, 0, 0)')    # '#FF0000'
```

## Supported Formats

| Format | Example | Valid |
|--------|---------|-------|
| Hex 6 | #FF5733 | Yes |
| Hex 3 | #F53 | Yes |
| Hex 8 | #FF5733FF | Yes |
| RGB | rgb(255, 100, 50) | Yes |
| RGBA | rgba(255, 100, 50, 0.5) | Yes |
| HSL | hsl(120, 50%, 50%) | Yes |
| HSLA | hsla(120, 50%, 50%, 0.5) | Yes |
| Named | red, blue | Optional |

## Validator Options

```python
# Accept named colors
ColorValidator(allow_named=True)

# Only hex format
ColorValidator(formats=['hex'])

# Hex and RGB only
ColorValidator(formats=['hex', 'rgb'])
```

## Color Conversion

```python
from django_extensions.color_validator import (
    hex_to_rgb,
    rgb_to_hex,
    hex_to_hsl
)

hex_to_rgb('#FF5733')  # (255, 87, 51)
rgb_to_hex(255, 87, 51)  # '#FF5733'
hex_to_hsl('#FF5733')  # (11, 100, 60)
```

## License

MIT
