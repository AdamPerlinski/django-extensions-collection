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

