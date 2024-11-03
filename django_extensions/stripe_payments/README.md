# Stripe Payments

Stripe payment processing integration.

## Installation

```bash
pip install stripe
```

```python
INSTALLED_APPS = [
    'django_extensions.stripe_payments',
]
```

## Configuration

```python
# settings.py
STRIPE_SECRET_KEY = 'sk_test_...'
STRIPE_PUBLISHABLE_KEY = 'pk_test_...'
STRIPE_WEBHOOK_SECRET = 'whsec_...'
```

## Usage

### Payment Intents

```python
from django_extensions.stripe_payments import create_payment_intent

# Create payment intent
intent = create_payment_intent(
    amount=2000,  # $20.00 in cents
    currency='usd',
    metadata={'order_id': '12345'}
)

# Return client_secret to frontend
return JsonResponse({'client_secret': intent.client_secret})
```

### Customers

```python
from django_extensions.stripe_payments import (
    create_customer,
    get_customer,
    update_customer
)

customer = create_customer(
    email='user@example.com',
    name='John Doe',
    metadata={'user_id': '123'}
)

# Attach payment method
attach_payment_method(customer.id, 'pm_...')
```

### Subscriptions

```python
from django_extensions.stripe_payments import create_subscription

subscription = create_subscription(
    customer_id='cus_...',
    price_id='price_...',
    trial_days=14
)
```

### Checkout Session

```python
from django_extensions.stripe_payments import create_checkout_session

session = create_checkout_session(
    line_items=[
        {'price': 'price_...', 'quantity': 1}
    ],
    success_url='https://example.com/success',
    cancel_url='https://example.com/cancel'
)

# Redirect to session.url
```

### Webhooks

```python
from django_extensions.stripe_payments import verify_webhook

def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    event = verify_webhook(payload, sig_header)

    if event.type == 'payment_intent.succeeded':
        handle_payment_success(event.data.object)
    elif event.type == 'customer.subscription.created':
        handle_subscription_created(event.data.object)

    return HttpResponse(status=200)
```

### Refunds

```python
from django_extensions.stripe_payments import create_refund

refund = create_refund(
    payment_intent='pi_...',
    amount=500  # Partial refund of $5.00
)
```

## License

MIT
