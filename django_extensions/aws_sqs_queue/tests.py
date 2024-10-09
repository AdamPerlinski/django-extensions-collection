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
        """Test sending string message."""
        result = queue.send('Hello World')

        assert result['MessageId'] == 'msg-123'
        call_kwargs = mock_client.send_message.call_args[1]
        assert call_kwargs['MessageBody'] == 'Hello World'

    def test_send_dict(self, queue, mock_client):
        """Test sending dict is JSON serialized."""
        queue.send({'event': 'test', 'id': 123})

        call_kwargs = mock_client.send_message.call_args[1]
        body = json.loads(call_kwargs['MessageBody'])
        assert body == {'event': 'test', 'id': 123}

    def test_send_with_delay(self, queue, mock_client):
        """Test sending with delay."""
        queue.send('Hello', delay_seconds=60)

        call_kwargs = mock_client.send_message.call_args[1]
        assert call_kwargs['DelaySeconds'] == 60

    def test_send_with_attributes(self, queue, mock_client):
        """Test sending with attributes."""
        queue.send('Hello', attributes={'key': 'value', 'count': 5})

        call_kwargs = mock_client.send_message.call_args[1]
        assert 'MessageAttributes' in call_kwargs
        assert call_kwargs['MessageAttributes']['key']['StringValue'] == 'value'

    def test_send_batch(self, queue, mock_client):
        """Test sending batch of messages."""
        mock_client.send_message_batch.return_value = {
            'Successful': [{'Id': '0'}, {'Id': '1'}],
            'Failed': []
        }

        result = queue.send_batch(['msg1', 'msg2'])

        assert len(result['Successful']) == 2
        mock_client.send_message_batch.assert_called_once()

    def test_receive(self, queue, mock_client):
        """Test receiving messages."""
        mock_client.receive_message.return_value = {
            'Messages': [
                {'MessageId': '1', 'Body': '{"event": "test"}', 'ReceiptHandle': 'h1'},
                {'MessageId': '2', 'Body': 'plain', 'ReceiptHandle': 'h2'},
            ]
        }

        messages = list(queue.receive(max_messages=5))

        assert len(messages) == 2
        assert messages[0].body == {'event': 'test'}
        assert messages[1].body == 'plain'

    def test_receive_with_wait(self, queue, mock_client):
        """Test long polling."""
        mock_client.receive_message.return_value = {'Messages': []}

        list(queue.receive(wait_time=20))

        call_kwargs = mock_client.receive_message.call_args[1]
        assert call_kwargs['WaitTimeSeconds'] == 20

    def test_delete_message(self, queue, mock_client):
        """Test deleting message."""
        queue.delete_message('receipt-handle-123')

        mock_client.delete_message.assert_called_once_with(
            QueueUrl='https://sqs.example.com/queue',
            ReceiptHandle='receipt-handle-123'
        )

    def test_purge(self, queue, mock_client):
        """Test purging queue."""
        queue.purge()

        mock_client.purge_queue.assert_called_once_with(
            QueueUrl='https://sqs.example.com/queue'
        )

    def test_message_count(self, queue, mock_client):
        """Test getting message count."""
        mock_client.get_queue_attributes.return_value = {
            'Attributes': {'ApproximateNumberOfMessages': '42'}
        }

        assert queue.message_count == 42


class TestQueueFunctions:
    """Test queue helper functions."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.AWS_SQS_REGION = 'us-east-1'
        settings.AWS_ACCESS_KEY_ID = 'test-key'
        settings.AWS_SECRET_ACCESS_KEY = 'test-secret'
        return settings

    def test_send_message(self, mock_settings):
        """Test send_message function."""
        with patch('django_extensions.aws_sqs_queue.queue.get_sqs_client') as mock_get:
            mock_client = MagicMock()
            mock_client.get_queue_url.return_value = {'QueueUrl': 'https://sqs/q'}
            mock_client.send_message.return_value = {'MessageId': 'msg-123'}
            mock_get.return_value = mock_client

            result = send_message('my-queue', {'event': 'test'})

            assert result['MessageId'] == 'msg-123'

    def test_receive_messages(self, mock_settings):
        """Test receive_messages function."""
        with patch('django_extensions.aws_sqs_queue.queue.get_sqs_client') as mock_get:
            mock_client = MagicMock()
            mock_client.get_queue_url.return_value = {'QueueUrl': 'https://sqs/q'}
            mock_client.receive_message.return_value = {
                'Messages': [{'Body': '{"id": 1}', 'ReceiptHandle': 'h1'}]
            }
            mock_get.return_value = mock_client

            messages = receive_messages('my-queue', max_messages=1)

            assert len(messages) == 1
            assert messages[0] == {'id': 1}

    def test_create_queue(self, mock_settings):
        """Test create_queue function."""
        with patch('django_extensions.aws_sqs_queue.queue.get_sqs_client') as mock_get:
            mock_client = MagicMock()
            mock_client.create_queue.return_value = {'QueueUrl': 'https://sqs/new-queue'}
            mock_get.return_value = mock_client

            url = create_queue('my-new-queue')

            assert url == 'https://sqs/new-queue'
            mock_client.create_queue.assert_called_with(QueueName='my-new-queue')

    def test_create_fifo_queue(self, mock_settings):
        """Test creating FIFO queue."""
        with patch('django_extensions.aws_sqs_queue.queue.get_sqs_client') as mock_get:
            mock_client = MagicMock()
            mock_client.create_queue.return_value = {'QueueUrl': 'https://sqs/q.fifo'}
            mock_get.return_value = mock_client

            create_queue('my-queue', fifo=True)

            call_kwargs = mock_client.create_queue.call_args[1]
            assert call_kwargs['QueueName'] == 'my-queue.fifo'
            assert call_kwargs['Attributes']['FifoQueue'] == 'true'

    def test_get_queue_url(self, mock_settings):
        """Test get_queue_url function."""
        with patch('django_extensions.aws_sqs_queue.queue.get_sqs_client') as mock_get:
            mock_client = MagicMock()
            mock_client.get_queue_url.return_value = {'QueueUrl': 'https://sqs/my-queue'}
            mock_get.return_value = mock_client

            url = get_queue_url('my-queue')

            assert url == 'https://sqs/my-queue'
