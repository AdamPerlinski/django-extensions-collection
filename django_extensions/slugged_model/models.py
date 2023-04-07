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
