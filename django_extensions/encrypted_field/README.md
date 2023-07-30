# Encrypted Field

Fernet-encrypted field for storing sensitive data securely.

## Installation

```bash
pip install cryptography
```

```python
INSTALLED_APPS = [
    'django_extensions.encrypted_field',
]

# settings.py
ENCRYPTION_KEY = 'your-32-byte-base64-encoded-key'
```

## Generate Key

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())  # Use this in settings
```

## Usage

```python
from django.db import models
from django_extensions.encrypted_field import EncryptedField, EncryptedTextField

class User(models.Model):
    name = models.CharField(max_length=100)
    ssn = EncryptedField(max_length=11)
    notes = EncryptedTextField()

user = User.objects.create(
    name="John",
    ssn="123-45-6789",
    notes="Sensitive information"
)

# Data is encrypted in database
print(user.ssn)  # "123-45-6789" (decrypted automatically)
```

## Field Types

| Field | Description |
|-------|-------------|
| `EncryptedField` | Encrypted CharField |
| `EncryptedTextField` | Encrypted TextField |
| `EncryptedEmailField` | Encrypted EmailField |
| `EncryptedIntegerField` | Encrypted IntegerField |
| `EncryptedJSONField` | Encrypted JSONField |

## Security Notes

1. **Key Management**: Store encryption key securely (environment variable, secrets manager)
2. **Key Rotation**: Plan for key rotation strategy
3. **Backup**: Encrypted data is unrecoverable without the key
4. **Searching**: Cannot search/filter on encrypted fields directly

## Database Storage

Data is stored as base64-encoded encrypted bytes:

```
gAAAAABk... (encrypted)
```

## Configuration

```python
# Custom encryption key per field
ssn = EncryptedField(encryption_key='field-specific-key')

# Nullable encrypted field
notes = EncryptedTextField(null=True, blank=True)
```

## License

MIT
