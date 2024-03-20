"""
clean_pyc - Remove .pyc files and __pycache__ directories.

Usage:
    python manage.py clean_pyc
    python manage.py clean_pyc --path /path/to/project
    python manage.py clean_pyc --dry-run
"""

import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Remove .pyc files and __pycache__ directories.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            default=None,
            help='Path to clean. Defaults to BASE_DIR.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without deleting.',
        )
        parser.add_argument(
            '--no-pycache',
            action='store_true',
            help='Do not remove __pycache__ directories.',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show each file/directory being removed.',
        )

    def handle(self, *args, **options):
        base_path = options['path'] or getattr(settings, 'BASE_DIR', os.getcwd())
        dry_run = options['dry_run']
        remove_pycache = not options['no_pycache']
        verbose = options['verbose']

        pyc_count = 0
        pycache_count = 0
        bytes_freed = 0

        for root, dirs, files in os.walk(base_path):
            # Skip hidden directories and virtual environments
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('venv', 'env', 'node_modules')]

            # Remove .pyc files
            for filename in files:
                if filename.endswith('.pyc') or filename.endswith('.pyo'):
                    filepath = os.path.join(root, filename)
                    file_size = os.path.getsize(filepath)

                    if verbose or dry_run:
                        action = "Would remove" if dry_run else "Removing"
                        self.stdout.write(f"{action}: {filepath}")

                    if not dry_run:
                        os.remove(filepath)

                    pyc_count += 1
                    bytes_freed += file_size

            # Remove __pycache__ directories
            if remove_pycache and '__pycache__' in dirs:
                pycache_path = os.path.join(root, '__pycache__')

                # Calculate size
                for dirpath, _, filenames in os.walk(pycache_path):
                    for f in filenames:
                        bytes_freed += os.path.getsize(os.path.join(dirpath, f))

                if verbose or dry_run:
                    action = "Would remove" if dry_run else "Removing"
                    self.stdout.write(f"{action}: {pycache_path}")

                if not dry_run:
                    shutil.rmtree(pycache_path)

                pycache_count += 1
                dirs.remove('__pycache__')

        # Summary
        size_str = self.format_size(bytes_freed)
        action = "Would remove" if dry_run else "Removed"

        self.stdout.write(self.style.SUCCESS(
            f"{action} {pyc_count} .pyc file(s) and {pycache_count} __pycache__ director(ies)"
        ))
        self.stdout.write(self.style.SUCCESS(f"Space freed: {size_str}"))

    def format_size(self, bytes_value):
        """Format bytes as human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.1f} TB"
