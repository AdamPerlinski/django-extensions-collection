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
