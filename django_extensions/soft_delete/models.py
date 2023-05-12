"""
SoftDeleteModel - Abstract model with soft delete functionality.

Usage:
    from django_extensions.soft_delete import SoftDeleteModel

    class MyModel(SoftDeleteModel):
        name = models.CharField(max_length=100)

    # Soft delete
    obj.delete()  # Sets deleted_at, doesn't actually delete

    # Hard delete
    obj.hard_delete()  # Actually deletes from database

    # Restore
    obj.restore()  # Clears deleted_at

    # Query only deleted objects
    MyModel.deleted.all()

    # Query all objects including deleted
    MyModel.all_objects.all()
"""

from django.db import models
from django.utils import timezone
