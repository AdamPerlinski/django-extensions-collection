"""
Stripe Payment Integration for Django.

Usage:
    # settings.py
    STRIPE_SECRET_KEY = 'sk_test_...'
    STRIPE_PUBLISHABLE_KEY = 'pk_test_...'
    STRIPE_WEBHOOK_SECRET = 'whsec_...'

    # Create a payment
    from django_extensions.stripe_payments import create_payment_intent

    intent = create_payment_intent(
        amount=2000,  # $20.00
        currency='usd',
        customer_id='cus_...',
        metadata={'order_id': '123'}
    )

    # Create a checkout session
    session = create_checkout_session(
        line_items=[{'price': 'price_...', 'quantity': 1}],
        success_url='https://example.com/success',
        cancel_url='https://example.com/cancel'
    )
"""

import json
import hmac
import hashlib
from functools import wraps
from django.conf import settings
from django.http import HttpResponse


def get_stripe():
    """Get configured stripe module."""
    try:
        import stripe
    except ImportError:
        raise ImportError("stripe is required. Install it with: pip install stripe")

    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
    stripe.api_version = getattr(settings, 'STRIPE_API_VERSION', None)

    return stripe


class StripeClient:
    """
    Stripe API client wrapper.

    Usage:
        client = StripeClient()
        customer = client.create_customer(email='user@example.com')
        intent = client.create_payment_intent(amount=2000, currency='usd')
    """

    def __init__(self, api_key=None):
        self._stripe = get_stripe()
        if api_key:
            self._stripe.api_key = api_key

    @property
    def stripe(self):
        return self._stripe

    def create_customer(self, email=None, name=None, phone=None, metadata=None, **kwargs):
        """Create a Stripe customer."""
        params = {}
        if email:
            params['email'] = email
        if name:
            params['name'] = name
        if phone:
            params['phone'] = phone
        if metadata:
            params['metadata'] = metadata
        params.update(kwargs)

        return self._stripe.Customer.create(**params)

    def get_customer(self, customer_id):
        """Retrieve a customer by ID."""
        return self._stripe.Customer.retrieve(customer_id)

    def update_customer(self, customer_id, **kwargs):
        """Update a customer."""
        return self._stripe.Customer.modify(customer_id, **kwargs)

    def delete_customer(self, customer_id):
        """Delete a customer."""
        return self._stripe.Customer.delete(customer_id)

    def create_payment_intent(self, amount, currency='usd', customer=None,
                               payment_method=None, confirm=False, metadata=None, **kwargs):
        """Create a payment intent."""
        params = {
            'amount': amount,
            'currency': currency,
        }
        if customer:
            params['customer'] = customer
        if payment_method:
            params['payment_method'] = payment_method
        if confirm:
            params['confirm'] = confirm
        if metadata:
            params['metadata'] = metadata
        params.update(kwargs)

        return self._stripe.PaymentIntent.create(**params)

    def confirm_payment_intent(self, intent_id, payment_method=None):
        """Confirm a payment intent."""
        params = {}
        if payment_method:
            params['payment_method'] = payment_method
        return self._stripe.PaymentIntent.confirm(intent_id, **params)

    def cancel_payment_intent(self, intent_id):
        """Cancel a payment intent."""
        return self._stripe.PaymentIntent.cancel(intent_id)

    def create_checkout_session(self, line_items, success_url, cancel_url,
                                  mode='payment', customer=None, metadata=None, **kwargs):
        """Create a checkout session."""
        params = {
            'line_items': line_items,
            'mode': mode,
            'success_url': success_url,
            'cancel_url': cancel_url,
        }
        if customer:
            params['customer'] = customer
        if metadata:
            params['metadata'] = metadata
        params.update(kwargs)

        return self._stripe.checkout.Session.create(**params)

    def create_subscription(self, customer, price_id, trial_days=None, metadata=None, **kwargs):
        """Create a subscription."""
        params = {
            'customer': customer,
            'items': [{'price': price_id}],
        }
        if trial_days:
            params['trial_period_days'] = trial_days
        if metadata:
            params['metadata'] = metadata
        params.update(kwargs)

        return self._stripe.Subscription.create(**params)

    def cancel_subscription(self, subscription_id, immediately=False):
        """Cancel a subscription."""
        if immediately:
            return self._stripe.Subscription.delete(subscription_id)
        return self._stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )

    def create_refund(self, payment_intent=None, charge=None, amount=None, reason=None, metadata=None):
        """Create a refund."""
        params = {}
        if payment_intent:
            params['payment_intent'] = payment_intent
        if charge:
            params['charge'] = charge
        if amount:
            params['amount'] = amount
        if reason:
            params['reason'] = reason
        if metadata:
            params['metadata'] = metadata

        return self._stripe.Refund.create(**params)

    def list_payment_methods(self, customer_id, type='card'):
        """List payment methods for a customer."""
        return self._stripe.PaymentMethod.list(
            customer=customer_id,
            type=type
        )

    def attach_payment_method(self, payment_method_id, customer_id):
        """Attach a payment method to a customer."""
        return self._stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer_id
        )

    def detach_payment_method(self, payment_method_id):
        """Detach a payment method."""
        return self._stripe.PaymentMethod.detach(payment_method_id)

    def create_product(self, name, description=None, metadata=None, **kwargs):
        """Create a product."""
        params = {'name': name}
        if description:
            params['description'] = description
        if metadata:
            params['metadata'] = metadata
        params.update(kwargs)

        return self._stripe.Product.create(**params)

    def create_price(self, product, unit_amount, currency='usd', recurring=None, **kwargs):
        """Create a price."""
        params = {
            'product': product,
            'unit_amount': unit_amount,
            'currency': currency,
        }
        if recurring:
            params['recurring'] = recurring
        params.update(kwargs)

        return self._stripe.Price.create(**params)

    def construct_webhook_event(self, payload, signature, secret=None):
        """Construct and verify a webhook event."""
        secret = secret or getattr(settings, 'STRIPE_WEBHOOK_SECRET')
        return self._stripe.Webhook.construct_event(payload, signature, secret)


# Convenience functions

def create_customer(email=None, name=None, **kwargs):
    """Create a Stripe customer."""
    client = StripeClient()
    return client.create_customer(email=email, name=name, **kwargs)


def get_customer(customer_id):
    """Get a Stripe customer."""
    client = StripeClient()
    return client.get_customer(customer_id)


def create_payment_intent(amount, currency='usd', **kwargs):
    """Create a payment intent."""
    client = StripeClient()
    return client.create_payment_intent(amount, currency, **kwargs)


def create_checkout_session(line_items, success_url, cancel_url, **kwargs):
    """Create a checkout session."""
    client = StripeClient()
    return client.create_checkout_session(line_items, success_url, cancel_url, **kwargs)


def create_subscription(customer, price_id, **kwargs):
    """Create a subscription."""
    client = StripeClient()
    return client.create_subscription(customer, price_id, **kwargs)


def cancel_subscription(subscription_id, immediately=False):
    """Cancel a subscription."""
    client = StripeClient()
    return client.cancel_subscription(subscription_id, immediately)


def create_refund(payment_intent=None, charge=None, amount=None, **kwargs):
    """Create a refund."""
    client = StripeClient()
    return client.create_refund(payment_intent=payment_intent, charge=charge, amount=amount, **kwargs)


def list_payment_methods(customer_id, type='card'):
    """List payment methods for a customer."""
    client = StripeClient()
    return client.list_payment_methods(customer_id, type)


def webhook_handler(webhook_secret=None):
    """
    Decorator for handling Stripe webhooks.

    Usage:
        @webhook_handler()
        def stripe_webhook(request, event):
            if event['type'] == 'payment_intent.succeeded':
                handle_payment_success(event['data']['object'])
            return HttpResponse(status=200)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            payload = request.body
            signature = request.META.get('HTTP_STRIPE_SIGNATURE')

            secret = webhook_secret or getattr(settings, 'STRIPE_WEBHOOK_SECRET')

            try:
                stripe = get_stripe()
                event = stripe.Webhook.construct_event(payload, signature, secret)
            except ValueError:
                return HttpResponse(status=400)
            except stripe.error.SignatureVerificationError:
                return HttpResponse(status=400)

            return view_func(request, event, *args, **kwargs)
        return wrapper
    return decorator


class StripeWebhookView:
    """
    Base class for Stripe webhook views.

    Usage:
        class MyWebhookView(StripeWebhookView):
            def handle_payment_intent_succeeded(self, event):
                payment_intent = event['data']['object']
                # Process successful payment

            def handle_customer_subscription_created(self, event):
                subscription = event['data']['object']
                # Process new subscription
    """

    webhook_secret = None

    def __call__(self, request):
        payload = request.body
        signature = request.META.get('HTTP_STRIPE_SIGNATURE')

        secret = self.webhook_secret or getattr(settings, 'STRIPE_WEBHOOK_SECRET')

        try:
            stripe = get_stripe()
            event = stripe.Webhook.construct_event(payload, signature, secret)
        except ValueError:
            return HttpResponse('Invalid payload', status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse('Invalid signature', status=400)

        # Get handler method
        event_type = event['type'].replace('.', '_')
        handler_name = f'handle_{event_type}'
        handler = getattr(self, handler_name, self.handle_unhandled_event)

        try:
            response = handler(event)
            if response:
                return response
            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(str(e), status=500)

    def handle_unhandled_event(self, event):
        """Handle events without specific handlers."""
        pass
