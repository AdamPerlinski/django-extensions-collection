"""
AutoCreatedField - DateTimeField that auto-sets on creation.

Usage:
    from django_extensions.auto_created_field import AutoCreatedField

    class MyModel(models.Model):
        created = AutoCreatedField()
        name = models.CharField(max_length=100)
"""

from django.db import models
from django.utils import timezone

