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

        cmd = Command()
        imports = cmd.get_imports()

        # Should include common utilities
        assert 'Q' in imports
        assert 'F' in imports
        assert 'timezone' in imports
        assert 'settings' in imports

    def test_no_imports_flag(self):
        """Test --no-imports flag."""
        out = StringIO()
        with patch('code.interact') as mock_interact:
            call_command('shell_plus', '--no-imports', '--plain', stdout=out)
            # Should be called with empty dict
            mock_interact.assert_called_once()
            called_imports = mock_interact.call_args[1]['local']
            assert called_imports == {}

    @patch('code.interact')
    def test_plain_shell(self, mock_interact):
        """Test --plain flag uses code.interact."""
        out = StringIO()
        call_command('shell_plus', '--plain', stdout=out)
        mock_interact.assert_called_once()

    def test_command_help(self):
        """Test command has help text."""
        from django_extensions.shell_plus.management.commands.shell_plus import Command
        cmd = Command()
        assert cmd.help is not None
        assert 'shell' in cmd.help.lower()
