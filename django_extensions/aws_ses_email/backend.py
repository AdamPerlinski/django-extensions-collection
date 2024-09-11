"""
AWS SES Email Backend for Django.

Usage:
    # settings.py
    EMAIL_BACKEND = 'django_extensions.aws_ses_email.SESEmailBackend'

    AWS_SES_REGION = 'us-east-1'
    AWS_ACCESS_KEY_ID = 'your-key'
    AWS_SECRET_ACCESS_KEY = 'your-secret'

    # Or use directly
    from django_extensions.aws_ses_email import send_ses_email

    send_ses_email(
        subject='Hello',
        body='World',
        to=['user@example.com'],
        from_email='noreply@example.com'
    )
"""

import json
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import EmailMessage, EmailMultiAlternatives


def get_ses_client():
    """Get SES client with credentials from settings."""
    try:
        import boto3
    except ImportError:
        raise ImportError("boto3 is required. Install it with: pip install boto3")

    return boto3.client(
        'ses',
        region_name=getattr(settings, 'AWS_SES_REGION', 'us-east-1'),
        aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
        aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
    )


class SESEmailBackend(BaseEmailBackend):
    """
    AWS SES email backend for Django.

    Settings:
        AWS_SES_REGION: AWS region (default: us-east-1)
        AWS_ACCESS_KEY_ID: AWS access key
        AWS_SECRET_ACCESS_KEY: AWS secret key
        AWS_SES_CONFIGURATION_SET: Configuration set name (optional)
        AWS_SES_RETURN_PATH: Return path for bounces (optional)
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self._client = None
        self.configuration_set = getattr(settings, 'AWS_SES_CONFIGURATION_SET', None)
        self.return_path = getattr(settings, 'AWS_SES_RETURN_PATH', None)

    @property
    def client(self):
        if self._client is None:
            self._client = get_ses_client()
        return self._client

    def send_messages(self, email_messages):
        """Send one or more EmailMessage objects."""
        if not email_messages:
            return 0

        num_sent = 0
        for message in email_messages:
            try:
                sent = self._send(message)
                if sent:
                    num_sent += 1
            except Exception as e:
                if not self.fail_silently:
                    raise
        return num_sent

    def _send(self, message):
        """Send a single email message."""
        if not message.recipients():
            return False

        # Build the email
        destination = {
            'ToAddresses': message.to,
        }

        if message.cc:
            destination['CcAddresses'] = message.cc
        if message.bcc:
            destination['BccAddresses'] = message.bcc

        # Check if it's a multipart message
        if isinstance(message, EmailMultiAlternatives) and message.alternatives:
            # Find HTML alternative
            html_content = None
            for content, mimetype in message.alternatives:
                if mimetype == 'text/html':
                    html_content = content
                    break

            email_body = {
                'Text': {'Data': message.body, 'Charset': 'UTF-8'},
            }
            if html_content:
                email_body['Html'] = {'Data': html_content, 'Charset': 'UTF-8'}
