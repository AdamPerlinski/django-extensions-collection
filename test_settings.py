DEBUG = True
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
INSTALLED_APPS = ['django.contrib.contenttypes', 'django.contrib.auth', 'django_extensions']
SECRET_KEY = 'test-secret-key'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
