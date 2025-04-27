# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added

#### Model Mixins (8)
- `timestamped_model` - Auto `created` and `modified` fields
- `uuid_model` - UUID primary key with `short_id` property
- `soft_delete_model` - Soft delete with `is_deleted` flag
- `ordered_model` - Ordering with `move_up`/`move_down`
- `status_model` - Status field with transitions
- `slugged_model` - Auto-generated slug from title
- `activator_model` - Activate/deactivate date ranges
- `title_slug_model` - Title + slug + description combo

#### Custom Fields (7)
- `auto_created_field` - Auto-set on creation
- `auto_modified_field` - Auto-update on save
- `short_uuid_field` - Short readable UUIDs
- `encrypted_field` - Fernet-encrypted storage
- `json_schema_field` - JSON with schema validation
- `money_field` - Currency-aware money storage
- `phone_field` - Validated phone numbers

#### Managers (3)
- `soft_delete_manager` - Filter deleted objects
- `active_manager` - Filter by `is_active`
- `random_manager` - Random object selection

#### Validators (4)
- `phone_validator` - E.164 phone validation
- `credit_card_validator` - Luhn algorithm + card type
- `color_validator` - HEX, RGB, HSL colors
- `url_validator` - URL format validation

#### Template Tags (4)
- `humanize_tags` - `naturaltime`, `filesizeformat`, `intcomma`
- `url_tags` - URL manipulation filters
- `math_tags` - Math operations in templates
- `string_tags` - String manipulation filters

#### Management Commands (5)
- `shell_plus` - Enhanced shell with auto-imports
- `show_urls` - Display all URL patterns
- `clean_pyc` - Remove `.pyc` files
- `reset_db` - Reset database
- `generate_secret_key` - Generate new SECRET_KEY

#### Middleware (2)
- `timezone_middleware` - Per-user timezone activation
- `request_logging_middleware` - Request/response logging

#### Decorators (3)
- `ajax_required` - Require AJAX requests
- `anonymous_required` - Require unauthenticated user
- `superuser_required` - Require superuser

#### Utilities (3)
- `cache_decorator` - Function result caching
- `pagination_utils` - Enhanced pagination
- `email_utils` - Email builder pattern

#### Cloud - AWS (4)
- `aws_s3_storage` - S3 file storage backend
- `aws_ses_email` - SES email backend
- `aws_sns_notifications` - SNS push notifications
- `aws_sqs_queue` - SQS message queue

#### Cloud - Payments (1)
- `stripe_payments` - Stripe payment processing

#### Cloud - Messaging (3)
- `twilio_sms` - SMS/WhatsApp via Twilio
- `slack_notifications` - Slack webhook messages
- `discord_notifications` - Discord webhook messages

#### Cloud - AI (2)
- `openai_integration` - OpenAI GPT API
- `anthropic_integration` - Anthropic Claude API

#### Cloud - Infrastructure (2)
- `redis_cache` - Redis caching + rate limiting
- `sentry_integration` - Sentry error tracking

### Tests
- 683 tests total
- 564 tests without database dependencies
- Full coverage for all extensions
