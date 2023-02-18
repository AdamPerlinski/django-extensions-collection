"""Tests for TimeStampedModel."""

import pytest
from datetime import timedelta
from django.db import models
from django.utils import timezone
from unittest.mock import patch

from .models import TimeStampedModel


class ConcreteTimeStampedModel(TimeStampedModel):
    """Concrete model for testing."""
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'timestamped_model'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteTimeStampedModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteTimeStampedModel)
        except Exception:
            pass


class TestTimeStampedModel:
    """Test cases for TimeStampedModel."""

    def test_model_is_abstract(self):
        """Test that TimeStampedModel is abstract."""
        assert TimeStampedModel._meta.abstract is True

    def test_created_field_exists(self):
        """Test that created field is defined."""
        field = ConcreteTimeStampedModel._meta.get_field('created')
        assert field is not None
        assert field.auto_now_add is True
        assert field.db_index is True

    def test_modified_field_exists(self):
