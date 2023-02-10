"""
TimeStampedModel - Abstract model with automatic created and modified timestamps.

Usage:
    from django_extensions.timestamped_model import TimeStampedModel

    class MyModel(TimeStampedModel):
        name = models.CharField(max_length=100)
"""

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
