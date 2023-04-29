"""Tests for ActivatorModel."""

import pytest
from django.db import models
from django.utils import timezone
from datetime import timedelta

from .models import ActivatorModel


class ConcreteActivatorModel(ActivatorModel):
    """Concrete model for testing."""
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'activator_model'


@pytest.fixture
def create_tables(db):
    """Create test tables."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.create_model(ConcreteActivatorModel)
        except Exception:
            pass
    yield
    with connection.schema_editor() as schema_editor:
        try:
            schema_editor.delete_model(ConcreteActivatorModel)
        except Exception:
            pass


class TestActivatorModel:
    """Test cases for ActivatorModel."""

    def test_model_is_abstract(self):
        """Test that ActivatorModel is abstract."""
        assert ActivatorModel._meta.abstract is True

    def test_fields_exist(self):
        """Test that all fields are defined."""
        assert ConcreteActivatorModel._meta.get_field('is_enabled') is not None
        assert ConcreteActivatorModel._meta.get_field('activate_date') is not None
        assert ConcreteActivatorModel._meta.get_field('deactivate_date') is not None

    def test_default_is_enabled(self, create_tables):
        """Test default is_enabled is True."""
        obj = ConcreteActivatorModel.objects.create(name='test')
        assert obj.is_enabled is True

    def test_is_active_when_enabled(self, create_tables):
        """Test is_active when enabled with no date restrictions."""
        obj = ConcreteActivatorModel.objects.create(name='test')
        assert obj.is_active is True

    def test_is_active_when_disabled(self, create_tables):
        """Test is_active when disabled."""
        obj = ConcreteActivatorModel.objects.create(name='test', is_enabled=False)
        assert obj.is_active is False

    def test_is_active_before_activate_date(self, create_tables):
        """Test is_active before activate_date."""
        future = timezone.now() + timedelta(days=1)
        obj = ConcreteActivatorModel.objects.create(
            name='test',
            activate_date=future
        )
        assert obj.is_active is False

    def test_is_active_after_activate_date(self, create_tables):
        """Test is_active after activate_date."""
        past = timezone.now() - timedelta(days=1)
        obj = ConcreteActivatorModel.objects.create(
            name='test',
            activate_date=past
        )
        assert obj.is_active is True

    def test_is_active_before_deactivate_date(self, create_tables):
        """Test is_active before deactivate_date."""
        future = timezone.now() + timedelta(days=1)
        obj = ConcreteActivatorModel.objects.create(
            name='test',
            deactivate_date=future
        )
        assert obj.is_active is True

    def test_is_active_after_deactivate_date(self, create_tables):
        """Test is_active after deactivate_date."""
        past = timezone.now() - timedelta(days=1)
        obj = ConcreteActivatorModel.objects.create(
            name='test',
            deactivate_date=past
        )
        assert obj.is_active is False

    def test_activate_method(self, create_tables):
        """Test activate method."""
        obj = ConcreteActivatorModel.objects.create(
            name='test',
            is_enabled=False,
            activate_date=timezone.now() + timedelta(days=1)
        )
        obj.activate()

        assert obj.is_enabled is True
        assert obj.activate_date is None
        assert obj.deactivate_date is None

    def test_deactivate_method(self, create_tables):
        """Test deactivate method."""
        obj = ConcreteActivatorModel.objects.create(name='test')
        obj.deactivate()

        assert obj.is_enabled is False

    def test_schedule_activation(self, create_tables):
        """Test schedule_activation method."""
        start = timezone.now() + timedelta(hours=1)
        end = timezone.now() + timedelta(days=1)

        obj = ConcreteActivatorModel.objects.create(name='test')
        obj.schedule_activation(start, end)

        assert obj.is_enabled is True
        assert obj.activate_date == start
        assert obj.deactivate_date == end

    def test_activation_status_disabled(self, create_tables):
        """Test activation_status when disabled."""
        obj = ConcreteActivatorModel.objects.create(name='test', is_enabled=False)
        assert obj.activation_status == 'disabled'

    def test_activation_status_scheduled(self, create_tables):
        """Test activation_status when scheduled."""
        future = timezone.now() + timedelta(days=1)
        obj = ConcreteActivatorModel.objects.create(name='test', activate_date=future)
        assert obj.activation_status == 'scheduled'

    def test_activation_status_expired(self, create_tables):
        """Test activation_status when expired."""
        past = timezone.now() - timedelta(days=1)
        obj = ConcreteActivatorModel.objects.create(name='test', deactivate_date=past)
        assert obj.activation_status == 'expired'

    def test_activation_status_active(self, create_tables):
        """Test activation_status when active."""
        obj = ConcreteActivatorModel.objects.create(name='test')
        assert obj.activation_status == 'active'

    def test_queryset_active(self, create_tables):
        """Test active() queryset method."""
        active_obj = ConcreteActivatorModel.objects.create(name='active')
        inactive_obj = ConcreteActivatorModel.objects.create(name='inactive', is_enabled=False)

        active_qs = ConcreteActivatorModel.objects.active()
        assert active_obj in active_qs
        assert inactive_obj not in active_qs

    def test_queryset_inactive(self, create_tables):
        """Test inactive() queryset method."""
        active_obj = ConcreteActivatorModel.objects.create(name='active')
        inactive_obj = ConcreteActivatorModel.objects.create(name='inactive', is_enabled=False)

        inactive_qs = ConcreteActivatorModel.objects.inactive()
        assert active_obj not in inactive_qs
        assert inactive_obj in inactive_qs

    def test_time_until_active(self, create_tables):
        """Test time_until_active property."""
        future = timezone.now() + timedelta(hours=2)
        obj = ConcreteActivatorModel.objects.create(name='test', activate_date=future)

        time_until = obj.time_until_active
        assert time_until is not None
        assert time_until.total_seconds() > 0

    def test_time_until_inactive(self, create_tables):
        """Test time_until_inactive property."""
        future = timezone.now() + timedelta(hours=2)
        obj = ConcreteActivatorModel.objects.create(name='test', deactivate_date=future)

        time_until = obj.time_until_inactive
        assert time_until is not None
        assert time_until.total_seconds() > 0
