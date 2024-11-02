"""Tests for Stripe Payment Integration."""

import pytest
import json
from unittest.mock import MagicMock, patch, PropertyMock

from .payments import (
    StripeClient,
    create_customer,
    create_payment_intent,
    create_checkout_session,
    create_subscription,
    cancel_subscription,
    create_refund,
    webhook_handler,
)


class TestStripeClient:
    """Test cases for StripeClient."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.STRIPE_SECRET_KEY = 'sk_test_123'
        settings.STRIPE_PUBLISHABLE_KEY = 'pk_test_123'
        settings.STRIPE_WEBHOOK_SECRET = 'whsec_123'
        return settings

    @pytest.fixture
    def mock_stripe(self):
        """Create mock stripe module."""
        mock = MagicMock()
        return mock

    @pytest.fixture
    def client(self, mock_settings, mock_stripe):
        """Create client with mocked stripe."""
        with patch('django_extensions.stripe_payments.payments.get_stripe', return_value=mock_stripe):
            return StripeClient()

    def test_create_customer(self, client, mock_stripe):
        """Test creating a customer."""
        mock_stripe.Customer.create.return_value = {'id': 'cus_123'}

        result = client.create_customer(
            email='user@example.com',
            name='John Doe',
            metadata={'user_id': '42'}
        )

        assert result['id'] == 'cus_123'
        mock_stripe.Customer.create.assert_called_once()
        call_kwargs = mock_stripe.Customer.create.call_args[1]
        assert call_kwargs['email'] == 'user@example.com'
        assert call_kwargs['name'] == 'John Doe'

    def test_get_customer(self, client, mock_stripe):
        """Test retrieving a customer."""
        mock_stripe.Customer.retrieve.return_value = {'id': 'cus_123', 'email': 'user@example.com'}

        result = client.get_customer('cus_123')

        assert result['email'] == 'user@example.com'
        mock_stripe.Customer.retrieve.assert_called_with('cus_123')

    def test_create_payment_intent(self, client, mock_stripe):
        """Test creating a payment intent."""
        mock_stripe.PaymentIntent.create.return_value = {
            'id': 'pi_123',
            'client_secret': 'pi_123_secret'
        }

        result = client.create_payment_intent(
            amount=2000,
            currency='usd',
            customer='cus_123',
            metadata={'order_id': '456'}
        )

        assert result['id'] == 'pi_123'
        call_kwargs = mock_stripe.PaymentIntent.create.call_args[1]
        assert call_kwargs['amount'] == 2000
        assert call_kwargs['currency'] == 'usd'

    def test_confirm_payment_intent(self, client, mock_stripe):
        """Test confirming a payment intent."""
        mock_stripe.PaymentIntent.confirm.return_value = {'status': 'succeeded'}

        result = client.confirm_payment_intent('pi_123', payment_method='pm_123')

        assert result['status'] == 'succeeded'
        mock_stripe.PaymentIntent.confirm.assert_called()

    def test_create_checkout_session(self, client, mock_stripe):
        """Test creating a checkout session."""
        mock_stripe.checkout.Session.create.return_value = {
            'id': 'cs_123',
            'url': 'https://checkout.stripe.com/...'
        }

        result = client.create_checkout_session(
            line_items=[{'price': 'price_123', 'quantity': 1}],
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel'
        )

        assert result['id'] == 'cs_123'
        call_kwargs = mock_stripe.checkout.Session.create.call_args[1]
        assert call_kwargs['mode'] == 'payment'

    def test_create_subscription(self, client, mock_stripe):
        """Test creating a subscription."""
        mock_stripe.Subscription.create.return_value = {
            'id': 'sub_123',
            'status': 'active'
        }

        result = client.create_subscription(
