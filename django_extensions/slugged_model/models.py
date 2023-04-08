"""
SluggedModel - Abstract model with auto-generated slug.

Usage:
    from django_extensions.slugged_model import SluggedModel

    class Article(SluggedModel):
        title = models.CharField(max_length=200)

        def get_slug_source(self):
            return self.title

    article = Article(title='Hello World')
    article.save()
    print(article.slug)  # 'hello-world'
"""

from django.db import models
from django.utils.text import slugify
import re


class SluggedModel(models.Model):
    """
    An abstract base model that provides automatic slug generation.
    Subclasses should implement get_slug_source() to define the source field.
    """
    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="URL-friendly identifier."
    )

    class Meta:
        abstract = True

    def get_slug_source(self):
        """
        Override this method to return the string to slugify.
        Default returns None which skips auto-generation.
        """
        return None

    def generate_slug(self):
        """Generate a unique slug from the source."""
        source = self.get_slug_source()
        if not source:
            return None

        base_slug = slugify(source)[:240]  # Leave room for suffix
        if not base_slug:
            base_slug = 'item'

        slug = base_slug
        counter = 1

        while self._slug_exists(slug):
            slug = f'{base_slug}-{counter}'
            counter += 1

        return slug

    def _slug_exists(self, slug):
        """Check if a slug already exists (excluding self)."""
        qs = self.__class__.objects.filter(slug=slug)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        return qs.exists()

    def save(self, *args, **kwargs):
        """Auto-generate slug if not set."""
        if not self.slug:
            self.slug = self.generate_slug()
        super().save(*args, **kwargs)

    def regenerate_slug(self, save=True):
        """Force regeneration of the slug."""
        self.slug = self.generate_slug()
        if save:
            self.save(update_fields=['slug'])

    @classmethod
    def get_by_slug(cls, slug):
        """Get an object by its slug."""
        try:
            return cls.objects.get(slug=slug)
        except cls.DoesNotExist:
            return None

    @property
    def slug_url(self):
        """Return the slug formatted for use in URLs."""
        return self.slug.lower()
