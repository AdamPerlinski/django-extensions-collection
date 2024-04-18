# Generate Secret Key

Generate cryptographically secure Django SECRET_KEY values.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.generate_secret_key',
]
```

## Usage

```bash
python manage.py generate_secret_key
```

Output:

```
y23rC)SxGh2gHi4GRk8ptWzO6nlgC*DxRhdi_We3ZLa^KjJ9*m

Add this to your settings.py or environment variables:
SECRET_KEY = 'y23rC)SxGh2gHi4GRk8ptWzO6nlgC*DxRhdi_We3ZLa^KjJ9*m'
```

## Options

### Key Length

```bash
# Default: 50 characters
python manage.py generate_secret_key

# Custom length
python manage.py generate_secret_key --length 64
```

### No Special Characters

```bash
python manage.py generate_secret_key --no-special
```

### Multiple Keys

```bash
python manage.py generate_secret_key --count 5
```

## Character Set

Default characters:
- Lowercase: `a-z`
- Uppercase: `A-Z`
- Digits: `0-9`
- Special: `!@#$%^&*(-_=+)`

## Environment Variable

```bash
# Generate and export
export SECRET_KEY=$(python manage.py generate_secret_key)

# Or save to .env
echo "SECRET_KEY='$(python manage.py generate_secret_key)'" >> .env
```

## Security Best Practices

1. **Never commit** SECRET_KEY to version control
2. **Use environment variables** in production
3. **Rotate keys** when compromised
4. **Use 50+ characters** for adequate entropy

## Programmatic Usage

```python
from django_extensions.generate_secret_key.management.commands.generate_secret_key import Command

cmd = Command()
key = cmd.generate_key(length=50, use_special=True)
print(key)
```

## License

MIT
