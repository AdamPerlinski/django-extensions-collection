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
        whatsapp_from = f'whatsapp:{from_number}' if not from_number.startswith('whatsapp:') else from_number

        params = {
            'to': whatsapp_to,
            'body': body,
            'from_': whatsapp_from,
        }

        if media_url:
            params['media_url'] = media_url if isinstance(media_url, list) else [media_url]

        return self.client.messages.create(**params)

    def make_call(self, to, url=None, twiml=None, from_=None, status_callback=None, record=False):
        """
        Make a phone call.

        Args:
            to: Recipient phone number
            url: URL returning TwiML instructions
            twiml: TwiML string directly
            from_: Caller ID
            status_callback: URL for status updates
            record: Whether to record the call

        Returns:
            Call object
        """
        params = {
            'to': to,
            'from_': from_ or self.phone_number,
        }

        if twiml:
            params['twiml'] = twiml
        elif url:
            params['url'] = url
        else:
            raise ValueError("Either url or twiml must be provided")

        if status_callback:
            params['status_callback'] = status_callback

        if record:
            params['record'] = True

        return self.client.calls.create(**params)

    def get_message(self, message_sid):
        """Get a message by SID."""
        return self.client.messages(message_sid).fetch()

    def list_messages(self, to=None, from_=None, date_sent=None, limit=20):
        """List messages."""
        params = {'limit': limit}
        if to:
            params['to'] = to
        if from_:
            params['from_'] = from_
        if date_sent:
            params['date_sent'] = date_sent

        return list(self.client.messages.list(**params))

    def send_verification(self, to, channel='sms', service_sid=None):
        """
        Send a verification code using Twilio Verify.

        Args:
            to: Phone number or email
            channel: 'sms', 'call', or 'email'
            service_sid: Verify service SID

        Returns:
            Verification object
        """
        service_sid = service_sid or getattr(settings, 'TWILIO_VERIFY_SERVICE_SID')

        return self.client.verify.v2.services(service_sid).verifications.create(
            to=to,
            channel=channel
        )

    def check_verification(self, to, code, service_sid=None):
        """
        Check a verification code.

        Args:
            to: Phone number or email
            code: Verification code
            service_sid: Verify service SID

        Returns:
            Verification check object with status
        """
        service_sid = service_sid or getattr(settings, 'TWILIO_VERIFY_SERVICE_SID')

        return self.client.verify.v2.services(service_sid).verification_checks.create(
            to=to,
            code=code
        )


# Convenience functions

def send_sms(to, body, from_=None, **kwargs):
    """Send an SMS message."""
    client = TwilioClient()
    return client.send_sms(to, body, from_=from_, **kwargs)


def send_whatsapp(to, body, from_=None, **kwargs):
    """Send a WhatsApp message."""
    client = TwilioClient()
    return client.send_whatsapp(to, body, from_=from_, **kwargs)


def make_call(to, url=None, twiml=None, from_=None, **kwargs):
    """Make a phone call."""
    client = TwilioClient()
    return client.make_call(to, url=url, twiml=twiml, from_=from_, **kwargs)


def verify_webhook_signature(request, auth_token=None):
    """
    Verify Twilio webhook signature.

    Args:
        request: Django request object
        auth_token: Twilio auth token (defaults to settings)

    Returns:
        bool: True if signature is valid
    """
    try:
        from twilio.request_validator import RequestValidator
    except ImportError:
        raise ImportError("twilio is required. Install it with: pip install twilio")

    auth_token = auth_token or getattr(settings, 'TWILIO_AUTH_TOKEN')
    validator = RequestValidator(auth_token)

    # Get the full URL
    url = request.build_absolute_uri()

    # Get POST params
    if request.method == 'POST':
        params = request.POST.dict()
    else:
        params = {}

    # Get signature
    signature = request.META.get('HTTP_X_TWILIO_SIGNATURE', '')

    return validator.validate(url, params, signature)


def twilio_webhook_required(view_func):
    """
    Decorator to verify Twilio webhook signatures.

    Usage:
        @twilio_webhook_required
        def my_webhook(request):
            # Handle webhook
            return HttpResponse('<Response></Response>', content_type='text/xml')
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not verify_webhook_signature(request):
            return HttpResponse('Invalid signature', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


def twiml_response(say=None, play=None, gather=None, dial=None, sms=None):
    """
    Generate a simple TwiML response.

    Args:
        say: Text to speak
        play: URL to play
        gather: Dict with gather options
        dial: Phone number to dial
        sms: SMS message to send

    Returns:
        str: TwiML XML string
    """
    try:
        from twilio.twiml.voice_response import VoiceResponse, Gather
        from twilio.twiml.messaging_response import MessagingResponse
    except ImportError:
        raise ImportError("twilio is required. Install it with: pip install twilio")

    if sms:
        response = MessagingResponse()
        response.message(sms)
        return str(response)

    response = VoiceResponse()

    if gather:
        g = Gather(**{k: v for k, v in gather.items() if k != 'say'})
        if gather.get('say'):
            g.say(gather['say'])
        response.append(g)
    elif say:
        response.say(say)
    elif play:
        response.play(play)
    elif dial:
        response.dial(dial)

    return str(response)
