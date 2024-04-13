"""Tests for generate_secret_key command."""

import pytest
from io import StringIO
from django.core.management import call_command


class TestGenerateSecretKeyCommand:
    """Test cases for generate_secret_key command."""

    def test_default_length(self):
        """Test default key length."""
        out = StringIO()
        call_command('generate_secret_key', stdout=out)
        output = out.getvalue()

        # First line should be the key (50 chars default)
        key = output.split('\n')[0]
        assert len(key) == 50

    def test_custom_length(self):
        """Test custom key length."""
        out = StringIO()
        call_command('generate_secret_key', '--length', '64', stdout=out)
        output = out.getvalue()

        key = output.split('\n')[0]
        assert len(key) == 64

    def test_no_special_chars(self):
        """Test --no-special flag."""
        out = StringIO()
        call_command('generate_secret_key', '--no-special', stdout=out)
        output = out.getvalue()

