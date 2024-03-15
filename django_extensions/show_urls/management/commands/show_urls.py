"""
show_urls - Display all URL patterns.

Usage:
    python manage.py show_urls
    python manage.py show_urls --format=table
    python manage.py show_urls --filter=api
"""

from django.core.management.base import BaseCommand
from django.urls import URLResolver, URLPattern
from django.conf import settings
import importlib


class Command(BaseCommand):
    help = 'Display all URL patterns defined in the project.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            default='table',
            choices=['table', 'json', 'simple'],
            help='Output format.',
        )
        parser.add_argument(
            '--filter',
            help='Filter URLs containing this string.',
        )
        parser.add_argument(
            '--unsorted',
            action='store_true',
            help='Do not sort URLs.',
        )

    def get_urls(self, urlpatterns, prefix=''):
        """Recursively extract all URL patterns."""
        urls = []

        for pattern in urlpatterns:
            if isinstance(pattern, URLResolver):
                # Nested URL patterns
                nested_prefix = prefix + str(pattern.pattern)
