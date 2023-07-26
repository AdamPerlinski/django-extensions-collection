"""
EncryptedCharField / EncryptedTextField - Fields with encryption at rest.

Usage:
    from django_extensions.encrypted_field import EncryptedCharField

    class MyModel(models.Model):
        secret_data = EncryptedCharField(max_length=255)

Settings required:
    ENCRYPTION_KEY = 'your-32-character-secret-key-here'
"""

import base64
from django.conf import settings
from django.db import models

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False


class EncryptionMixin:
    """Mixin providing encryption/decryption functionality."""

    def _get_fernet(self):
        """Get or create Fernet instance for encryption."""
        if not HAS_CRYPTOGRAPHY:
            raise ImportError(
                "The 'cryptography' package is required for encrypted fields. "
                "Install it with: pip install cryptography"
            )

        key = getattr(settings, 'ENCRYPTION_KEY', None)
        if not key:
            raise ValueError(
                "ENCRYPTION_KEY must be set in Django settings for encrypted fields."
            )

        # Derive a proper key from the settings key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'django_extensions_salt',
            iterations=100000,
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(key.encode()))
        return Fernet(derived_key)

    def encrypt_value(self, value):
        """Encrypt a string value."""
        if value is None:
            return None
        fernet = self._get_fernet()
        return fernet.encrypt(value.encode()).decode()

    def decrypt_value(self, value):
        """Decrypt an encrypted value."""
        if value is None:
            return None
        fernet = self._get_fernet()
        return fernet.decrypt(value.encode()).decode()


class EncryptedCharField(EncryptionMixin, models.CharField):
    """
    A CharField that encrypts data before storing in the database
    and decrypts when retrieved.
    """

    def __init__(self, *args, **kwargs):
        # Encrypted data is longer than original
        max_length = kwargs.get('max_length', 255)
        kwargs['max_length'] = max(max_length * 3, 500)
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        """Encrypt value before saving to database."""
        value = super().get_prep_value(value)
        return self.encrypt_value(value)

    def from_db_value(self, value, expression, connection):
        """Decrypt value when loading from database."""
        return self.decrypt_value(value)

    def to_python(self, value):
        """Convert value to Python string."""
        if value is None:
            return None
        # If already decrypted (plain string), return as-is
        return value


class EncryptedTextField(EncryptionMixin, models.TextField):
    """
    A TextField that encrypts data before storing in the database
    and decrypts when retrieved.
    """

    def get_prep_value(self, value):
        """Encrypt value before saving to database."""
        value = super().get_prep_value(value)
        return self.encrypt_value(value)

    def from_db_value(self, value, expression, connection):
        """Decrypt value when loading from database."""
        return self.decrypt_value(value)

    def to_python(self, value):
        """Convert value to Python string."""
        if value is None:
            return None
        return value
