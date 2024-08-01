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
        template_name: Path to HTML template.
        context: Context dictionary for the template.
        to: List of recipient email addresses.
        from_email: Sender email.
        text_template_name: Optional path to plain text template.
        **kwargs: Additional arguments passed to send_html_email.

    Returns:
        Number of emails sent.
    """
    html_content = render_to_string(template_name, context)

    if text_template_name:
        text_content = render_to_string(text_template_name, context)
    else:
        text_content = None

    return send_html_email(
        subject=subject,
        html_content=html_content,
        to=to,
        from_email=from_email,
        text_content=text_content,
        **kwargs
    )


class EmailBuilder:
    """Fluent builder for constructing and sending emails."""

    def __init__(self):
        self._subject = ''
        self._to = []
        self._cc = []
        self._bcc = []
        self._from_email = None
        self._reply_to = []
        self._html_content = None
        self._text_content = None
        self._attachments = []
        self._headers = {}

    def subject(self, subject):
        """Set email subject."""
        self._subject = subject
        return self

    def to(self, *recipients):
        """Add recipients."""
        for recipient in recipients:
            if isinstance(recipient, (list, tuple)):
                self._to.extend(recipient)
            else:
                self._to.append(recipient)
        return self

    def cc(self, *recipients):
        """Add CC recipients."""
        for recipient in recipients:
            if isinstance(recipient, (list, tuple)):
                self._cc.extend(recipient)
            else:
                self._cc.append(recipient)
        return self

    def bcc(self, *recipients):
        """Add BCC recipients."""
        for recipient in recipients:
            if isinstance(recipient, (list, tuple)):
                self._bcc.extend(recipient)
            else:
                self._bcc.append(recipient)
        return self

    def from_email(self, email):
        """Set sender email."""
        self._from_email = email
        return self

    def reply_to(self, *emails):
        """Set reply-to addresses."""
        self._reply_to.extend(emails)
        return self

    def html(self, content):
        """Set HTML content."""
        self._html_content = content
        return self

    def text(self, content):
        """Set plain text content."""
        self._text_content = content
        return self

    def template(self, template_name, context=None):
        """Set content from template."""
        context = context or {}
        self._html_content = render_to_string(template_name, context)
        return self

    def attach(self, filename, content, mimetype=None):
        """Add an attachment."""
        if mimetype:
            self._attachments.append((filename, content, mimetype))
        else:
            self._attachments.append((filename, content))
        return self

    def attach_file(self, filepath, filename=None, mimetype=None):
        """Attach a file from disk."""
        import os
        filename = filename or os.path.basename(filepath)
        with open(filepath, 'rb') as f:
            content = f.read()
        return self.attach(filename, content, mimetype)

    def header(self, name, value):
        """Add a custom header."""
        self._headers[name] = value
        return self

    def send(self, fail_silently=False):
        """Send the email."""
        if not self._html_content:
            raise ValueError('Email content is required. Use html() or template().')

        if not self._to:
            raise ValueError('At least one recipient is required.')

        return send_html_email(
            subject=self._subject,
            html_content=self._html_content,
            to=self._to,
            from_email=self._from_email,
            text_content=self._text_content,
            cc=self._cc or None,
            bcc=self._bcc or None,
            reply_to=self._reply_to or None,
            attachments=self._attachments or None,
            fail_silently=fail_silently,
        )

    def preview(self):
        """Return a dict representation of the email for preview."""
        return {
            'subject': self._subject,
            'to': self._to,
            'cc': self._cc,
            'bcc': self._bcc,
            'from_email': self._from_email,
            'reply_to': self._reply_to,
            'html_content': self._html_content,
            'text_content': self._text_content or strip_tags(self._html_content or ''),
            'attachments': [(a[0], len(a[1])) for a in self._attachments],
        }
