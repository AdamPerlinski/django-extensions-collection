"""
AWS SQS Queue integration for Django.

Usage:
    from django_extensions.aws_sqs_queue import SQSQueue, send_message

    # Using the class
    queue = SQSQueue('my-queue-name')
    queue.send({'event': 'user_created', 'user_id': 123})

    for message in queue.receive():
        process(message.body)
        message.delete()

    # Using functions
    send_message('my-queue', {'event': 'test'})
"""

import json
from django.conf import settings


def get_sqs_client():
    """Get SQS client with credentials from settings."""
    try:
        import boto3
    except ImportError:
        raise ImportError("boto3 is required. Install it with: pip install boto3")

    return boto3.client(
        'sqs',
        region_name=getattr(settings, 'AWS_SQS_REGION', getattr(settings, 'AWS_REGION', 'us-east-1')),
        aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
        aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
    )


def get_sqs_resource():
    """Get SQS resource."""
    try:
        import boto3
    except ImportError:
        raise ImportError("boto3 is required. Install it with: pip install boto3")

    return boto3.resource(
        'sqs',
        region_name=getattr(settings, 'AWS_SQS_REGION', getattr(settings, 'AWS_REGION', 'us-east-1')),
        aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
        aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
    )


class SQSMessage:
    """Wrapper for SQS message with convenient methods."""

    def __init__(self, message, queue):
        self._message = message
        self._queue = queue
        self._body = None

    @property
    def message_id(self):
        return self._message.get('MessageId')

    @property
    def receipt_handle(self):
        return self._message.get('ReceiptHandle')

    @property
    def body(self):
        """Get message body, parsing JSON if possible."""
        if self._body is None:
            raw_body = self._message.get('Body', '')
            try:
                self._body = json.loads(raw_body)
            except (json.JSONDecodeError, TypeError):
                self._body = raw_body
        return self._body

    @property
    def raw_body(self):
        """Get raw message body string."""
        return self._message.get('Body', '')

    @property
    def attributes(self):
        """Get message attributes."""
        return self._message.get('MessageAttributes', {})

    @property
    def md5_of_body(self):
        return self._message.get('MD5OfBody')

    def delete(self):
        """Delete this message from the queue."""
        self._queue.delete_message(self.receipt_handle)

    def change_visibility(self, timeout):
        """Change message visibility timeout."""
        self._queue.change_visibility(self.receipt_handle, timeout)


class SQSQueue:
    """
    AWS SQS Queue helper class.

    Usage:
        queue = SQSQueue('my-queue-name')
        # or
        queue = SQSQueue(queue_url='https://sqs.us-east-1.amazonaws.com/...')

        queue.send({'event': 'user_created'})
        queue.send_batch([{'id': 1}, {'id': 2}, {'id': 3}])

        for message in queue.receive(max_messages=10):
            process(message.body)
            message.delete()
    """

    def __init__(self, queue_name=None, queue_url=None):
        self.queue_name = queue_name
        self._queue_url = queue_url
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = get_sqs_client()
        return self._client

    @property
    def queue_url(self):
        if self._queue_url is None:
            if not self.queue_name:
                raise ValueError("Either queue_name or queue_url must be provided")
            response = self.client.get_queue_url(QueueName=self.queue_name)
            self._queue_url = response['QueueUrl']
        return self._queue_url

