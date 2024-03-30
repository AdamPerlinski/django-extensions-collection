"""
reset_db - Reset the database.

Usage:
    python manage.py reset_db
    python manage.py reset_db --noinput
"""

import os
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings


class Command(BaseCommand):
    help = 'Reset the database by dropping all tables and recreating them.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput',
            '--no-input',
            action='store_true',
            help='Do not prompt for confirmation.',
        )
        parser.add_argument(
            '--skip-migrate',
            action='store_true',
            help='Skip running migrations after reset.',
        )

    def handle(self, *args, **options):
        db_settings = settings.DATABASES.get('default', {})
        engine = db_settings.get('ENGINE', '')

        if not options['noinput']:
            confirm = input(
                'Are you sure you want to reset the database? '
                'This will delete ALL data. [y/N] '
