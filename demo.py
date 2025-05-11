#!/usr/bin/env python
"""
Demo script showcasing Django Extensions in action.
Run with: python demo.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from datetime import datetime, timedelta
from decimal import Decimal


def header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def demo_validators():
    """Demo validators."""
    header("VALIDATORS")

    from django_extensions.phone_validator import PhoneNumberValidator, is_valid_phone
    from django_extensions.credit_card_validator import CreditCardValidator, is_valid_card
    from django_extensions.color_validator import ColorValidator, is_valid_color
    from django_extensions.url_validator import URLValidator, is_valid_url

    print("\n📞 Phone Validator:")
    phones = ['+15551234567', '555-123-4567', '123', 'invalid']
    for phone in phones:
        valid = is_valid_phone(phone)
        print(f"   {phone:20} -> {'✅ Valid' if valid else '❌ Invalid'}")

    print("\n💳 Credit Card Validator:")
    cards = ['4111111111111111', '5500000000000004', '1234567890123456']
    for card in cards:
        valid = is_valid_card(card)
        card_type = ""
        if valid:
            if card.startswith('4'):
                card_type = "(Visa)"
            elif card.startswith('5'):
                card_type = "(Mastercard)"
        print(f"   {card} -> {'✅ Valid ' + card_type if valid else '❌ Invalid'}")

    print("\n🎨 Color Validator:")
    colors = ['#FF5733', '#fff', 'rgb(255, 100, 50)', 'hsl(120, 50%, 50%)', 'invalid']
    for color in colors:
        valid = is_valid_color(color)
        print(f"   {color:25} -> {'✅ Valid' if valid else '❌ Invalid'}")

    print("\n🔗 URL Validator:")
    urls = ['https://example.com', 'http://localhost:8000', 'ftp://files.com', 'not-a-url']
    for url in urls:
        valid = is_valid_url(url)
        print(f"   {url:30} -> {'✅ Valid' if valid else '❌ Invalid'}")


def demo_template_tags():
    """Demo template tags."""
    header("TEMPLATE TAGS")

    from django_extensions.humanize_tags.templatetags import (
        naturaltime, filesizeformat, oxford_comma, intcomma
    )
    from django_extensions.math_tags.templatetags import (
        add, subtract, multiply, divide, percentage
    )
    from django_extensions.string_tags.templatetags import (
        slugify, title, remove_html, truncate_chars
    )

    print("\n⏰ Humanize Tags:")
    now = datetime.now()
    times = [
        now - timedelta(seconds=30),
        now - timedelta(minutes=5),
        now - timedelta(hours=2),
        now - timedelta(days=1),
    ]
    for t in times:
        print(f"   {t.strftime('%H:%M:%S')} -> {naturaltime(t)}")

    print("\n📁 File Sizes:")
    sizes = [512, 1024, 1048576, 1073741824]
    for size in sizes:
        print(f"   {size:15} bytes -> {filesizeformat(size)}")

    print("\n🔢 Math Operations:")
    print(f"   10 + 5 = {add(10, 5)}")
    print(f"   10 - 5 = {subtract(10, 5)}")
    print(f"   10 × 5 = {multiply(10, 5)}")
    print(f"   10 ÷ 5 = {divide(10, 5)}")
    print(f"   25 of 100 = {percentage(25, 100)}%")

    print("\n📝 String Operations:")
    text = "Hello World! This is a Test"
    html = "<p>Hello <strong>World</strong></p>"
    print(f"   Slugify: '{text}' -> '{slugify(text)}'")
    print(f"   Title:   'hello world' -> '{title('hello world')}'")
    print(f"   Strip HTML: '{html}' -> '{remove_html(html)}'")
    print(f"   Truncate: '{text}' -> '{truncate_chars(text, 15)}...'")

    print("\n📋 Oxford Comma:")
    items = ['apples', 'oranges', 'bananas']
    print(f"   {items} -> '{oxford_comma(items)}'")


def demo_decorators():
    """Demo decorators."""
    header("DECORATORS")

    from django_extensions.cache_decorator import cache_result

    print("\n🚀 Cache Decorator:")

    call_count = 0

    @cache_result(timeout=60, key_prefix='demo')
    def expensive_calculation(x, y):
        nonlocal call_count
        call_count += 1
        return x * y + x ** 2

    # Note: Without actual cache backend, this just shows the decorator works
    result1 = expensive_calculation(5, 3)
    print(f"   expensive_calculation(5, 3) = {result1}")
    print(f"   Function was called {call_count} time(s)")

    from django_extensions.ajax_required import ajax_required
    from django_extensions.superuser_required import superuser_required

    print("\n🔒 View Decorators (available):")
    print("   @ajax_required - Requires AJAX request")
    print("   @superuser_required - Requires superuser")
    print("   @anonymous_required - Requires unauthenticated user")


def demo_pagination():
    """Demo pagination utilities."""
    header("PAGINATION UTILITIES")

    from django_extensions.pagination_utils import Paginator, paginate, get_page_range

    print("\n📄 Paginator:")
    items = list(range(1, 101))  # 100 items
    paginator = Paginator(items, per_page=10)

    print(f"   Total items: {paginator.count}")
    print(f"   Items per page: {paginator.per_page}")
    print(f"   Total pages: {paginator.num_pages}")

    page = paginator.page(1)
    print(f"   Page 1 items: {list(page.object_list)[:5]}...")
    print(f"   Has next: {page.has_next()}")
    print(f"   Has previous: {page.has_previous()}")

    print("\n📊 Page Range:")
    page5 = paginator.page(5)
    page_range = get_page_range(page5, window=2)
    print(f"   Current page 5, window 2: {page_range}")


def demo_email_utils():
    """Demo email utilities."""
    header("EMAIL UTILITIES")

    from django_extensions.email_utils import EmailBuilder

    print("\n📧 EmailBuilder (fluent interface):")

    email = (EmailBuilder()
        .subject("Welcome to our platform!")
        .to("user@example.com")
        .cc("manager@example.com")
        .from_email("noreply@example.com")
        .text("Hello! Welcome to our platform.")
        .html("<h1>Hello!</h1><p>Welcome to our platform.</p>")
        .attach("report.pdf", b"PDF content here", "application/pdf")
        .header("X-Priority", "1"))

    print(f"   Subject: {email._subject}")
    print(f"   To: {email._to}")
    print(f"   CC: {email._cc}")
    print(f"   From: {email._from_email}")
    print(f"   Has HTML: {bool(email._html_content)}")
    print(f"   Attachments: {len(email._attachments)}")
    print("   (Email built but not sent - no SMTP configured)")


def demo_models():
    """Demo model mixins (without database)."""
    header("MODEL MIXINS (Structure Demo)")

    print("\n🏗️ Available Model Mixins:")

    mixins = [
        ("TimeStampedModel", "created, modified fields with auto-update"),
        ("UUIDModel", "UUID primary key with short_id property"),
        ("SoftDeleteModel", "Soft delete with is_deleted flag"),
        ("OrderedModel", "Ordering with move_up/move_down methods"),
        ("StatusModel", "Status field with transitions"),
        ("SluggedModel", "Auto-generated slug from title"),
        ("ActivatorModel", "activate_date, deactivate_date fields"),
        ("TitleSlugModel", "Title + slug + description"),
    ]

    for name, desc in mixins:
        print(f"   📦 {name}")
        print(f"      {desc}")


def demo_management_commands():
    """Demo management commands."""
    header("MANAGEMENT COMMANDS")

    print("\n🔧 Available Commands:")

    commands = [
        ("shell_plus", "Enhanced shell with auto-imports"),
        ("show_urls", "Display all URL patterns"),
        ("clean_pyc", "Remove .pyc files recursively"),
        ("reset_db", "Reset database (with confirmation)"),
        ("generate_secret_key", "Generate new Django secret key"),
    ]

    for name, desc in commands:
        print(f"   ./manage.py {name}")
        print(f"      {desc}")

    # Actually run generate_secret_key
    print("\n🔑 Generating Secret Key:")
    from django_extensions.generate_secret_key.management.commands.generate_secret_key import Command
    from io import StringIO
    cmd = Command()
    out = StringIO()
    cmd.stdout = out
    cmd.style = type('Style', (), {'SUCCESS': lambda self, x: x, 'WARNING': lambda self, x: x})()
    cmd.handle(length=50, no_special=False, count=1)
    key = out.getvalue().strip().split('\n')[0]
    print(f"   {key[:50]}...")


def demo_cloud_integrations():
    """Demo cloud integrations (mocked)."""
    header("CLOUD INTEGRATIONS")

    print("\n☁️ AWS Integrations:")
    print("   📦 aws_s3_storage - S3 file storage backend")
    print("      from django_extensions.aws_s3_storage import S3Storage, s3_upload")
    print("      storage = S3Storage(bucket_name='my-bucket')")
    print("      url = s3_upload(file_obj, 'path/to/file.txt')")

    print("\n   📧 aws_ses_email - SES email backend")
    print("      from django_extensions.aws_ses_email import send_ses_email")
    print("      send_ses_email(subject='Hi', body='Hello', to=['user@example.com'])")

    print("\n   📢 aws_sns_notifications - SNS notifications")
    print("      from django_extensions.aws_sns_notifications import publish_message, publish_sms")
    print("      publish_sms('+15551234567', 'Your code is 123456')")

    print("\n   📬 aws_sqs_queue - SQS message queue")
    print("      from django_extensions.aws_sqs_queue import SQSQueue")
    print("      queue = SQSQueue('my-queue')")
    print("      queue.send({'event': 'user_created', 'user_id': 123})")

    print("\n💳 Payment Integrations:")
    print("   stripe_payments - Stripe payments")
    print("      from django_extensions.stripe_payments import create_payment_intent")
    print("      intent = create_payment_intent(amount=2000, currency='usd')")

    print("\n💬 Messaging Integrations:")
    print("   twilio_sms - Twilio SMS/WhatsApp")
    print("      from django_extensions.twilio_sms import send_sms")
    print("      send_sms('+15551234567', 'Hello from Django!')")

    print("\n   slack_notifications - Slack webhooks")
    print("      from django_extensions.slack_notifications import send_webhook")
    print("      send_webhook(text='Deployment complete!', channel='#alerts')")

    print("\n   discord_notifications - Discord webhooks")
    print("      from django_extensions.discord_notifications import send_embed")
    print("      send_embed(title='Alert', description='Server is down', color=0xff0000)")

    print("\n🤖 AI Integrations:")
    print("   openai_integration - OpenAI API")
    print("      from django_extensions.openai_integration import chat_completion")
    print("      response = chat_completion([{'role': 'user', 'content': 'Hello!'}])")

    print("\n   anthropic_integration - Anthropic Claude")
    print("      from django_extensions.anthropic_integration import text_completion")
    print("      response = text_completion('Explain quantum computing')")

    print("\n🔧 Infrastructure:")
    print("   redis_cache - Redis caching with rate limiting")
    print("      from django_extensions.redis_cache import cache_set, rate_limit")
    print("      cache_set('user:123', {'name': 'John'}, ttl=3600)")
    print("      if rate_limit('api:user:123', limit=100, window=60): ...")

    print("\n   sentry_integration - Sentry error tracking")
    print("      from django_extensions.sentry_integration import capture_exception")
    print("      try: ... except Exception as e: capture_exception(e)")


def demo_all():
    """Run all demos."""
    print("\n" + "🚀 DJANGO EXTENSIONS DEMO 🚀".center(60))
    print("="*60)
    print("Showcasing 51 Django extensions with tests")
    print("="*60)

    demo_validators()
    demo_template_tags()
    demo_decorators()
    demo_pagination()
    demo_email_utils()
    demo_models()
    demo_management_commands()
    demo_cloud_integrations()

    header("SUMMARY")
    print("""
📊 Total Extensions: 51

Categories:
  • Model Mixins (8): timestamped, uuid, soft_delete, ordered, status, slugged, activator, title_slug
  • Custom Fields (7): auto_created, auto_modified, short_uuid, encrypted, json_schema, money, phone
  • Managers (3): soft_delete, active, random
  • Validators (4): phone, credit_card, color, url
  • Template Tags (4): humanize, url, math, string
  • Management Commands (5): shell_plus, show_urls, clean_pyc, reset_db, generate_secret_key
  • Middleware (2): timezone, request_logging
  • Decorators (3): ajax_required, anonymous_required, superuser_required
  • Utilities (3): cache_decorator, pagination_utils, email_utils
  • Cloud - AWS (4): s3_storage, ses_email, sns_notifications, sqs_queue
  • Cloud - Payments (1): stripe_payments
  • Cloud - Messaging (3): twilio_sms, slack_notifications, discord_notifications
  • Cloud - AI (2): openai_integration, anthropic_integration
  • Cloud - Infrastructure (2): redis_cache, sentry_integration

✅ 683 tests (564 without DB dependencies)
""")


if __name__ == '__main__':
    demo_all()
