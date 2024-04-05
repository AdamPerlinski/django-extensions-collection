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
