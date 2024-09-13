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
        else:
            email_body = {
                'Text': {'Data': message.body, 'Charset': 'UTF-8'},
            }

        send_args = {
            'Source': message.from_email,
            'Destination': destination,
            'Message': {
                'Subject': {'Data': message.subject, 'Charset': 'UTF-8'},
                'Body': email_body,
            },
        }

        # Add optional parameters
        if message.reply_to:
            send_args['ReplyToAddresses'] = message.reply_to

        if self.return_path:
            send_args['ReturnPath'] = self.return_path

        if self.configuration_set:
            send_args['ConfigurationSetName'] = self.configuration_set

        # Add custom headers as tags
        if message.extra_headers:
            tags = []
            for key, value in message.extra_headers.items():
                if key.startswith('X-SES-'):
                    continue  # Skip SES-specific headers
                tags.append({'Name': key[:256], 'Value': str(value)[:256]})
            if tags:
                send_args['Tags'] = tags[:50]  # Max 50 tags

        self.client.send_email(**send_args)
        return True


def send_ses_email(
    subject,
    body,
    to,
    from_email=None,
    html_body=None,
    cc=None,
    bcc=None,
    reply_to=None,
    attachments=None,
    configuration_set=None,
    tags=None
):
    """
    Send an email via AWS SES.

    Args:
        subject: Email subject
        body: Plain text body
        to: List of recipient emails
        from_email: Sender email (defaults to DEFAULT_FROM_EMAIL)
        html_body: Optional HTML body
        cc: List of CC recipients
        bcc: List of BCC recipients
        reply_to: List of reply-to addresses
        attachments: List of attachments (not supported for simple send)
        configuration_set: SES configuration set name
        tags: Dict of tags for tracking

    Returns:
        dict: SES response with MessageId
    """
    client = get_ses_client()

    from_email = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL')

    if isinstance(to, str):
        to = [to]

    destination = {'ToAddresses': to}
    if cc:
        destination['CcAddresses'] = cc if isinstance(cc, list) else [cc]
    if bcc:
        destination['BccAddresses'] = bcc if isinstance(bcc, list) else [bcc]

    email_body = {'Text': {'Data': body, 'Charset': 'UTF-8'}}
    if html_body:
        email_body['Html'] = {'Data': html_body, 'Charset': 'UTF-8'}

    send_args = {
        'Source': from_email,
        'Destination': destination,
        'Message': {
            'Subject': {'Data': subject, 'Charset': 'UTF-8'},
            'Body': email_body,
        },
    }

    if reply_to:
        send_args['ReplyToAddresses'] = reply_to if isinstance(reply_to, list) else [reply_to]

    if configuration_set:
        send_args['ConfigurationSetName'] = configuration_set

    if tags:
        send_args['Tags'] = [
            {'Name': k[:256], 'Value': str(v)[:256]}
            for k, v in tags.items()
        ][:50]

    return client.send_email(**send_args)


def send_templated_email(
    template_name,
    template_data,
    to,
    from_email=None,
    cc=None,
    bcc=None,
    reply_to=None,
    configuration_set=None,
    tags=None
):
    """
    Send a templated email via AWS SES.

    Args:
        template_name: Name of SES template
        template_data: Dict of template variables
        to: List of recipient emails
        from_email: Sender email
        cc: List of CC recipients
        bcc: List of BCC recipients
        reply_to: Reply-to addresses
        configuration_set: SES configuration set
        tags: Dict of tags

    Returns:
        dict: SES response
    """
    client = get_ses_client()

    from_email = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL')

    if isinstance(to, str):
        to = [to]

    destination = {'ToAddresses': to}
    if cc:
        destination['CcAddresses'] = cc if isinstance(cc, list) else [cc]
    if bcc:
        destination['BccAddresses'] = bcc if isinstance(bcc, list) else [bcc]

    send_args = {
        'Source': from_email,
        'Destination': destination,
        'Template': template_name,
        'TemplateData': json.dumps(template_data),
    }

    if reply_to:
        send_args['ReplyToAddresses'] = reply_to if isinstance(reply_to, list) else [reply_to]

    if configuration_set:
        send_args['ConfigurationSetName'] = configuration_set

    if tags:
        send_args['Tags'] = [
            {'Name': k[:256], 'Value': str(v)[:256]}
            for k, v in tags.items()
        ][:50]

    return client.send_templated_email(**send_args)


def verify_email_identity(email):
    """
    Send verification email for a new sender identity.

    Args:
        email: Email address to verify

    Returns:
        dict: SES response
    """
    client = get_ses_client()
    return client.verify_email_identity(EmailAddress=email)


def get_send_quota():
    """
    Get SES sending quota information.

    Returns:
        dict: Quota info with Max24HourSend, MaxSendRate, SentLast24Hours
    """
    client = get_ses_client()
    return client.get_send_quota()


def get_send_statistics():
    """
    Get SES sending statistics.

    Returns:
        dict: Statistics for the last 2 weeks
    """
    client = get_ses_client()
    return client.get_send_statistics()
