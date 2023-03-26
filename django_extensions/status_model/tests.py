"""Tests for StatusModel."""

import pytest
from django.db import models
from django.utils import timezone
from datetime import timedelta

from .models import StatusModel, StatusField


class ConcreteStatusModel(StatusModel):
    """Concrete model for testing."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = StatusField(choices=STATUS_CHOICES, default='pending')
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'status_model'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteStatusModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteStatusModel)
        except Exception:
            pass


class TestStatusField:
    """Test cases for StatusField."""

    def test_is_charfield(self):
        """Test StatusField is a CharField."""
        field = StatusField()
        assert isinstance(field, models.CharField)

    def test_default_max_length(self):
        """Test default max_length is 50."""
        field = StatusField()
        assert field.max_length == 50

    def test_custom_max_length(self):
        """Test custom max_length is respected."""
        field = StatusField(max_length=100)
        assert field.max_length == 100

    def test_db_index_default(self):
        """Test db_index is True by default."""
        field = StatusField()
        assert field.db_index is True


class TestStatusModel:
