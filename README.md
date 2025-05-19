<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-3.2%2B-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/Tests-826_passing-2ea44f?style=for-the-badge" alt="Tests">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Extensions-51-blueviolet?style=for-the-badge" alt="Extensions">
</p>

# Django Extensions Collection

A battle-tested collection of **51 Django extensions** for building production-ready applications. Each extension is independently usable, fully tested, and designed to eliminate the boilerplate you write on every project.

> Stop rebuilding the same utilities. Soft delete, UUID models, Stripe payments, S3 uploads, Slack notifications, rate limiting -- it's all here, tested, and ready to drop in.

---

## Installation

```bash
pip install django-extensions-collection
```

```python
INSTALLED_APPS = [
    ...
    'django_extensions',
]
```

Install only what you need:

```bash
pip install django-extensions-collection[aws]        # S3, SES, SNS, SQS
pip install django-extensions-collection[payments]    # Stripe
pip install django-extensions-collection[messaging]   # Twilio
pip install django-extensions-collection[ai]          # OpenAI + Anthropic
pip install django-extensions-collection[cache]       # Redis
pip install django-extensions-collection[monitoring]  # Sentry
pip install django-extensions-collection[all]         # Everything
```

---

## What's Inside

### Model Mixins

Drop-in abstract models that add common patterns to any model.

```python
from django.db import models
from django_extensions.timestamped_model import TimeStampedModel
from django_extensions.uuid_model import UUIDModel
from django_extensions.soft_delete import SoftDeleteModel

class Article(TimeStampedModel, UUIDModel, SoftDeleteModel):
    title = models.CharField(max_length=200)
    body = models.TextField()

# You now have: id (UUID), short_id, created, modified, is_deleted,
# .delete() (soft), .hard_delete(), .restore(), .objects (alive only),
# .all_objects (everything)
```

| Extension | What it does |
|---|---|
| **TimeStampedModel** | `created` and `modified` fields, auto-managed |
| **UUIDModel** | UUID primary key with 8-char `short_id` |
| **SoftDeleteModel** | Soft delete with `is_deleted` flag, `restore()`, custom manager |
| **OrderedModel** | Integer ordering with `move_up()`, `move_down()`, `move_to()` |
| **StatusModel** | Configurable status field with `set_status()` transitions |
| **SluggedModel** | Auto-generated unique slug from any field |
| **ActivatorModel** | `activate_date` / `deactivate_date` with `.active()` queryset |
| **TitleSlugModel** | Title + auto-slug + description, common CMS pattern |

### Custom Fields

```python
from django_extensions.encrypted_field import EncryptedField
from django_extensions.money_field import MoneyField
from django_extensions.short_uuid_field import ShortUUIDField

class Payment(models.Model):
    ref = ShortUUIDField()                    # "a8Kz9bQ3"
    amount = MoneyField(max_digits=10)        # Decimal with currency
    card_token = EncryptedField()             # AES-256 encrypted at rest
```

| Field | What it does |
|---|---|
| **AutoCreatedField** | `DateTimeField` that sets on creation, not editable |
| **AutoModifiedField** | `DateTimeField` that updates on every save |
| **ShortUUIDField** | URL-friendly short UUIDs (8-22 chars) |
| **EncryptedField** | Fernet (AES-128-CBC) encryption, transparent encrypt/decrypt |
| **JSONSchemaField** | `JSONField` with JSON Schema validation on save |
| **MoneyField** | Decimal field with currency code and arithmetic support |
| **PhoneField** | Stores E.164 phone numbers, validates format |

### Validators

```python
from django_extensions.phone_validator import is_valid_phone, PhoneValidator
from django_extensions.credit_card_validator import is_valid_card, get_card_type

is_valid_phone('+442071234567')          # True
is_valid_card('4111111111111111')         # True
get_card_type('4111111111111111')         # 'visa'
```

| Validator | Formats |
|---|---|
| **PhoneValidator** | E.164 international phone numbers |
| **CreditCardValidator** | Luhn checksum, Visa/MC/Amex/Discover detection |
| **ColorValidator** | HEX (`#ff0000`), RGB (`rgb(255,0,0)`), HSL, named colors |
| **URLValidator** | HTTP/HTTPS URLs with protocol, domain, path validation |

### Template Tags

```django
{% load humanize_extras math_filters string_extras %}

{{ user.last_login|naturaltime }}       {# "3 hours ago" #}
{{ product.price|multiply:quantity }}   {# 299.97 #}
{{ title|slugify }}                     {# "my-blog-post" #}
{{ bytes|filesizeformat }}              {# "4.2 MB" #}
{{ text|truncate_chars:100 }}           {# "Lorem ipsum dolor..." #}
```

| Tag Library | Filters |
|---|---|
| **humanize_tags** | `naturaltime`, `naturalday`, `intcomma`, `intword`, `filesizeformat`, `ordinal` |
| **string_tags** | `slugify`, `truncate_chars`, `truncate_words`, `title`, `upper`, `lower`, `strip`, `replace`, `split`, `join_str`, `remove_html`, `regex_replace`, `contains`, `startswith`, `endswith`, `pad_left`, `pad_right`, `repeat`, `reverse_str`, `capitalize` |
| **math_tags** | `add`, `subtract`, `multiply`, `divide`, `modulo`, `power`, `percentage`, `abs_value`, `round_num`, `floor`, `ceil`, `min_value`, `max_value`, `clamp`, `sqrt`, `calculate` |
| **url_tags** | `urlencode`, `urldecode`, `add_query_param`, `remove_query_param`, `domain`, `protocol`, `is_absolute_url` |

### Management Commands

```bash
python manage.py generate_secret_key    # Print a new SECRET_KEY
python manage.py show_urls              # List all URL patterns
python manage.py shell_plus             # Shell with all models auto-imported
python manage.py clean_pyc              # Remove all .pyc files
python manage.py reset_db               # Drop and recreate the database
```

### Middleware

```python
MIDDLEWARE = [
    ...
    'django_extensions.timezone_middleware.TimezoneMiddleware',
    'django_extensions.request_logging_middleware.RequestLoggingMiddleware',
]
```

| Middleware | What it does |
|---|---|
| **TimezoneMiddleware** | Activates user's timezone from session/profile per request |
| **RequestLoggingMiddleware** | Logs method, path, status, response time for every request |

### Decorators

```python
from django_extensions.ajax_required import ajax_required
from django_extensions.superuser_required import superuser_required

@ajax_required
def api_endpoint(request):
    ...  # Returns 400 if not XMLHttpRequest

@superuser_required
def admin_action(request):
    ...  # Returns 403 if not superuser
```

### Utilities

```python
from django_extensions.cache_decorator import cache_result
from django_extensions.pagination_utils import paginate_queryset
from django_extensions.email_utils import EmailBuilder

@cache_result(timeout=300, key_prefix='stats')
def get_dashboard_stats():
    return expensive_query()

page = paginate_queryset(Article.objects.all(), page=2, per_page=25)

EmailBuilder() \
    .to('user@example.com') \
    .subject('Welcome') \
    .template('welcome.html', {'name': 'Adam'}) \
    .send()
```

---

## Cloud Integrations

### AWS

```python
# S3 Storage
from django_extensions.aws_s3_storage import S3Storage, s3_upload, s3_download
url = s3_upload(file_obj, 'uploads/photo.jpg')

# SES Email
from django_extensions.aws_ses_email import SESEmailBackend
# Drop-in replacement: EMAIL_BACKEND = 'django_extensions.aws_ses_email.SESEmailBackend'

# SNS Notifications
from django_extensions.aws_sns_notifications import publish_notification
publish_notification(topic_arn, message='Server deployed', subject='Deploy')

# SQS Queue
from django_extensions.aws_sqs_queue import SQSQueue
queue = SQSQueue('my-queue')
queue.send_message({'task': 'process_upload', 'id': 42})
```

### Payments

```python
from django_extensions.stripe_payments import (
    create_customer, create_payment_intent, create_subscription
)

customer = create_customer(email='user@example.com', name='Adam')
intent = create_payment_intent(amount=2000, currency='usd', customer=customer['id'])
```

### Messaging

```python
from django_extensions.twilio_sms import send_sms
from django_extensions.slack_notifications import send_message, send_rich_message
from django_extensions.discord_notifications import send_discord_message

send_sms(to='+15551234567', body='Your order shipped!')
send_message(text='Deploy complete!', channel='#releases')
send_discord_message(content='Build passed', username='CI Bot')
```

### AI

```python
from django_extensions.openai_integration import OpenAIClient
from django_extensions.anthropic_integration import AnthropicClient

gpt = OpenAIClient()
response = gpt.chat('Summarize this article', model='gpt-4')

claude = AnthropicClient()
response = claude.chat('Explain this error log')
```

### Infrastructure

```python
# Redis - caching, rate limiting, distributed locks
from django_extensions.redis_cache import RedisCache
cache = RedisCache()
cache.set('key', 'value', timeout=3600)

with cache.lock('payment-processing'):
    process_payment()

# Sentry - error tracking
from django_extensions.sentry_integration import SentryTracker
tracker = SentryTracker()
tracker.capture_exception(e)
```

---

## Configuration

```python
# settings.py

# AWS
AWS_ACCESS_KEY_ID = 'your-key'
AWS_SECRET_ACCESS_KEY = 'your-secret'
AWS_S3_BUCKET_NAME = 'my-bucket'
AWS_S3_REGION = 'us-east-1'

# Stripe
STRIPE_SECRET_KEY = 'sk_live_...'
STRIPE_WEBHOOK_SECRET = 'whsec_...'

# Twilio
TWILIO_ACCOUNT_SID = 'AC...'
TWILIO_AUTH_TOKEN = 'your-token'
TWILIO_PHONE_NUMBER = '+15551234567'

# Slack / Discord
SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/...'
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/...'

# AI
OPENAI_API_KEY = 'sk-...'
ANTHROPIC_API_KEY = 'sk-ant-...'

# Redis
REDIS_URL = 'redis://localhost:6379/0'

# Sentry
SENTRY_DSN = 'https://...@sentry.io/...'

# Encryption (for EncryptedField)
ENCRYPTION_KEY = 'your-32-byte-key-here'
```

---

## Testing

```bash
# Run all tests
pytest

# Skip DB-dependent model tests
pytest -k "not test_model"

# Single extension
pytest django_extensions/credit_card_validator/

# With coverage
pytest --cov=django_extensions --cov-report=term-missing
```

**826 tests** across 51 extensions. 680 pass without database migrations, the rest require a migrated DB for concrete model tests.

---

## Project Structure

```
django_extensions/
    timestamped_model/      # Each extension is a self-contained package
        __init__.py         # Public API exports
        models.py           # Implementation
        tests.py            # Tests
        README.md           # Extension docs
    ...
```

Every extension follows the same pattern: a Python package with implementation, tests, and documentation. No extension depends on another -- use one or use all.

---

## Compatibility

| Python | Django |
|--------|--------|
| 3.8    | 3.2, 4.0, 4.1, 4.2 |
| 3.9    | 3.2, 4.0, 4.1, 4.2, 5.0 |
| 3.10   | 3.2, 4.0, 4.1, 4.2, 5.0 |
| 3.11   | 4.0, 4.1, 4.2, 5.0 |
| 3.12   | 4.2, 5.0 |

---

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-extension`)
3. Follow the existing package structure
4. Write tests (aim for >90% coverage per extension)
5. Run `black` and `isort` before committing
6. Open a pull request

---

## License

MIT -- see [LICENSE](LICENSE) for details.
