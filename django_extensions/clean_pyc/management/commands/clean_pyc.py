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
