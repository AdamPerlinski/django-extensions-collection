# Email Utils

Enhanced email utilities with fluent builder pattern.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.email_utils',
]
```

## Usage

### Simple HTML Email

```python
from django_extensions.email_utils import send_html_email

send_html_email(
    subject='Welcome!',
    html_content='<h1>Hello</h1><p>Welcome aboard!</p>',
    to=['user@example.com']
)
```

### Template Email

```python
from django_extensions.email_utils import send_template_email

send_template_email(
    subject='Order Confirmation',
    template_name='emails/order_confirmation.html',
    context={'order': order, 'user': user},
    to=[user.email]
)
```

### EmailBuilder

Fluent interface for complex emails:

```python
from django_extensions.email_utils import EmailBuilder

email = (EmailBuilder()
    .subject('Welcome to Our Platform!')
    .to('user@example.com')
    .cc('manager@example.com')
    .bcc('archive@example.com')
    .from_email('noreply@example.com')
    .reply_to('support@example.com')
    .html('<h1>Welcome!</h1>')
    .text('Welcome!')
    .attach('report.pdf', pdf_content, 'application/pdf')
    .header('X-Priority', '1')
    .send())
```

### Multiple Recipients

```python
EmailBuilder()
    .subject('Newsletter')
    .to('user1@example.com', 'user2@example.com')
    .to(['user3@example.com', 'user4@example.com'])
    .html(newsletter_html)
    .send()
```

### Attachments

```python
# From memory
.attach('report.pdf', pdf_bytes, 'application/pdf')

# From file path
.attach_file('/path/to/file.pdf')

# With custom filename
.attach_file('/path/to/report.pdf', filename='Monthly Report.pdf')
```

### Preview

```python
email = EmailBuilder()
    .subject('Test')
    .to('user@example.com')
    .html('<p>Hello</p>')

preview = email.preview()
# {
#     'subject': 'Test',
#     'to': ['user@example.com'],
#     'html_content': '<p>Hello</p>',
#     ...
# }
```

## Configuration

```python
# settings.py
DEFAULT_FROM_EMAIL = 'noreply@example.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

## License

MIT
