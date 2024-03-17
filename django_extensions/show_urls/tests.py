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
