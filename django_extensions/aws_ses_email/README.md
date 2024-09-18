# AWS SES Email

Amazon Simple Email Service backend for Django.

## Installation

```bash
pip install boto3
```

```python
INSTALLED_APPS = [
    'django_extensions.aws_ses_email',
]
```

## Configuration

```python
# settings.py
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_SES_REGION = 'us-east-1'

# Use as email backend
EMAIL_BACKEND = 'django_extensions.aws_ses_email.SESEmailBackend'

# Optional
AWS_SES_CONFIGURATION_SET = 'my-config-set'
AWS_SES_RETURN_PATH = 'bounces@example.com'
```

## Usage

### With Django's Email Functions

```python
from django.core.mail import send_mail

send_mail(
    subject='Hello',
    message='Welcome!',
    from_email='noreply@example.com',
    recipient_list=['user@example.com']
)
```

### Direct SES Function

```python
from django_extensions.aws_ses_email import send_ses_email

send_ses_email(
    subject='Welcome!',
    body='Hello, welcome to our platform.',
    to=['user@example.com'],
    from_email='noreply@example.com'
)
```

### HTML Email

```python
send_ses_email(
    subject='Welcome!',
    body='Plain text fallback',
    html_body='<h1>Welcome!</h1><p>Hello!</p>',
    to=['user@example.com']
)
```

### With Attachments

```python
send_ses_email(
    subject='Report',
    body='Please find attached.',
    to=['user@example.com'],
    attachments=[
        ('report.pdf', pdf_content, 'application/pdf')
    ]
)
```

### Bulk Email

```python
from django_extensions.aws_ses_email import send_bulk_email

send_bulk_email(
    template='welcome_template',
    destinations=[
        {'email': 'user1@example.com', 'data': {'name': 'User 1'}},
        {'email': 'user2@example.com', 'data': {'name': 'User 2'}},
    ]
)
```

## SES Templates

```python
from django_extensions.aws_ses_email import create_template

create_template(
    name='welcome_template',
    subject='Welcome {{name}}!',
    html='<h1>Hello {{name}}</h1>',
    text='Hello {{name}}'
)
```

## Verified Identities

Ensure sender emails/domains are verified in SES console.

## License

MIT
