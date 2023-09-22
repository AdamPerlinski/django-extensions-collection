"""Tests for PhoneNumberField."""

import pytest
from django.core.exceptions import ValidationError
from django.db import models

from .fields import PhoneNumberField, format_phone


class ConcretePhoneModel(models.Model):
    """Concrete model for testing."""
    phone = PhoneNumberField()
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'phone_field'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcretePhoneModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcretePhoneModel)
        except Exception:
            pass


class TestPhoneNumberField:
    """Test cases for PhoneNumberField."""

    def test_is_char_field(self):
        """Test PhoneNumberField is a CharField."""
        field = PhoneNumberField()
        assert isinstance(field, models.CharField)

    def test_default_max_length(self):
        """Test default max_length is 20."""
        field = PhoneNumberField()
        assert field.max_length == 20

    def test_default_region(self):
        """Test default region is US."""
        field = PhoneNumberField()
        assert field.region == 'US'

    def test_normalize_us_10_digit(self):
        """Test normalization of 10-digit US number."""
        field = PhoneNumberField()
        result = field.normalize_phone('5551234567')
        assert result == '+15551234567'

