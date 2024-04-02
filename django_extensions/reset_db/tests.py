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
