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


class AutoCreatedField(models.DateTimeField):
    """
    A DateTimeField that automatically sets its value to the current
    datetime when the object is first created.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('editable', False)
        kwargs.setdefault('db_index', True)
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        """Set the field value on first save."""
        if add:
            value = timezone.now()
            setattr(model_instance, self.attname, value)
            return value
        return super().pre_save(model_instance, add)

    def deconstruct(self):
        """Return deconstructed field for migrations."""
        name, path, args, kwargs = super().deconstruct()
        if self.editable is False:
            del kwargs['editable']
        if kwargs.get('db_index') is True:
            del kwargs['db_index']
        return name, path, args, kwargs
