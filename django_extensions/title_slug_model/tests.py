"""Tests for TitleSlugModel."""

import pytest
from django.db import models

from .models import TitleSlugModel


class ConcreteTitleSlugModel(TitleSlugModel):
    """Concrete model for testing."""

    class Meta:
        app_label = 'title_slug_model'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteTitleSlugModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteTitleSlugModel)
        except Exception:
            pass


class TestTitleSlugModel:
    """Test cases for TitleSlugModel."""

    def test_model_is_abstract(self):
        """Test that TitleSlugModel is abstract."""
        assert TitleSlugModel._meta.abstract is True

    def test_fields_exist(self):
        """Test that all fields are defined."""
        assert ConcreteTitleSlugModel._meta.get_field('title') is not None
        assert ConcreteTitleSlugModel._meta.get_field('description') is not None
        assert ConcreteTitleSlugModel._meta.get_field('slug') is not None

    def test_title_max_length(self):
        """Test title max_length."""
        field = ConcreteTitleSlugModel._meta.get_field('title')
        assert field.max_length == 255

    def test_description_blank(self):
        """Test description can be blank."""
        field = ConcreteTitleSlugModel._meta.get_field('description')
        assert field.blank is True

    def test_slug_unique(self):
        """Test slug is unique."""
        field = ConcreteTitleSlugModel._meta.get_field('slug')
