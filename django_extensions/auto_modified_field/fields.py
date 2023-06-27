"""
AutoModifiedField - DateTimeField that auto-updates on every save.

Usage:
    from django_extensions.auto_modified_field import AutoModifiedField

    class MyModel(models.Model):
        modified = AutoModifiedField()
        name = models.CharField(max_length=100)
"""

from django.db import models
from django.utils import timezone

