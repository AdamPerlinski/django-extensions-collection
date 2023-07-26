"""Tests for EncryptedCharField and EncryptedTextField."""

import pytest
from django.db import models
from django.conf import settings
from unittest.mock import patch

from .fields import EncryptedCharField, EncryptedTextField, EncryptionMixin


class ConcreteEncryptedModel(models.Model):
    """Concrete model for testing."""
    secret = EncryptedCharField(max_length=255)
    secret_text = EncryptedTextField()
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'encrypted_field'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteEncryptedModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteEncryptedModel)
        except Exception:
            pass


class TestEncryptionMixin:
    """Test cases for EncryptionMixin."""

    def test_encrypt_decrypt_roundtrip(self):
        """Test encrypting and decrypting returns original value."""
        mixin = EncryptionMixin()
        original = "Hello, World!"

        encrypted = mixin.encrypt_value(original)
        decrypted = mixin.decrypt_value(encrypted)

        assert decrypted == original

    def test_encrypt_returns_different_value(self):
        """Test encryption produces different output than input."""
        mixin = EncryptionMixin()
        original = "Secret Data"

        encrypted = mixin.encrypt_value(original)

        assert encrypted != original

    def test_encrypt_none(self):
        """Test encrypting None returns None."""
        mixin = EncryptionMixin()
        assert mixin.encrypt_value(None) is None

    def test_decrypt_none(self):
        """Test decrypting None returns None."""
        mixin = EncryptionMixin()
        assert mixin.decrypt_value(None) is None

    def test_missing_encryption_key(self):
        """Test error when ENCRYPTION_KEY is not set."""
        mixin = EncryptionMixin()

        with patch.object(settings, 'ENCRYPTION_KEY', None):
