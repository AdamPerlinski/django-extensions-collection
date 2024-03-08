"""Tests for shell_plus command."""

import pytest
from io import StringIO
from django.core.management import call_command
from unittest.mock import patch, MagicMock


class TestShellPlusCommand:
    """Test cases for shell_plus command."""

    def test_print_imports(self):
        """Test --print-imports flag."""
        out = StringIO()
        call_command('shell_plus', '--print-imports', stdout=out)
        output = out.getvalue()

        assert 'Auto-imported' in output

    def test_get_imports(self):
        """Test get_imports method."""
        from django_extensions.shell_plus.management.commands.shell_plus import Command
