"""Tests for AWS SQS Queue."""

import pytest
import json
from unittest.mock import MagicMock, patch

from .queue import (
    SQSQueue,
    SQSMessage,
    send_message,
    receive_messages,
    create_queue,
    get_queue_url,
)


class TestSQSMessage:
    """Test cases for SQSMessage."""

    def test_message_id(self):
        """Test message_id property."""
        msg = SQSMessage({'MessageId': 'msg-123'}, MagicMock())
        assert msg.message_id == 'msg-123'

    def test_receipt_handle(self):
        """Test receipt_handle property."""
        msg = SQSMessage({'ReceiptHandle': 'handle-123'}, MagicMock())
        assert msg.receipt_handle == 'handle-123'

    def test_body_json(self):
        """Test body parsing JSON."""
        msg = SQSMessage({'Body': '{"event": "test"}'}, MagicMock())
        assert msg.body == {'event': 'test'}

    def test_body_string(self):
        """Test body with plain string."""
        msg = SQSMessage({'Body': 'plain text'}, MagicMock())
        assert msg.body == 'plain text'

    def test_raw_body(self):
        """Test raw_body property."""
        msg = SQSMessage({'Body': '{"event": "test"}'}, MagicMock())
        assert msg.raw_body == '{"event": "test"}'

    def test_delete(self):
        """Test deleting message."""
        queue = MagicMock()
        msg = SQSMessage({'ReceiptHandle': 'handle-123'}, queue)

        msg.delete()

        queue.delete_message.assert_called_once_with('handle-123')

    def test_change_visibility(self):
        """Test changing visibility timeout."""
        queue = MagicMock()
        msg = SQSMessage({'ReceiptHandle': 'handle-123'}, queue)

        msg.change_visibility(60)

        queue.change_visibility.assert_called_once_with('handle-123', 60)


class TestSQSQueue:
    """Test cases for SQSQueue."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.AWS_SQS_REGION = 'us-east-1'
        settings.AWS_ACCESS_KEY_ID = 'test-key'
        settings.AWS_SECRET_ACCESS_KEY = 'test-secret'
        return settings

    @pytest.fixture
    def mock_client(self):
        """Create mock SQS client."""
        client = MagicMock()
        client.get_queue_url.return_value = {'QueueUrl': 'https://sqs.example.com/queue'}
        client.send_message.return_value = {'MessageId': 'msg-123'}
        return client

    @pytest.fixture
    def queue(self, mock_settings, mock_client):
        """Create queue with mocked client."""
        with patch('django_extensions.aws_sqs_queue.queue.get_sqs_client', return_value=mock_client):
            q = SQSQueue('test-queue')
            q._client = mock_client
            return q

    def test_init_with_name(self, mock_settings):
        """Test queue initialization with name."""
        with patch('django_extensions.aws_sqs_queue.queue.get_sqs_client'):
            queue = SQSQueue('my-queue')
            assert queue.queue_name == 'my-queue'

    def test_init_with_url(self, mock_settings):
        """Test queue initialization with URL."""
        with patch('django_extensions.aws_sqs_queue.queue.get_sqs_client'):
            queue = SQSQueue(queue_url='https://sqs.example.com/my-queue')
            assert queue._queue_url == 'https://sqs.example.com/my-queue'

    def test_queue_url_lookup(self, queue, mock_client):
        """Test queue URL is looked up from name."""
        url = queue.queue_url
        assert url == 'https://sqs.example.com/queue'
        mock_client.get_queue_url.assert_called_with(QueueName='test-queue')

    def test_send_string(self, queue, mock_client):
