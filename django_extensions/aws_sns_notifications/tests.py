"""Tests for AWS SNS Notifications."""

import pytest
import json
from unittest.mock import MagicMock, patch

from .notifications import (
    SNSNotifier,
    publish_message,
    publish_sms,
    create_topic,
    subscribe_email,
    subscribe_sms,
)


class TestSNSNotifier:
    """Test cases for SNSNotifier."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.AWS_SNS_REGION = 'us-east-1'
        settings.AWS_ACCESS_KEY_ID = 'test-key'
        settings.AWS_SECRET_ACCESS_KEY = 'test-secret'
        settings.AWS_SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:123456789:test-topic'
        return settings

    @pytest.fixture
    def mock_client(self):
        """Create mock SNS client."""
        client = MagicMock()
        client.publish.return_value = {'MessageId': 'test-msg-id'}
        return client

    @pytest.fixture
    def notifier(self, mock_settings, mock_client):
        """Create notifier with mocked client."""
        with patch('django_extensions.aws_sns_notifications.notifications.get_sns_client', return_value=mock_client):
            n = SNSNotifier()
            n._client = mock_client
            return n

    def test_init_from_settings(self, mock_settings):
        """Test notifier initializes from settings."""
        with patch('django_extensions.aws_sns_notifications.notifications.get_sns_client'):
            notifier = SNSNotifier()
            assert notifier.topic_arn == 'arn:aws:sns:us-east-1:123456789:test-topic'

    def test_init_with_params(self, mock_settings):
        """Test notifier with explicit params."""
        with patch('django_extensions.aws_sns_notifications.notifications.get_sns_client'):
            notifier = SNSNotifier(
                topic_arn='arn:custom',
                default_subject='Default'
            )
            assert notifier.topic_arn == 'arn:custom'
            assert notifier.default_subject == 'Default'

    def test_publish(self, notifier, mock_client):
        """Test publishing a message."""
        result = notifier.publish('Hello World')

        assert result['MessageId'] == 'test-msg-id'
        mock_client.publish.assert_called_once()
        call_kwargs = mock_client.publish.call_args[1]
        assert call_kwargs['Message'] == 'Hello World'

    def test_publish_with_subject(self, notifier, mock_client):
        """Test publishing with subject."""
        notifier.publish('Hello', subject='Test Subject')

        call_kwargs = mock_client.publish.call_args[1]
        assert call_kwargs['Subject'] == 'Test Subject'

    def test_publish_with_default_subject(self, mock_settings, mock_client):
        """Test publishing uses default subject."""
        with patch('django_extensions.aws_sns_notifications.notifications.get_sns_client', return_value=mock_client):
            notifier = SNSNotifier(default_subject='Default Subject')
            notifier._client = mock_client
            notifier.publish('Hello')

            call_kwargs = mock_client.publish.call_args[1]
            assert call_kwargs['Subject'] == 'Default Subject'

    def test_publish_with_attributes(self, notifier, mock_client):
        """Test publishing with message attributes."""
        notifier.publish('Hello', attributes={'key': 'value', 'count': 5})

        call_kwargs = mock_client.publish.call_args[1]
        assert 'MessageAttributes' in call_kwargs
        assert call_kwargs['MessageAttributes']['key']['StringValue'] == 'value'
        assert call_kwargs['MessageAttributes']['count']['StringValue'] == '5'

    def test_publish_json(self, notifier, mock_client):
        """Test publishing JSON data."""
        notifier.publish_json({'event': 'user_created', 'user_id': 123})

        call_kwargs = mock_client.publish.call_args[1]
        message = json.loads(call_kwargs['Message'])
        assert message['event'] == 'user_created'
        assert message['user_id'] == 123

    def test_publish_without_topic_raises(self, mock_settings, mock_client):
        """Test publish without topic ARN raises error."""
        mock_settings.AWS_SNS_TOPIC_ARN = None
        with patch('django_extensions.aws_sns_notifications.notifications.get_sns_client', return_value=mock_client):
            notifier = SNSNotifier(topic_arn=None)
            notifier._client = mock_client

            with pytest.raises(ValueError):
                notifier.publish('Hello')

    def test_subscribe(self, notifier, mock_client):
        """Test subscribing to topic."""
        mock_client.subscribe.return_value = {'SubscriptionArn': 'arn:subscription'}

        result = notifier.subscribe('email', 'user@example.com')

        assert result['SubscriptionArn'] == 'arn:subscription'
        mock_client.subscribe.assert_called_once()


class TestPublishMessage:
    """Test publish_message function."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.AWS_SNS_REGION = 'us-east-1'
        settings.AWS_ACCESS_KEY_ID = 'test-key'
        settings.AWS_SECRET_ACCESS_KEY = 'test-secret'
        return settings

    def test_publish_string(self, mock_settings):
        """Test publishing string message."""
        with patch('django_extensions.aws_sns_notifications.notifications.get_sns_client') as mock_get:
            mock_client = MagicMock()
            mock_client.publish.return_value = {'MessageId': 'msg-123'}
            mock_get.return_value = mock_client

            result = publish_message(
                topic_arn='arn:topic',
                message='Hello World'
            )

            assert result['MessageId'] == 'msg-123'
            call_kwargs = mock_client.publish.call_args[1]
            assert call_kwargs['Message'] == 'Hello World'

    def test_publish_dict(self, mock_settings):
        """Test publishing dict is JSON serialized."""
        with patch('django_extensions.aws_sns_notifications.notifications.get_sns_client') as mock_get:
            mock_client = MagicMock()
            mock_get.return_value = mock_client

            publish_message(
                topic_arn='arn:topic',
                message={'event': 'test'}
            )

            call_kwargs = mock_client.publish.call_args[1]
            assert json.loads(call_kwargs['Message']) == {'event': 'test'}


class TestPublishSMS:
    """Test publish_sms function."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.AWS_SNS_REGION = 'us-east-1'
        settings.AWS_ACCESS_KEY_ID = 'test-key'
        settings.AWS_SECRET_ACCESS_KEY = 'test-secret'
        return settings

    def test_send_sms(self, mock_settings):
        """Test sending SMS."""
        with patch('django_extensions.aws_sns_notifications.notifications.get_sns_client') as mock_get:
            mock_client = MagicMock()
            mock_client.publish.return_value = {'MessageId': 'sms-123'}
            mock_get.return_value = mock_client

            result = publish_sms(
                phone_number='+15551234567',
                message='Your code is 123456'
            )

            assert result['MessageId'] == 'sms-123'
            call_kwargs = mock_client.publish.call_args[1]
            assert call_kwargs['PhoneNumber'] == '+15551234567'
            assert call_kwargs['Message'] == 'Your code is 123456'

    def test_send_sms_with_sender_id(self, mock_settings):
        """Test SMS with sender ID."""
        with patch('django_extensions.aws_sns_notifications.notifications.get_sns_client') as mock_get:
            mock_client = MagicMock()
            mock_get.return_value = mock_client

            publish_sms(
                phone_number='+15551234567',
                message='Hello',
                sender_id='MyApp'
            )

            call_kwargs = mock_client.publish.call_args[1]
            assert 'AWS.SNS.SMS.SenderID' in call_kwargs['MessageAttributes']

    def test_send_promotional_sms(self, mock_settings):
        """Test promotional SMS type."""
        with patch('django_extensions.aws_sns_notifications.notifications.get_sns_client') as mock_get:
            mock_client = MagicMock()
            mock_get.return_value = mock_client

            publish_sms(
                phone_number='+15551234567',
                message='Sale!',
                message_type='Promotional'
            )

            call_kwargs = mock_client.publish.call_args[1]
            sms_type = call_kwargs['MessageAttributes']['AWS.SNS.SMS.SMSType']['StringValue']
            assert sms_type == 'Promotional'


class TestTopicManagement:
    """Test topic management functions."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.AWS_SNS_REGION = 'us-east-1'
        settings.AWS_ACCESS_KEY_ID = 'test-key'
        settings.AWS_SECRET_ACCESS_KEY = 'test-secret'
        return settings

    def test_create_topic(self, mock_settings):
        """Test creating a topic."""
        with patch('django_extensions.aws_sns_notifications.notifications.get_sns_client') as mock_get:
            mock_client = MagicMock()
            mock_client.create_topic.return_value = {'TopicArn': 'arn:new-topic'}
            mock_get.return_value = mock_client

            result = create_topic('my-topic')

            assert result['TopicArn'] == 'arn:new-topic'
            mock_client.create_topic.assert_called_with(Name='my-topic')

    def test_create_topic_with_tags(self, mock_settings):
        """Test creating topic with tags."""
        with patch('django_extensions.aws_sns_notifications.notifications.get_sns_client') as mock_get:
            mock_client = MagicMock()
            mock_get.return_value = mock_client

            create_topic('my-topic', tags={'env': 'production'})

            call_kwargs = mock_client.create_topic.call_args[1]
            assert call_kwargs['Tags'] == [{'Key': 'env', 'Value': 'production'}]

    def test_subscribe_email(self, mock_settings):
        """Test subscribing email."""
        with patch('django_extensions.aws_sns_notifications.notifications.get_sns_client') as mock_get:
            mock_client = MagicMock()
            mock_client.subscribe.return_value = {'SubscriptionArn': 'pending confirmation'}
            mock_get.return_value = mock_client

            result = subscribe_email('arn:topic', 'user@example.com')

            mock_client.subscribe.assert_called_with(
                TopicArn='arn:topic',
                Protocol='email',
                Endpoint='user@example.com'
            )

    def test_subscribe_sms(self, mock_settings):
        """Test subscribing SMS."""
        with patch('django_extensions.aws_sns_notifications.notifications.get_sns_client') as mock_get:
            mock_client = MagicMock()
            mock_get.return_value = mock_client

            subscribe_sms('arn:topic', '+15551234567')

            mock_client.subscribe.assert_called_with(
                TopicArn='arn:topic',
                Protocol='sms',
                Endpoint='+15551234567'
            )
