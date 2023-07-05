"""
AutoModifiedField - DateTimeField that auto-updates on every save.

Usage:
    from django_extensions.auto_modified_field import AutoModifiedField

    class MyModel(models.Model):
        modified = AutoModifiedField()
        name = models.CharField(max_length=100)
"""

from django.db import models
from django.utils import timezone


class AutoModifiedField(models.DateTimeField):
    """
    A DateTimeField that automatically updates its value to the current
    datetime every time the object is saved.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('editable', False)
        kwargs.setdefault('db_index', True)
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        """Update the field value on every save."""
        value = timezone.now()
        setattr(model_instance, self.attname, value)
        return value

    def deconstruct(self):
        """Return deconstructed field for migrations."""
        name, path, args, kwargs = super().deconstruct()
        if self.editable is False:
            del kwargs['editable']
        if kwargs.get('db_index') is True:
            del kwargs['db_index']
        return name, path, args, kwargs
