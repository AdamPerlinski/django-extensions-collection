# Clean PYC

Remove Python bytecode files recursively.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.clean_pyc',
]
```

## Usage

```bash
python manage.py clean_pyc
```

## What It Removes

- `*.pyc` files
- `*.pyo` files
- `__pycache__` directories

## Output

```
Removed: /path/to/project/__pycache__/
Removed: /path/to/project/app/__pycache__/
Removed: /path/to/project/app/models.pyc

Cleaned 15 files and 5 directories.
```

## Options

### Dry Run

Preview what would be deleted:

```bash
python manage.py clean_pyc --dry-run
```

### Specific Path

Clean specific directory:

```bash
python manage.py clean_pyc --path /path/to/app
```

### Verbose

Show all files being removed:

```bash
python manage.py clean_pyc --verbose
```

### Include Optimization Files

Also remove `.pyo` files:

```bash
python manage.py clean_pyc --optimize
```

## When to Use

- Before committing to version control
- After major refactoring
- When debugging import issues
- Before deployment

## Cron Job

```bash
# Clean bytecode daily
0 0 * * * cd /path/to/project && python manage.py clean_pyc
```

## Git Hook

```bash
# .git/hooks/pre-commit
#!/bin/sh
python manage.py clean_pyc --dry-run
```

## License

MIT
