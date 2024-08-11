import os
import django
from django.conf import settings

def pytest_configure():
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'django.contrib.sessions',
                'django_extensions',
            ],
            MIDDLEWARE=[
                'django.middleware.common.CommonMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
            ],
            ROOT_URLCONF='test_urls',
            SECRET_KEY='test-secret-key-for-testing-only',
            USE_TZ=True,
            TIME_ZONE='UTC',
            DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
            TEMPLATES=[{
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.request',
                    ],
                },
            }],
            ENCRYPTION_KEY='0123456789abcdef0123456789abcdef',
        )
        django.setup()
