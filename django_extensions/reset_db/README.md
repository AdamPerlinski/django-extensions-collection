# Reset DB

Reset database with confirmation.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.reset_db',
]
```

## Usage

```bash
python manage.py reset_db
```

## Confirmation

```
You have requested a database reset.
This will IRREVERSIBLY DESTROY all data in database 'myproject'.
Are you sure you want to do this? (yes/no): yes

Database reset successfully.
```

## Options

### No Input

Skip confirmation (for scripts):

```bash
python manage.py reset_db --noinput
```

### Specific Database

Reset specific database:

```bash
python manage.py reset_db --database secondary
```

### Close Connections

Force close existing connections:

```bash
python manage.py reset_db --close-sessions
```

### Create Only

Just create database, don't drop:

```bash
python manage.py reset_db --create-only
```

## Database Support

| Database | Supported |
|----------|-----------|
| PostgreSQL | Yes |
| MySQL | Yes |
| SQLite | Yes |
| Oracle | Yes |

## What It Does

1. Drops the existing database
2. Creates a new empty database
3. Does NOT run migrations

## After Reset

Run migrations to recreate tables:

```bash
python manage.py reset_db --noinput
python manage.py migrate
python manage.py createsuperuser
```

## Development Script

```bash
#!/bin/bash
python manage.py reset_db --noinput
python manage.py migrate
python manage.py loaddata initial_data.json
echo "Database reset complete!"
```

## Safety

- Never use in production without backups
- `--noinput` flag requires explicit use
- Logs all reset operations

## License

MIT
