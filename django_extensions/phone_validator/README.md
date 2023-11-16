# Phone Validator

Phone number validation for Django forms and models.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.phone_validator',
]
```

## Usage

### Form Validation

```python
from django import forms
from django_extensions.phone_validator import PhoneNumberValidator

class ContactForm(forms.Form):
    phone = forms.CharField(validators=[PhoneNumberValidator()])
```

### Model Validation

```python
from django.db import models
from django_extensions.phone_validator import PhoneNumberValidator

class Contact(models.Model):
    phone = models.CharField(
        max_length=20,
        validators=[PhoneNumberValidator()]
    )
```

### Utility Function

```python
from django_extensions.phone_validator import is_valid_phone, validate_phone_number

# Quick validation
is_valid_phone('+15551234567')  # True
is_valid_phone('invalid')        # False

# With exception
validate_phone_number('+15551234567')  # Returns normalized
validate_phone_number('invalid')        # Raises ValidationError
```

## Supported Formats

| Format | Example | Valid |
|--------|---------|-------|
| E.164 | +15551234567 | Yes |
| North American | 555-123-4567 | Yes |
| With parentheses | (555) 123-4567 | Yes |
| International | +44 20 7946 0958 | Yes |
| Too short | 123 | No |
| Letters | 555-CALL-NOW | No |

## Validator Options

```python
# Require specific format
PhoneNumberValidator(format='e164')

# Require country code
PhoneNumberValidator(require_country_code=True)

# Specific region
PhoneNumberValidator(region='US')
```

## Normalization

```python
from django_extensions.phone_validator import normalize_phone

normalize_phone('(555) 123-4567')  # '+15551234567'
normalize_phone('+44 20 7946 0958')  # '+442079460958'
```

## License

MIT
