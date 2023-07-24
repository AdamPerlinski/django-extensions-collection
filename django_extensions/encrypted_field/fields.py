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
