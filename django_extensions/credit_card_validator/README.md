# Credit Card Validator

Credit card validation using Luhn algorithm with card type detection.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.credit_card_validator',
]
```

## Usage

### Form Validation

```python
from django import forms
from django_extensions.credit_card_validator import CreditCardValidator

class PaymentForm(forms.Form):
    card_number = forms.CharField(validators=[CreditCardValidator()])
```

### Utility Functions

```python
from django_extensions.credit_card_validator import (
    is_valid_card,
    get_card_type,
    validate_credit_card
)

# Quick validation
is_valid_card('4111111111111111')  # True (Visa)
is_valid_card('1234567890123456')  # False

# Get card type
get_card_type('4111111111111111')  # 'visa'
get_card_type('5500000000000004')  # 'mastercard'
get_card_type('378282246310005')   # 'amex'

# Validate with exception
validate_credit_card('4111111111111111')  # Returns True
validate_credit_card('1234567890123456')  # Raises ValidationError
```

## Supported Card Types

| Card | Prefix | Length | Example |
|------|--------|--------|---------|
| Visa | 4 | 16 | 4111111111111111 |
| Mastercard | 51-55 | 16 | 5500000000000004 |
| American Express | 34, 37 | 15 | 378282246310005 |
| Discover | 6011 | 16 | 6011111111111117 |
| Diners Club | 36 | 14 | 36000000000008 |
| JCB | 35 | 16 | 3530111333300000 |

## Luhn Algorithm

The validator uses the Luhn algorithm (mod 10) to verify card numbers:

1. Double every second digit from right
2. Subtract 9 from results > 9
3. Sum all digits
4. Valid if sum % 10 == 0

## Restrict Card Types

```python
# Only accept Visa and Mastercard
CreditCardValidator(accepted_cards=['visa', 'mastercard'])
```

## Security Note

Never store full credit card numbers. Use this for validation before tokenization with a payment processor.

## License

MIT
