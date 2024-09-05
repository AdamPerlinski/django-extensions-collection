"""AWS SES Email backend for Django."""

from .backend import SESEmailBackend, send_ses_email, send_templated_email

__all__ = ['SESEmailBackend', 'send_ses_email', 'send_templated_email']
