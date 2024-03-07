"""
shell_plus - Enhanced Django shell with auto-imports.

Usage:
    python manage.py shell_plus
    python manage.py shell_plus --ipython
    python manage.py shell_plus --print-imports
"""

from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = 'Like the built-in Django shell but with all models auto-imported.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ipython',
            action='store_true',
            help='Use IPython if available.',
        )
        parser.add_argument(
            '--bpython',
            action='store_true',
            help='Use bpython if available.',
        )
        parser.add_argument(
            '--plain',
            action='store_true',
            help='Use plain Python shell.',
        )
        parser.add_argument(
            '--print-imports',
            action='store_true',
            help='Print the auto-import statements.',
        )
        parser.add_argument(
            '--no-imports',
            action='store_true',
            help='Do not auto-import models.',
        )

    def get_imports(self):
        """Get dictionary of imports for the shell context."""
        imports = {}
