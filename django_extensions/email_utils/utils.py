"""
Email utilities - Enhanced email sending helpers.

Usage:
    from django_extensions.email_utils import send_html_email, EmailBuilder

    send_html_email(
        subject='Welcome!',
        html_content='<h1>Hello</h1>',
        to=['user@example.com']
    )

    # Or use the builder
    EmailBuilder() \
        .subject('Welcome!') \
        .to('user@example.com') \
        .template('emails/welcome.html', {'name': 'John'}) \
        .send()
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_html_email(subject, html_content, to, from_email=None, text_content=None,
                    cc=None, bcc=None, reply_to=None, attachments=None,
                    fail_silently=False):
    """
    Send an HTML email with plain text fallback.

    Args:
        subject: Email subject.
        html_content: HTML content of the email.
        to: List of recipient email addresses.
        from_email: Sender email (defaults to DEFAULT_FROM_EMAIL).
        text_content: Plain text content (auto-generated from HTML if not provided).
        cc: List of CC recipients.
        bcc: List of BCC recipients.
        reply_to: List of reply-to addresses.
        attachments: List of (filename, content, mimetype) tuples.
        fail_silently: Whether to suppress exceptions.

    Returns:
        Number of emails sent (1 if successful, 0 if failed).
    """
    if isinstance(to, str):
        to = [to]

    from_email = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', None)
    text_content = text_content or strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=to,
        cc=cc,
        bcc=bcc,
        reply_to=reply_to,
    )

    email.attach_alternative(html_content, 'text/html')

    if attachments:
        for attachment in attachments:
            if len(attachment) == 3:
                email.attach(*attachment)
            elif len(attachment) == 2:
                email.attach(attachment[0], attachment[1])

    return email.send(fail_silently=fail_silently)


def send_template_email(subject, template_name, context, to, from_email=None,
                        text_template_name=None, **kwargs):
    """
    Send an email using Django templates.

    Args:
        subject: Email subject.
