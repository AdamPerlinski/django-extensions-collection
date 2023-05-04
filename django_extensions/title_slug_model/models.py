"""
TitleSlugModel - Abstract model with title, description, and auto-slug.

Usage:
    from django_extensions.title_slug_model import TitleSlugModel

    class Article(TitleSlugModel):
        author = models.ForeignKey(User, on_delete=models.CASCADE)

    article = Article(title='My Article', description='About something')
    article.save()
    print(article.slug)  # 'my-article'
"""

from django.db import models
from django.utils.text import slugify


class TitleSlugModel(models.Model):
    """
    An abstract base model that provides title, description, and auto-slug.
    """
    title = models.CharField(
        max_length=255,
        help_text="The title of this item."
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text="A description of this item."
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="URL-friendly identifier (auto-generated from title)."
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Auto-generate slug from title if not set."""
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        """Generate a unique slug from the title."""
        base_slug = slugify(self.title)[:240]
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

    @property
    def short_description(self):
        """Return first 100 characters of description."""
        if len(self.description) <= 100:
            return self.description
        return self.description[:97] + '...'

    @property
    def has_description(self):
        """Check if description is set."""
        return bool(self.description and self.description.strip())

    def update_title(self, new_title, regenerate_slug=False):
        """Update title and optionally regenerate slug."""
        self.title = new_title
        if regenerate_slug:
            self.slug = self._generate_unique_slug()
        self.save()
