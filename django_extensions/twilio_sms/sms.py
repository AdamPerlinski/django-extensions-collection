"""
Twilio SMS Integration for Django.

Usage:
    # settings.py
    TWILIO_ACCOUNT_SID = 'your-account-sid'
    TWILIO_AUTH_TOKEN = 'your-auth-token'
    TWILIO_PHONE_NUMBER = '+15551234567'

    # Send SMS
    from django_extensions.twilio_sms import send_sms

    send_sms(
        to='+15559876543',
        body='Hello from Django!'
    )
"""

import hmac
import hashlib
from functools import wraps
from urllib.parse import urlencode
from django.conf import settings
from django.http import HttpResponse


def get_twilio_client():
    """Get configured Twilio client."""
    try:
        from twilio.rest import Client
    except ImportError:
        raise ImportError("twilio is required. Install it with: pip install twilio")

    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)

    if not account_sid or not auth_token:
        raise ValueError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set")

    return Client(account_sid, auth_token)


class TwilioClient:
    """
    Twilio API client wrapper.

    Usage:
        client = TwilioClient()
        client.send_sms('+15559876543', 'Hello!')
        client.send_whatsapp('+15559876543', 'Hello via WhatsApp!')
    """

    def __init__(self, account_sid=None, auth_token=None, phone_number=None):
        self._client = None
        self._account_sid = account_sid
        self._auth_token = auth_token
        self.phone_number = phone_number or getattr(settings, 'TWILIO_PHONE_NUMBER', None)

    @property
    def client(self):
        if self._client is None:
            if self._account_sid and self._auth_token:
                try:
                    from twilio.rest import Client
                except ImportError:
                    raise ImportError("twilio is required. Install it with: pip install twilio")
                self._client = Client(self._account_sid, self._auth_token)
            else:
                self._client = get_twilio_client()
        return self._client

    def send_sms(self, to, body, from_=None, media_url=None, status_callback=None):
        """
        Send an SMS message.

        Args:
            to: Recipient phone number (E.164 format)
            body: Message body
            from_: Sender phone number (defaults to TWILIO_PHONE_NUMBER)
            media_url: URL of media to include (MMS)
            status_callback: URL for status updates

        Returns:
            Message object with sid, status, etc.
        """
        params = {
            'to': to,
            'body': body,
            'from_': from_ or self.phone_number,
        }

        if media_url:
            params['media_url'] = media_url if isinstance(media_url, list) else [media_url]

        if status_callback:
            params['status_callback'] = status_callback

        return self.client.messages.create(**params)

    def send_whatsapp(self, to, body, from_=None, media_url=None):
        """
        Send a WhatsApp message.

        Args:
            to: Recipient phone number
            body: Message body
            from_: Sender (defaults to whatsapp:TWILIO_PHONE_NUMBER)
            media_url: URL of media to include

        Returns:
            Message object
        """
        whatsapp_to = f'whatsapp:{to}' if not to.startswith('whatsapp:') else to

        from_number = from_ or self.phone_number
