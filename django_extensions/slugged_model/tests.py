"""Tests for SluggedModel."""

import pytest
from django.db import models

from .models import SluggedModel


class ConcreteSluggedModel(SluggedModel):
    """Concrete model for testing."""
    title = models.CharField(max_length=200)

    class Meta:
        app_label = 'slugged_model'

    def get_slug_source(self):
        return self.title


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteSluggedModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteSluggedModel)
        except Exception:
            pass


class TestSluggedModel:
    """Test cases for SluggedModel."""

    def test_model_is_abstract(self):
        """Test that SluggedModel is abstract."""
        assert SluggedModel._meta.abstract is True

    def test_slug_field_exists(self):
        """Test that slug field is defined."""
        field = ConcreteSluggedModel._meta.get_field('slug')
        assert field is not None
        assert isinstance(field, models.SlugField)
        assert field.unique is True
        assert field.db_index is True

    def test_auto_slug_generation(self, create_tables):
        """Test automatic slug generation."""
        obj = ConcreteSluggedModel.objects.create(title='Hello World')
