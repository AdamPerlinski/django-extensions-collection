"""Tests for show_urls command."""

import pytest
from io import StringIO
from django.core.management import call_command


class TestShowUrlsCommand:
    """Test cases for show_urls command."""

    def test_basic_output(self):
        """Test basic command output."""
        out = StringIO()
        call_command('show_urls', stdout=out)
        output = out.getvalue()

        assert 'Total:' in output

    def test_table_format(self):
        """Test table format output."""
        out = StringIO()
        call_command('show_urls', '--format=table', stdout=out)
        output = out.getvalue()

        assert 'Pattern' in output
        assert 'Name' in output
        assert 'View' in output

    def test_json_format(self):
        """Test JSON format output."""
        import json
        out = StringIO()
        call_command('show_urls', '--format=json', stdout=out)
        output = out.getvalue()

        # Should be valid JSON (before the "Total:" line)
        json_part = output.split('\n\nTotal:')[0]
        parsed = json.loads(json_part)
        assert isinstance(parsed, list)

    def test_simple_format(self):
        """Test simple format output."""
        out = StringIO()
        call_command('show_urls', '--format=simple', stdout=out)
        output = out.getvalue()

        # Simple format should just have patterns
        assert 'Pattern' not in output

    def test_filter_option(self):
        """Test --filter option."""
        out = StringIO()
        call_command('show_urls', '--filter=home', stdout=out)
        output = out.getvalue()

        # Should only show URLs matching filter
        lines = [l for l in output.split('\n') if l and not l.startswith('Total')]
        for line in lines:
            if line.strip() and not line.startswith('-'):
                # Skip header line
                if 'Pattern' not in line:
                    assert 'home' in line.lower() or 'Name' in line

    def test_get_urls(self):
        """Test get_urls method."""
        from django_extensions.show_urls.management.commands.show_urls import Command

        cmd = Command()
        from django.conf import settings
        import importlib

        urlconf = importlib.import_module(settings.ROOT_URLCONF)
        urlpatterns = getattr(urlconf, 'urlpatterns', [])

        urls = cmd.get_urls(urlpatterns)
        assert isinstance(urls, list)

    def test_command_help(self):
        """Test command has help text."""
        from django_extensions.show_urls.management.commands.show_urls import Command
        cmd = Command()
        assert cmd.help is not None
