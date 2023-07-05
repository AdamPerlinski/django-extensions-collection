"""Tests for AutoModifiedField."""

import pytest
from django.db import models
from django.utils import timezone
from datetime import timedelta
import time

from .fields import AutoModifiedField


class ConcreteAutoModifiedModel(models.Model):
    """Concrete model for testing."""
    modified = AutoModifiedField()
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'auto_modified_field'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteAutoModifiedModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteAutoModifiedModel)
        except Exception:
            pass


class TestAutoModifiedField:
    """Test cases for AutoModifiedField."""

