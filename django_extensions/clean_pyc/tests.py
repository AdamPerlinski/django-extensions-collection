"""Tests for clean_pyc command."""

import pytest
import os
import tempfile
from io import StringIO
from django.core.management import call_command


class TestCleanPycCommand:
    """Test cases for clean_pyc command."""

    def test_dry_run(self):
        """Test --dry-run flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a .pyc file
            pyc_file = os.path.join(tmpdir, 'test.pyc')
            with open(pyc_file, 'w') as f:
                f.write('test')

            out = StringIO()
            call_command('clean_pyc', '--path', tmpdir, '--dry-run', stdout=out)
            output = out.getvalue()

            # File should still exist
            assert os.path.exists(pyc_file)
            assert 'Would remove' in output

    def test_removes_pyc(self):
        """Test .pyc file removal."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a .pyc file
            pyc_file = os.path.join(tmpdir, 'test.pyc')
            with open(pyc_file, 'w') as f:
                f.write('test')

            out = StringIO()
            call_command('clean_pyc', '--path', tmpdir, '--verbose', stdout=out)

            # File should be removed
            assert not os.path.exists(pyc_file)

    def test_removes_pycache(self):
        """Test __pycache__ directory removal."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create __pycache__ directory
            pycache_dir = os.path.join(tmpdir, '__pycache__')
            os.makedirs(pycache_dir)
            pyc_file = os.path.join(pycache_dir, 'test.cpython-39.pyc')
            with open(pyc_file, 'w') as f:
                f.write('test')

            out = StringIO()
            call_command('clean_pyc', '--path', tmpdir, stdout=out)

            # Directory should be removed
            assert not os.path.exists(pycache_dir)

    def test_no_pycache_flag(self):
        """Test --no-pycache flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create __pycache__ directory
            pycache_dir = os.path.join(tmpdir, '__pycache__')
            os.makedirs(pycache_dir)

            out = StringIO()
            call_command('clean_pyc', '--path', tmpdir, '--no-pycache', stdout=out)

            # Directory should still exist
            assert os.path.exists(pycache_dir)

    def test_summary_output(self):
        """Test summary output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = StringIO()
            call_command('clean_pyc', '--path', tmpdir, stdout=out)
            output = out.getvalue()

            assert 'Removed' in output or 'file(s)' in output

    def test_command_help(self):
        """Test command has help text."""
        from django_extensions.clean_pyc.management.commands.clean_pyc import Command
        cmd = Command()
        assert cmd.help is not None
