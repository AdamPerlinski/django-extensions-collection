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

    def test_normalize_us_with_country_code(self):
        """Test normalization with country code."""
        field = PhoneNumberField()
        result = field.normalize_phone('15551234567')
        assert result == '+15551234567'

    def test_normalize_with_formatting(self):
        """Test normalization removes formatting."""
        field = PhoneNumberField()
        result = field.normalize_phone('(555) 123-4567')
        assert result == '+15551234567'

    def test_normalize_with_plus(self):
        """Test normalization preserves plus."""
        field = PhoneNumberField()
        result = field.normalize_phone('+15551234567')
        assert result == '+15551234567'

    def test_validate_valid_number(self):
        """Test validation of valid number."""
        field = PhoneNumberField()
        field.validate_phone('+15551234567')  # Should not raise

    def test_validate_too_short(self):
        """Test validation rejects too short numbers."""
        field = PhoneNumberField()
        with pytest.raises(ValidationError):
            field.validate_phone('12345')

    def test_validate_too_long(self):
        """Test validation rejects too long numbers."""
        field = PhoneNumberField()
        with pytest.raises(ValidationError):
            field.validate_phone('1234567890123456')

    def test_save_and_retrieve(self, create_tables):
        """Test saving and retrieving phone numbers."""
        obj = ConcretePhoneModel.objects.create(
            name='test',
            phone='+15551234567'
        )
        obj.refresh_from_db()
        assert obj.phone == '+15551234567'

    def test_deconstruct(self):
        """Test field deconstruction."""
        field = PhoneNumberField(region='UK')
        name, path, args, kwargs = field.deconstruct()
        assert kwargs.get('region') == 'UK'

    def test_deconstruct_default_region(self):
        """Test field deconstruction with default region."""
        field = PhoneNumberField()
        name, path, args, kwargs = field.deconstruct()
        assert 'region' not in kwargs


class TestFormatPhone:
    """Test cases for format_phone utility."""

    def test_national_format_10_digit(self):
        """Test national format for 10-digit number."""
        result = format_phone('5551234567', 'national')
        assert result == '(555) 123-4567'

    def test_national_format_11_digit(self):
        """Test national format for 11-digit number."""
        result = format_phone('15551234567', 'national')
        assert result == '(555) 123-4567'

    def test_international_format(self):
        """Test international format."""
        result = format_phone('5551234567', 'international')
        assert result == '+1 (555) 123-4567'

    def test_e164_format(self):
        """Test E.164 format."""
        result = format_phone('5551234567', 'e164')
        assert result == '+5551234567'

    def test_e164_with_plus(self):
        """Test E.164 format with existing plus."""
        result = format_phone('+15551234567', 'e164')
        assert result == '+15551234567'

    def test_empty_value(self):
        """Test empty value handling."""
        assert format_phone('') == ''
        assert format_phone(None) is None
