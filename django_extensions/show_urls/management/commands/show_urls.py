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
                urls.extend(self.get_urls(pattern.url_patterns, nested_prefix))
            elif isinstance(pattern, URLPattern):
                url_info = {
                    'pattern': prefix + str(pattern.pattern),
                    'name': pattern.name or '',
                    'view': self.get_view_name(pattern.callback),
                }
                urls.append(url_info)

        return urls

    def get_view_name(self, callback):
        """Get the name of the view function or class."""
        if hasattr(callback, 'view_class'):
            return f"{callback.view_class.__module__}.{callback.view_class.__name__}"
        if hasattr(callback, '__name__'):
            module = getattr(callback, '__module__', '')
            return f"{module}.{callback.__name__}"
        return str(callback)

    def format_table(self, urls):
        """Format URLs as a table."""
        if not urls:
            return "No URLs found."

        # Calculate column widths
        pattern_width = max(len(u['pattern']) for u in urls)
        name_width = max(len(u['name']) for u in urls)
        view_width = max(len(u['view']) for u in urls)

        # Header
        header = f"{'Pattern':<{pattern_width}} | {'Name':<{name_width}} | {'View':<{view_width}}"
        separator = '-' * len(header)

        lines = [header, separator]
        for url in urls:
            line = f"{url['pattern']:<{pattern_width}} | {url['name']:<{name_width}} | {url['view']:<{view_width}}"
            lines.append(line)

        return '\n'.join(lines)

    def format_json(self, urls):
        """Format URLs as JSON."""
        import json
        return json.dumps(urls, indent=2)

    def format_simple(self, urls):
        """Format URLs as simple list."""
        lines = []
        for url in urls:
            name_part = f" [{url['name']}]" if url['name'] else ""
            lines.append(f"{url['pattern']}{name_part}")
        return '\n'.join(lines)

    def handle(self, *args, **options):
        # Get root URLconf
        root_urlconf = settings.ROOT_URLCONF
        urlconf = importlib.import_module(root_urlconf)
        urlpatterns = getattr(urlconf, 'urlpatterns', [])

        # Extract all URLs
        urls = self.get_urls(urlpatterns)

        # Filter if requested
        if options['filter']:
            filter_str = options['filter'].lower()
            urls = [u for u in urls if filter_str in u['pattern'].lower() or
                    filter_str in u['name'].lower()]

        # Sort unless --unsorted
        if not options['unsorted']:
            urls.sort(key=lambda u: u['pattern'])

        # Format output
        format_method = {
            'table': self.format_table,
            'json': self.format_json,
            'simple': self.format_simple,
        }[options['format']]

        self.stdout.write(format_method(urls))
        self.stdout.write(self.style.SUCCESS(f'\nTotal: {len(urls)} URL patterns'))
