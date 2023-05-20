"""Managers for SoftDeleteModel."""

from django.db import models


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet that handles soft deletion."""

    def delete(self):
        """Soft delete all objects in the queryset."""
        from django.utils import timezone
        return self.update(deleted_at=timezone.now())

    def hard_delete(self):
        """Permanently delete all objects in the queryset."""
        return super().delete()

    def restore(self):
        """Restore all soft-deleted objects in the queryset."""
        return self.update(deleted_at=None)

    def alive(self):
        """Return only non-deleted objects."""
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        """Return only deleted objects."""
        return self.filter(deleted_at__isnull=False)


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted objects by default."""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()


class DeletedManager(models.Manager):
    """Manager that only returns soft-deleted objects."""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).dead()


class AllObjectsManager(models.Manager):
    """Manager that returns all objects including soft-deleted ones."""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)
