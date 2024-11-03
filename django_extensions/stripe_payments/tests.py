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
            customer='cus_123',
            price_id='price_123',
            trial_days=14
        )

        assert result['id'] == 'sub_123'
        call_kwargs = mock_stripe.Subscription.create.call_args[1]
        assert call_kwargs['trial_period_days'] == 14

    def test_cancel_subscription_at_period_end(self, client, mock_stripe):
        """Test canceling subscription at period end."""
        mock_stripe.Subscription.modify.return_value = {'cancel_at_period_end': True}

        result = client.cancel_subscription('sub_123', immediately=False)

        mock_stripe.Subscription.modify.assert_called_with(
            'sub_123',
            cancel_at_period_end=True
        )

    def test_cancel_subscription_immediately(self, client, mock_stripe):
        """Test canceling subscription immediately."""
        mock_stripe.Subscription.delete.return_value = {'status': 'canceled'}

        result = client.cancel_subscription('sub_123', immediately=True)

        mock_stripe.Subscription.delete.assert_called_with('sub_123')

    def test_create_refund(self, client, mock_stripe):
        """Test creating a refund."""
        mock_stripe.Refund.create.return_value = {'id': 're_123', 'status': 'succeeded'}

        result = client.create_refund(
            payment_intent='pi_123',
            amount=1000,
            reason='requested_by_customer'
        )

        assert result['id'] == 're_123'
        call_kwargs = mock_stripe.Refund.create.call_args[1]
        assert call_kwargs['amount'] == 1000

    def test_list_payment_methods(self, client, mock_stripe):
        """Test listing payment methods."""
        mock_stripe.PaymentMethod.list.return_value = {
            'data': [{'id': 'pm_123', 'type': 'card'}]
        }

        result = client.list_payment_methods('cus_123')

        assert len(result['data']) == 1
        mock_stripe.PaymentMethod.list.assert_called_with(
            customer='cus_123',
            type='card'
        )

    def test_create_product(self, client, mock_stripe):
        """Test creating a product."""
        mock_stripe.Product.create.return_value = {'id': 'prod_123'}

        result = client.create_product(
            name='Pro Plan',
            description='Access to all features'
        )

        assert result['id'] == 'prod_123'

    def test_create_price(self, client, mock_stripe):
        """Test creating a price."""
        mock_stripe.Price.create.return_value = {'id': 'price_123'}

        result = client.create_price(
            product='prod_123',
            unit_amount=1999,
            currency='usd',
            recurring={'interval': 'month'}
        )

        assert result['id'] == 'price_123'


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.STRIPE_SECRET_KEY = 'sk_test_123'
        return settings

    def test_create_customer_function(self, mock_settings):
        """Test create_customer function."""
        with patch('django_extensions.stripe_payments.payments.get_stripe') as mock_get:
            mock_stripe = MagicMock()
            mock_stripe.Customer.create.return_value = {'id': 'cus_123'}
            mock_get.return_value = mock_stripe

            result = create_customer(email='user@example.com')

            assert result['id'] == 'cus_123'

    def test_create_payment_intent_function(self, mock_settings):
        """Test create_payment_intent function."""
        with patch('django_extensions.stripe_payments.payments.get_stripe') as mock_get:
            mock_stripe = MagicMock()
            mock_stripe.PaymentIntent.create.return_value = {'id': 'pi_123'}
            mock_get.return_value = mock_stripe

            result = create_payment_intent(2000, 'usd')

            assert result['id'] == 'pi_123'

    def test_create_checkout_session_function(self, mock_settings):
        """Test create_checkout_session function."""
        with patch('django_extensions.stripe_payments.payments.get_stripe') as mock_get:
            mock_stripe = MagicMock()
            mock_stripe.checkout.Session.create.return_value = {'id': 'cs_123'}
            mock_get.return_value = mock_stripe

            result = create_checkout_session(
                line_items=[{'price': 'price_123', 'quantity': 1}],
                success_url='https://example.com/success',
                cancel_url='https://example.com/cancel'
            )

            assert result['id'] == 'cs_123'


class TestWebhookHandler:
    """Test webhook handling."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.STRIPE_SECRET_KEY = 'sk_test_123'
        settings.STRIPE_WEBHOOK_SECRET = 'whsec_123'
        return settings

    def test_webhook_decorator(self, mock_settings):
        """Test webhook_handler decorator."""
        with patch('django_extensions.stripe_payments.payments.get_stripe') as mock_get:
            mock_stripe = MagicMock()
            mock_stripe.Webhook.construct_event.return_value = {
                'type': 'payment_intent.succeeded',
                'data': {'object': {'id': 'pi_123'}}
            }
            mock_get.return_value = mock_stripe

            @webhook_handler()
            def my_handler(request, event):
                return event['type']

            request = MagicMock()
            request.body = b'{"type": "payment_intent.succeeded"}'
            request.META = {'HTTP_STRIPE_SIGNATURE': 'sig_123'}

            result = my_handler(request)

            assert result == 'payment_intent.succeeded'

    def test_webhook_invalid_signature(self, mock_settings):
        """Test webhook with invalid signature."""
        with patch('django_extensions.stripe_payments.payments.get_stripe') as mock_get:
            mock_stripe = MagicMock()
            mock_stripe.error = MagicMock()
            mock_stripe.error.SignatureVerificationError = Exception
            mock_stripe.Webhook.construct_event.side_effect = Exception('Invalid signature')
            mock_get.return_value = mock_stripe

            @webhook_handler()
            def my_handler(request, event):
                return 'success'

            request = MagicMock()
            request.body = b'{}'
            request.META = {'HTTP_STRIPE_SIGNATURE': 'invalid'}

            result = my_handler(request)

            assert result.status_code == 400
