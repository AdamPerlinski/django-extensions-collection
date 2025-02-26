"""
Django Extensions Collection - 51 Django extensions for production-ready applications.

This package provides reusable Django components including:

Model Mixins (8):
- TimeStampedModel, UUIDModel, SoftDeleteModel, OrderedModel
- StatusModel, SluggedModel, ActivatorModel, TitleSlugModel

Custom Fields (7):
- AutoCreatedField, AutoModifiedField, ShortUUIDField
- EncryptedField, JSONSchemaField, MoneyField, PhoneField

Managers (3):
- SoftDeleteManager, ActiveManager, RandomManager

Validators (4):
- PhoneValidator, CreditCardValidator, ColorValidator, URLValidator

Template Tags (4):
- humanize_tags, url_tags, math_tags, string_tags

Management Commands (5):
- shell_plus, show_urls, clean_pyc, reset_db, generate_secret_key

Middleware (2):
- TimezoneMiddleware, RequestLoggingMiddleware

Decorators (3):
- ajax_required, anonymous_required, superuser_required

Utilities (3):
- cache_decorator, pagination_utils, email_utils

Cloud - AWS (4):
- aws_s3_storage, aws_ses_email, aws_sns_notifications, aws_sqs_queue

Cloud - Payments (1):
- stripe_payments

Cloud - Messaging (3):
- twilio_sms, slack_notifications, discord_notifications

Cloud - AI (2):
- openai_integration, anthropic_integration

Cloud - Infrastructure (2):
- redis_cache, sentry_integration
"""

__version__ = '1.0.0'
__author__ = 'Django Extensions'

default_app_config = 'django_extensions.apps.DjangoExtensionsConfig'
