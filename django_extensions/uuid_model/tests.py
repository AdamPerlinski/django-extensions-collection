"""Tests for UUIDModel."""

import uuid
import pytest
from django.db import models

from .models import UUIDModel


class ConcreteUUIDModel(UUIDModel):
    """Concrete model for testing."""
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'uuid_model'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteUUIDModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteUUIDModel)
        except Exception:
            pass


class TestUUIDModel:
    """Test cases for UUIDModel."""

    def test_model_is_abstract(self):
        """Test that UUIDModel is abstract."""
        assert UUIDModel._meta.abstract is True

