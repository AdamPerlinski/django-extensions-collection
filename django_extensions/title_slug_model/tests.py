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
        assert field.unique is True

    def test_auto_slug_generation(self, create_tables):
        """Test automatic slug generation from title."""
        obj = ConcreteTitleSlugModel.objects.create(title='Hello World')
        assert obj.slug == 'hello-world'

    def test_slug_uniqueness(self, create_tables):
        """Test slug uniqueness with duplicates."""
        obj1 = ConcreteTitleSlugModel.objects.create(title='Test')
        obj2 = ConcreteTitleSlugModel.objects.create(title='Test')

        assert obj1.slug == 'test'
        assert obj2.slug == 'test-1'

    def test_str_method(self, create_tables):
        """Test __str__ returns title."""
        obj = ConcreteTitleSlugModel.objects.create(title='My Title')
        assert str(obj) == 'My Title'

    def test_short_description(self, create_tables):
        """Test short_description property."""
        short = 'Short text'
        obj = ConcreteTitleSlugModel.objects.create(
            title='Test',
            description=short
        )
        assert obj.short_description == short

    def test_short_description_truncates(self, create_tables):
        """Test short_description truncates long text."""
        long_text = 'A' * 200
        obj = ConcreteTitleSlugModel.objects.create(
            title='Test',
            description=long_text
        )
        assert len(obj.short_description) == 100
        assert obj.short_description.endswith('...')

    def test_has_description_true(self, create_tables):
        """Test has_description when description exists."""
        obj = ConcreteTitleSlugModel.objects.create(
            title='Test',
            description='Some description'
        )
        assert obj.has_description is True

    def test_has_description_false(self, create_tables):
        """Test has_description when description is empty."""
        obj = ConcreteTitleSlugModel.objects.create(title='Test')
        assert obj.has_description is False

    def test_has_description_whitespace_only(self, create_tables):
        """Test has_description with whitespace-only description."""
        obj = ConcreteTitleSlugModel.objects.create(
            title='Test',
            description='   '
        )
        assert obj.has_description is False

    def test_update_title_no_slug_change(self, create_tables):
        """Test update_title without regenerating slug."""
        obj = ConcreteTitleSlugModel.objects.create(title='Original')
        original_slug = obj.slug

        obj.update_title('New Title')

        assert obj.title == 'New Title'
        assert obj.slug == original_slug

    def test_update_title_with_slug_regeneration(self, create_tables):
        """Test update_title with regenerating slug."""
        obj = ConcreteTitleSlugModel.objects.create(title='Original')

        obj.update_title('New Title', regenerate_slug=True)

        assert obj.title == 'New Title'
        assert obj.slug == 'new-title'

    def test_custom_slug_preserved(self, create_tables):
        """Test that custom slug is preserved."""
        obj = ConcreteTitleSlugModel(title='Test', slug='custom-slug')
        obj.save()
        assert obj.slug == 'custom-slug'

    def test_empty_title_slug(self, create_tables):
        """Test slug generation with empty title."""
        obj = ConcreteTitleSlugModel.objects.create(title='')
        assert obj.slug == 'item'
