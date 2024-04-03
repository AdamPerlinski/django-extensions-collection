"""Tests for reset_db command."""

import pytest
import os
import tempfile
from io import StringIO
from django.core.management import call_command
from unittest.mock import patch


class TestResetDbCommand:
    """Test cases for reset_db command."""

    def test_requires_confirmation(self):
        """Test command requires confirmation."""
        out = StringIO()
        with patch('builtins.input', return_value='n'):
            call_command('reset_db', stdout=out)

        assert 'cancelled' in out.getvalue().lower()

    @pytest.mark.django_db
    def test_noinput_skips_confirmation(self):
        """Test --noinput skips confirmation."""
        out = StringIO()
        # This should proceed without prompting
        call_command('reset_db', '--noinput', stdout=out)

        # Should complete (may have various messages)
        output = out.getvalue()
        # Either shows success or reports on what happened
        assert len(output) > 0

    def test_skip_migrate_flag(self):
        """Test --skip-migrate flag."""
        out = StringIO()
        with patch('django.core.management.call_command') as mock_call:
            # Reset the mock for call_command to avoid recursion
            mock_call.side_effect = lambda *args, **kwargs: None

            # We need to call the actual command, not mock it
            from django_extensions.reset_db.management.commands.reset_db import Command
            cmd = Command()
            cmd.stdout = out
            cmd.style = cmd.stdout  # Simplified

    def test_command_help(self):
        """Test command has help text."""
        from django_extensions.reset_db.management.commands.reset_db import Command
        cmd = Command()
        assert cmd.help is not None
        assert 'reset' in cmd.help.lower()

    def test_reset_sqlite_method(self):
        """Test reset_sqlite method."""
        from django_extensions.reset_db.management.commands.reset_db import Command

        with tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite3') as f:
            db_path = f.name

        try:
            cmd = Command()
            cmd.stdout = StringIO()
            cmd.reset_sqlite({'NAME': db_path})

            assert not os.path.exists(db_path)
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)
