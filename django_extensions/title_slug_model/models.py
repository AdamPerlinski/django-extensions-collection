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
