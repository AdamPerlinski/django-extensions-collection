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
            )
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('Reset cancelled.'))
                return

        if 'sqlite3' in engine:
            self.reset_sqlite(db_settings)
        elif 'postgresql' in engine:
            self.reset_postgresql(db_settings)
        elif 'mysql' in engine:
            self.reset_mysql(db_settings)
        else:
            raise CommandError(f'Unsupported database engine: {engine}')

        if not options['skip_migrate']:
            self.stdout.write('Running migrations...')
            call_command('migrate', verbosity=0)
            self.stdout.write(self.style.SUCCESS('Migrations complete.'))

        self.stdout.write(self.style.SUCCESS('Database reset complete.'))

    def reset_sqlite(self, db_settings):
        """Reset SQLite database by deleting the file."""
        db_path = db_settings.get('NAME')

        if db_path and db_path != ':memory:' and os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write(f'Deleted database file: {db_path}')
        else:
            self.stdout.write('No database file to delete.')

    def reset_postgresql(self, db_settings):
        """Reset PostgreSQL database by dropping and recreating."""
        from django.db import connection

        db_name = db_settings.get('NAME')

        with connection.cursor() as cursor:
            # Terminate other connections
            cursor.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{db_name}'
                AND pid <> pg_backend_pid()
            """)

            # Drop all tables
            cursor.execute("""
                DROP SCHEMA public CASCADE;
                CREATE SCHEMA public;
                GRANT ALL ON SCHEMA public TO public;
            """)

        self.stdout.write(f'Reset PostgreSQL database: {db_name}')

    def reset_mysql(self, db_settings):
        """Reset MySQL database by dropping all tables."""
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute('SET FOREIGN_KEY_CHECKS = 0')

            cursor.execute('SHOW TABLES')
            tables = cursor.fetchall()

            for table in tables:
                cursor.execute(f'DROP TABLE IF EXISTS `{table[0]}`')

            cursor.execute('SET FOREIGN_KEY_CHECKS = 1')

        self.stdout.write(f'Reset MySQL database: {db_settings.get("NAME")}')
