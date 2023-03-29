"""Tests for StatusModel."""

import pytest
from django.db import models
from django.utils import timezone
from datetime import timedelta

from .models import StatusModel, StatusField


class ConcreteStatusModel(StatusModel):
    """Concrete model for testing."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = StatusField(choices=STATUS_CHOICES, default='pending')
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'status_model'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteStatusModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteStatusModel)
        except Exception:
            pass


class TestStatusField:
    """Test cases for StatusField."""

    def test_is_charfield(self):
        """Test StatusField is a CharField."""
        field = StatusField()
        assert isinstance(field, models.CharField)

    def test_default_max_length(self):
        """Test default max_length is 50."""
        field = StatusField()
        assert field.max_length == 50

    def test_custom_max_length(self):
        """Test custom max_length is respected."""
        field = StatusField(max_length=100)
        assert field.max_length == 100

    def test_db_index_default(self):
        """Test db_index is True by default."""
        field = StatusField()
        assert field.db_index is True


class TestStatusModel:
    """Test cases for StatusModel."""

    def test_model_is_abstract(self):
        """Test that StatusModel is abstract."""
        assert StatusModel._meta.abstract is True

    def test_status_changed_field_exists(self):
        """Test that status_changed field is defined."""
        field = ConcreteStatusModel._meta.get_field('status_changed')
        assert field is not None
        assert field.null is True

    def test_default_status(self, create_tables):
        """Test default status is set."""
        obj = ConcreteStatusModel.objects.create(name='test')
        assert obj.status == 'pending'

    def test_is_status_properties(self, create_tables):
        """Test auto-generated is_<status> properties."""
        obj = ConcreteStatusModel.objects.create(name='test')

        assert obj.is_pending is True
        assert obj.is_processing is False
        assert obj.is_completed is False
        assert obj.is_cancelled is False

    def test_set_status(self, create_tables):
        """Test set_status method."""
        obj = ConcreteStatusModel.objects.create(name='test')

        old_status = obj.set_status('processing')

        assert old_status == 'pending'
        assert obj.status == 'processing'
        assert obj.is_processing is True
        assert obj.status_changed is not None

    def test_set_status_updates_timestamp(self, create_tables):
        """Test set_status updates status_changed."""
        obj = ConcreteStatusModel.objects.create(name='test')

        obj.set_status('processing')
        first_change = obj.status_changed

        obj.set_status('completed')
        second_change = obj.status_changed

        assert second_change >= first_change

    def test_set_status_same_value(self, create_tables):
        """Test set_status with same value doesn't update timestamp."""
        obj = ConcreteStatusModel.objects.create(name='test')

        obj.set_status('pending')  # Same as default

        assert obj.status_changed is None

    def test_set_status_no_save(self, create_tables):
        """Test set_status with save=False."""
        obj = ConcreteStatusModel.objects.create(name='test')

        obj.set_status('processing', save=False)

        obj.refresh_from_db()
        assert obj.status == 'pending'  # Not saved

    def test_status_age(self, create_tables):
        """Test status_age property."""
        obj = ConcreteStatusModel.objects.create(name='test')
        obj.set_status('processing')

        age = obj.status_age
        assert age is not None
        assert age.total_seconds() >= 0

    def test_status_age_none(self, create_tables):
        """Test status_age is None when never changed."""
        obj = ConcreteStatusModel.objects.create(name='test')
        assert obj.status_age is None

    def test_get_available_statuses(self, create_tables):
        """Test get_available_statuses method."""
        obj = ConcreteStatusModel.objects.create(name='test')
        statuses = obj.get_available_statuses()

        assert statuses == ['pending', 'processing', 'completed', 'cancelled']

    def test_get_status_display_name(self, create_tables):
        """Test get_status_display_name method."""
        obj = ConcreteStatusModel.objects.create(name='test')
        assert obj.get_status_display_name() == 'Pending'

        obj.set_status('processing')
        assert obj.get_status_display_name() == 'Processing'

    def test_status_persists_after_save(self, create_tables):
        """Test status persists after save."""
        obj = ConcreteStatusModel.objects.create(name='test')
        obj.set_status('completed')

        obj.refresh_from_db()
        assert obj.status == 'completed'
