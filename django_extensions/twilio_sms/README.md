# Twilio SMS

Twilio SMS and WhatsApp integration.

## Installation

```bash
pip install twilio
```

```python
INSTALLED_APPS = [
    'django_extensions.twilio_sms',
]
```

## Configuration

```python
# settings.py
TWILIO_ACCOUNT_SID = 'AC...'
TWILIO_AUTH_TOKEN = 'your-auth-token'
TWILIO_PHONE_NUMBER = '+15551234567'
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+15551234567'
```

## Usage

### Send SMS

```python
from django_extensions.twilio_sms import send_sms

message = send_sms(
    to='+15559876543',
    body='Hello from Django!'
)

print(message.sid)  # Message ID
```

### Send WhatsApp

```python
from django_extensions.twilio_sms import send_whatsapp

send_whatsapp(
    to='+15559876543',
    body='Hello via WhatsApp!'
)
```

### SMS with Media

```python
send_sms(
    to='+15559876543',
    body='Check this out!',
    media_url='https://example.com/image.jpg'
)
```

### TwilioClient Class

```python
from django_extensions.twilio_sms import TwilioClient

client = TwilioClient()

# Send SMS
client.send_sms('+15559876543', 'Hello!')

# Send WhatsApp
client.send_whatsapp('+15559876543', 'Hello!')

# Check message status
status = client.get_message_status('SM...')
```

### Bulk SMS

```python
from django_extensions.twilio_sms import send_bulk_sms

results = send_bulk_sms(
    recipients=['+15551111111', '+15552222222', '+15553333333'],
    body='Important announcement!'
)
```

### Verification

```python
from django_extensions.twilio_sms import send_verification, check_verification

# Send code
send_verification('+15559876543')

# Verify code
is_valid = check_verification('+15559876543', '123456')
```

### Incoming Webhooks

```python
from django_extensions.twilio_sms import validate_request

def sms_webhook(request):
    if not validate_request(request):
        return HttpResponseForbidden()

    from_number = request.POST['From']
    body = request.POST['Body']

    # Process incoming message
    return HttpResponse('<Response><Message>Thanks!</Message></Response>')
```

## License

MIT
