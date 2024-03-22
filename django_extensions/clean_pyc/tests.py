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
