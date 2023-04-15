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
        assert obj.slug == 'hello-world'

    def test_slug_with_special_characters(self, create_tables):
        """Test slug generation with special characters."""
        obj = ConcreteSluggedModel.objects.create(title='Hello, World! @#$%')
        assert obj.slug == 'hello-world'

    def test_slug_with_unicode(self, create_tables):
        """Test slug generation with unicode characters."""
        obj = ConcreteSluggedModel.objects.create(title='Café Résumé')
        assert 'cafe' in obj.slug.lower()

    def test_unique_slug_generation(self, create_tables):
        """Test unique slug generation with duplicates."""
        obj1 = ConcreteSluggedModel.objects.create(title='Hello World')
        obj2 = ConcreteSluggedModel.objects.create(title='Hello World')

        assert obj1.slug == 'hello-world'
        assert obj2.slug == 'hello-world-1'

    def test_multiple_duplicates(self, create_tables):
        """Test slug generation with multiple duplicates."""
        obj1 = ConcreteSluggedModel.objects.create(title='Test')
        obj2 = ConcreteSluggedModel.objects.create(title='Test')
        obj3 = ConcreteSluggedModel.objects.create(title='Test')

        assert obj1.slug == 'test'
        assert obj2.slug == 'test-1'
        assert obj3.slug == 'test-2'

    def test_custom_slug_preserved(self, create_tables):
        """Test that custom slug is preserved."""
        obj = ConcreteSluggedModel(title='Hello World', slug='custom-slug')
        obj.save()
        assert obj.slug == 'custom-slug'

    def test_regenerate_slug(self, create_tables):
        """Test regenerate_slug method."""
        obj = ConcreteSluggedModel.objects.create(title='Original Title')
        original_slug = obj.slug

        obj.title = 'New Title'
        obj.regenerate_slug()

        assert obj.slug != original_slug
        assert obj.slug == 'new-title'

    def test_get_by_slug(self, create_tables):
        """Test get_by_slug classmethod."""
        obj = ConcreteSluggedModel.objects.create(title='Test')
        found = ConcreteSluggedModel.get_by_slug('test')
        assert found == obj

    def test_get_by_slug_not_found(self, create_tables):
        """Test get_by_slug returns None when not found."""
        found = ConcreteSluggedModel.get_by_slug('nonexistent')
        assert found is None

    def test_slug_url_property(self, create_tables):
        """Test slug_url property."""
        obj = ConcreteSluggedModel.objects.create(title='Test Title')
        assert obj.slug_url == obj.slug.lower()

    def test_empty_title(self, create_tables):
        """Test slug generation with empty title."""
        obj = ConcreteSluggedModel.objects.create(title='')
        assert obj.slug == 'item'

    def test_slug_max_length(self, create_tables):
        """Test slug respects max length."""
        long_title = 'A' * 300
        obj = ConcreteSluggedModel.objects.create(title=long_title)
        assert len(obj.slug) <= 255

    def test_slug_not_regenerated_on_save(self, create_tables):
        """Test slug is not regenerated on subsequent saves."""
        obj = ConcreteSluggedModel.objects.create(title='Original')
        original_slug = obj.slug

        obj.title = 'Updated'
        obj.save()

        assert obj.slug == original_slug
