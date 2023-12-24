# URL Validator

Enhanced URL validation for Django.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.url_validator',
]
```

## Usage

### Form Validation

```python
from django import forms
from django_extensions.url_validator import URLValidator

class LinkForm(forms.Form):
    website = forms.CharField(validators=[URLValidator()])
```

### Utility Functions

```python
from django_extensions.url_validator import is_valid_url, validate_url

# Quick validation
is_valid_url('https://example.com')       # True
is_valid_url('http://localhost:8000')     # False (by default)
is_valid_url('ftp://files.example.com')   # False (by default)
is_valid_url('not-a-url')                 # False

# With exception
validate_url('https://example.com')  # Returns True
validate_url('invalid')               # Raises ValidationError
```

## Validation Rules

Default validation:
- Must have http:// or https:// scheme
- Must have valid domain
- No localhost by default
- No IP addresses by default

## Validator Options

```python
# Allow localhost
URLValidator(allow_localhost=True)

# Allow IP addresses
URLValidator(allow_ip=True)

# Allow additional schemes
URLValidator(schemes=['http', 'https', 'ftp'])

# Require specific TLDs
URLValidator(allowed_tlds=['com', 'org', 'net'])

# Maximum length
URLValidator(max_length=2048)
```

## URL Components Validation

```python
from django_extensions.url_validator import parse_url

result = parse_url('https://user:pass@example.com:8080/path?q=1#hash')
# {
#     'scheme': 'https',
#     'username': 'user',
#     'password': 'pass',
#     'host': 'example.com',
#     'port': 8080,
#     'path': '/path',
#     'query': 'q=1',
#     'fragment': 'hash'
# }
```

## Comparison with Django URLValidator

| Feature | This Validator | Django URLValidator |
|---------|---------------|---------------------|
| Localhost control | Yes | No |
| IP address control | Yes | No |
| TLD validation | Yes | Limited |
| Scheme customization | Yes | Yes |

## License

MIT
