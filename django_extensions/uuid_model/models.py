"""
UUIDModel - Abstract model with UUID as primary key.

Usage:
    from django_extensions.uuid_model import UUIDModel

    class MyModel(UUIDModel):
        name = models.CharField(max_length=100)
"""

import uuid
from django.db import models


class UUIDModel(models.Model):
    """
