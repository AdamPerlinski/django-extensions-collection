"""
SoftDeleteManager is included in the soft_delete extension.
This module re-exports those managers for convenience.
"""

from django_extensions.soft_delete.managers import (
    SoftDeleteManager,
    SoftDeleteQuerySet,
    DeletedManager,
    AllObjectsManager,
)

__all__ = ['SoftDeleteManager', 'SoftDeleteQuerySet', 'DeletedManager', 'AllObjectsManager']
