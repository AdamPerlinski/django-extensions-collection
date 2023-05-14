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

from .managers import SoftDeleteManager, DeletedManager, AllObjectsManager


class SoftDeleteModel(models.Model):
    """
    An abstract base model that provides soft delete functionality.
    Objects are marked as deleted rather than being removed from the database.
    """
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Timestamp when this record was soft-deleted."
    )

    objects = SoftDeleteManager()
    deleted = DeletedManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, hard=False):
        """
        Soft delete the object by setting deleted_at.
        Use hard=True to permanently delete.
        """
        if hard:
            return super().delete(using=using, keep_parents=keep_parents)

        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete the object from the database."""
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """Restore a soft-deleted object."""
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    @property
    def is_deleted(self):
        """Check if the object is soft-deleted."""
        return self.deleted_at is not None

    @property
    def is_alive(self):
        """Check if the object is not soft-deleted."""
        return self.deleted_at is None
