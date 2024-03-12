# Shell Plus

Enhanced Django shell with auto-imports.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.shell_plus',
]
```

## Usage

```bash
python manage.py shell_plus
```

## Features

### Auto-Imports

All models are automatically imported:

```python
# Instead of:
from myapp.models import User, Article, Comment

# Just use:
>>> User.objects.count()
>>> Article.objects.first()
```

### Startup Banner

Shows imported models:

```
# Shell Plus
# Auto-imported models:
#   from django.contrib.auth.models import User, Group
#   from myapp.models import Article, Comment
#   from blog.models import Post, Category
```

### Enhanced Features

- Tab completion
- Syntax highlighting
- History persistence
- Multi-line editing

## Configuration

```python
# settings.py

SHELL_PLUS_IMPORTS = [
    'from datetime import datetime, timedelta',
    'from django.db.models import Q, F, Count',
]

SHELL_PLUS_DONT_LOAD = ['myapp.models.LargeModel']

SHELL_PLUS_MODEL_ALIASES = {
    'User': 'U',
    'Article': 'A',
}
```

## IPython Support

If IPython is installed, it's used automatically:

```bash
pip install ipython
python manage.py shell_plus
```

## bpython Support

```bash
pip install bpython
python manage.py shell_plus --bpython
```

## Print SQL Queries

```bash
python manage.py shell_plus --print-sql
```

Shows SQL for every query:

```python
>>> User.objects.count()
SELECT COUNT(*) FROM auth_user
42
```

## License

MIT
