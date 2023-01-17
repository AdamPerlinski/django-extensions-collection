import django
from django.conf import settings

def pytest_configure():
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
            INSTALLED_APPS=['django.contrib.contenttypes', 'django.contrib.auth', 'django_extensions'],
            SECRET_KEY='test-secret-key',
            DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
        )
        django.setup()
