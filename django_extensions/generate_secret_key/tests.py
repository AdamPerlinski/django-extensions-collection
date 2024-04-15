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

        key = output.split('\n')[0]
        special_chars = '!@#$%^&*(-_=+)'
        assert not any(c in key for c in special_chars)

    def test_with_special_chars(self):
        """Test keys include special chars by default."""
        # Generate multiple keys to increase chance of special chars
        found_special = False
        for _ in range(20):
            out = StringIO()
            call_command('generate_secret_key', stdout=out)
            key = out.getvalue().split('\n')[0]
            special_chars = '!@#$%^&*(-_=+)'
            if any(c in key for c in special_chars):
                found_special = True
                break

        # Statistically, we should find special chars
        assert found_special

    def test_multiple_keys(self):
        """Test generating multiple keys."""
        out = StringIO()
        call_command('generate_secret_key', '--count', '5', stdout=out)
        output = out.getvalue()

        # Should have 5 numbered lines
        lines = [l for l in output.split('\n') if l.strip() and l[0].isdigit()]
        assert len(lines) == 5

    def test_keys_are_unique(self):
        """Test generated keys are unique."""
        keys = set()
        for _ in range(10):
            out = StringIO()
            call_command('generate_secret_key', stdout=out)
            key = out.getvalue().split('\n')[0]
            keys.add(key)

        assert len(keys) == 10

    def test_short_key_warning(self):
        """Test warning for short keys."""
        out = StringIO()
        call_command('generate_secret_key', '--length', '8', stdout=out)
        output = out.getvalue()

        assert 'Warning' in output or 'short' in output.lower()

    def test_command_help(self):
        """Test command has help text."""
        from django_extensions.generate_secret_key.management.commands.generate_secret_key import Command
        cmd = Command()
        assert cmd.help is not None
