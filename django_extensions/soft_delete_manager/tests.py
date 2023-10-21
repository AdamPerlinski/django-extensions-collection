"""Tests for soft_delete_manager - delegates to soft_delete tests."""

import pytest

# The actual tests are in django_extensions.soft_delete.tests
# This file ensures the re-export works correctly

def test_imports():
    """Test that all managers can be imported."""
    from django_extensions.soft_delete_manager import (
        SoftDeleteManager,
        SoftDeleteQuerySet,
        DeletedManager,
        AllObjectsManager,
    )

    assert SoftDeleteManager is not None
    assert SoftDeleteQuerySet is not None
    assert DeletedManager is not None
    assert AllObjectsManager is not None
