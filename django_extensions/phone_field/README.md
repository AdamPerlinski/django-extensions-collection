# Phone Field

Validated phone number field for Django models.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.phone_field',
]
```

## Usage

```python
from django.db import models
from django_extensions.phone_field import PhoneField

class Contact(models.Model):
    name = models.CharField(max_length=100)
    phone = PhoneField()

# Valid phone numbers
contact = Contact.objects.create(
    name="John",
    phone="+15551234567"
)

# Various formats accepted
Contact.objects.create(name="Jane", phone="555-123-4567")
Contact.objects.create(name="Bob", phone="(555) 123-4567")
Contact.objects.create(name="Alice", phone="+44 20 7946 0958")
```

## Validation

The field validates:
- E.164 format (`+15551234567`)
- North American format (`555-123-4567`)
- International formats
- Minimum 7 digits, maximum 15 digits

## Normalization

Phone numbers are normalized to E.164 format:

```python
contact = Contact.objects.create(phone="(555) 123-4567")
print(contact.phone)  # "+15551234567"
```

## Configuration

```python
# With region hint
phone = PhoneField(region='US')

# Optional phone
phone = PhoneField(blank=True, null=True)

# Max length
phone = PhoneField(max_length=20)
```

## Form Widget

```python
from django_extensions.phone_field import PhoneWidget

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'phone']
        widgets = {
            'phone': PhoneWidget(attrs={'placeholder': '+1 555 123 4567'})
        }
```

## Querying

```python
# Exact match
Contact.objects.filter(phone='+15551234567')

# Contains (normalized)
Contact.objects.filter(phone__contains='555')
```

## License

MIT
