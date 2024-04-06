"""
generate_secret_key - Generate a new Django SECRET_KEY.

Usage:
    python manage.py generate_secret_key
    python manage.py generate_secret_key --length 64
"""

import secrets
import string
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Generate a new random SECRET_KEY for Django settings.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--length',
            type=int,
            default=50,
            help='Length of the secret key (default: 50).',
        )
        parser.add_argument(
            '--no-special',
            action='store_true',
            help='Exclude special characters.',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=1,
            help='Number of keys to generate.',
        )

    def generate_key(self, length, use_special=True):
        """Generate a random secret key."""
        chars = string.ascii_letters + string.digits
        if use_special:
            # Django's default special chars for SECRET_KEY
            chars += '!@#$%^&*(-_=+)'

        return ''.join(secrets.choice(chars) for _ in range(length))

    def handle(self, *args, **options):
        length = options['length']
        use_special = not options['no_special']
        count = options['count']

        if length < 16:
            self.stdout.write(self.style.WARNING(
                'Warning: Short keys are less secure. Recommended: 50+ characters.'
            ))

        for i in range(count):
            key = self.generate_key(length, use_special)

            if count > 1:
                self.stdout.write(f'{i + 1}. {key}')
            else:
                self.stdout.write(key)

        if count == 1:
            self.stdout.write(self.style.SUCCESS(
                '\nAdd this to your settings.py or environment variables:'
            ))
            self.stdout.write(f"SECRET_KEY = '{key}'")
