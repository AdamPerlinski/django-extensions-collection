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

        # Import all models
        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                imports[model.__name__] = model

        # Import common utilities
        try:
            from django.db.models import Q, F, Count, Sum, Avg, Max, Min
            imports.update({
                'Q': Q, 'F': F, 'Count': Count, 'Sum': Sum,
                'Avg': Avg, 'Max': Max, 'Min': Min,
            })
        except ImportError:
            pass

        try:
            from django.utils import timezone
            imports['timezone'] = timezone
        except ImportError:
            pass

        try:
            from django.conf import settings
            imports['settings'] = settings
        except ImportError:
            pass

        return imports

    def print_imports(self, imports):
        """Print the import statements."""
        self.stdout.write(self.style.SUCCESS('Auto-imported:'))
        for name, obj in sorted(imports.items()):
            module = getattr(obj, '__module__', 'unknown')
            self.stdout.write(f'  from {module} import {name}')

    def run_ipython(self, imports):
        """Run IPython shell."""
        try:
            from IPython import start_ipython
            start_ipython(argv=[], user_ns=imports)
            return True
        except ImportError:
            return False

    def run_bpython(self, imports):
        """Run bpython shell."""
        try:
            import bpython
            bpython.embed(locals_=imports)
            return True
        except ImportError:
            return False

    def run_plain(self, imports):
        """Run plain Python shell."""
        import code
        code.interact(local=imports)

    def handle(self, *args, **options):
        imports = {} if options['no_imports'] else self.get_imports()

        if options['print_imports']:
            self.print_imports(imports)
            if not any([options['ipython'], options['bpython'], options['plain']]):
                return

        self.stdout.write(self.style.SUCCESS(
            f'Django shell_plus - {len(imports)} objects imported automatically'
        ))

        if options['ipython']:
            if self.run_ipython(imports):
                return
            self.stdout.write(self.style.WARNING('IPython not available, falling back'))

        if options['bpython']:
            if self.run_bpython(imports):
                return
            self.stdout.write(self.style.WARNING('bpython not available, falling back'))

        # Try IPython first by default
        if not options['plain']:
            if self.run_ipython(imports):
                return

        self.run_plain(imports)
