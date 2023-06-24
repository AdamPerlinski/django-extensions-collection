"""Tests for AutoCreatedField."""

import pytest
from django.db import models
from django.utils import timezone
from datetime import timedelta

from .fields import AutoCreatedField


class ConcreteAutoCreatedModel(models.Model):
    """Concrete model for testing."""
    created = AutoCreatedField()
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'auto_created_field'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteAutoCreatedModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteAutoCreatedModel)
        except Exception:
            pass


class TestAutoCreatedField:
    """Test cases for AutoCreatedField."""

