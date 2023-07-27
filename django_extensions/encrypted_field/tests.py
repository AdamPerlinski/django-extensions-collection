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
            with pytest.raises(ValueError, match="ENCRYPTION_KEY must be set"):
                mixin.encrypt_value("test")


class TestEncryptedCharField:
    """Test cases for EncryptedCharField."""

    def test_is_char_field(self):
        """Test EncryptedCharField is a CharField."""
        field = EncryptedCharField(max_length=100)
        assert isinstance(field, models.CharField)

    def test_max_length_expanded(self):
        """Test max_length is expanded for encrypted data."""
        field = EncryptedCharField(max_length=100)
        assert field.max_length >= 300

    def test_save_and_retrieve(self, create_tables):
        """Test saving and retrieving encrypted data."""
        original = "Secret Information"
        obj = ConcreteEncryptedModel.objects.create(
            name='test',
            secret=original,
            secret_text='text'
        )

        obj.refresh_from_db()
        assert obj.secret == original

    def test_different_values_different_encrypted(self, create_tables):
        """Test different values produce different encrypted data."""
        obj1 = ConcreteEncryptedModel.objects.create(
            name='test1',
            secret='Secret1',
            secret_text='text'
        )
        obj2 = ConcreteEncryptedModel.objects.create(
            name='test2',
            secret='Secret2',
            secret_text='text'
        )

        # Get raw values from database
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT secret FROM encrypted_field_concreteencryptedmodel WHERE id = %s",
                [obj1.pk]
            )
            raw1 = cursor.fetchone()[0]
            cursor.execute(
                "SELECT secret FROM encrypted_field_concreteencryptedmodel WHERE id = %s",
                [obj2.pk]
            )
            raw2 = cursor.fetchone()[0]

        assert raw1 != raw2

    def test_null_value(self, create_tables):
        """Test null value handling."""
        obj = ConcreteEncryptedModel.objects.create(
            name='test',
            secret=None,
            secret_text=None
        )
        obj.refresh_from_db()
        assert obj.secret is None


class TestEncryptedTextField:
    """Test cases for EncryptedTextField."""

    def test_is_text_field(self):
        """Test EncryptedTextField is a TextField."""
        field = EncryptedTextField()
        assert isinstance(field, models.TextField)

    def test_save_and_retrieve(self, create_tables):
        """Test saving and retrieving encrypted text data."""
        original = "This is a longer piece of secret text that needs to be encrypted."
        obj = ConcreteEncryptedModel.objects.create(
            name='test',
            secret='secret',
            secret_text=original
        )

        obj.refresh_from_db()
        assert obj.secret_text == original

    def test_multiline_text(self, create_tables):
        """Test multiline text encryption."""
        original = "Line 1\nLine 2\nLine 3"
        obj = ConcreteEncryptedModel.objects.create(
            name='test',
            secret='secret',
            secret_text=original
        )

        obj.refresh_from_db()
        assert obj.secret_text == original

    def test_unicode_text(self, create_tables):
        """Test unicode text encryption."""
        original = "Hello 世界 🌍 مرحبا"
        obj = ConcreteEncryptedModel.objects.create(
            name='test',
            secret='secret',
            secret_text=original
        )

        obj.refresh_from_db()
        assert obj.secret_text == original
