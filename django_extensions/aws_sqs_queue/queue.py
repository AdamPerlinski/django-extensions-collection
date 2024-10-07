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

    def send(self, message, delay_seconds=0, attributes=None, deduplication_id=None, group_id=None):
        """
        Send a message to the queue.

        Args:
            message: Message string or dict (will be JSON serialized)
            delay_seconds: Delay before message is available (0-900)
            attributes: Optional message attributes
            deduplication_id: For FIFO queues
            group_id: For FIFO queues

        Returns:
            dict: SQS response with MessageId
        """
        if isinstance(message, dict):
            message = json.dumps(message)

        send_args = {
            'QueueUrl': self.queue_url,
            'MessageBody': message,
            'DelaySeconds': delay_seconds,
        }

        if attributes:
            send_args['MessageAttributes'] = self._format_attributes(attributes)

        if deduplication_id:
            send_args['MessageDeduplicationId'] = deduplication_id

        if group_id:
            send_args['MessageGroupId'] = group_id

        return self.client.send_message(**send_args)

    def send_batch(self, messages, delay_seconds=0):
        """
        Send multiple messages in a batch.

        Args:
            messages: List of messages (strings or dicts)
            delay_seconds: Delay for all messages

        Returns:
            dict: SQS response with Successful and Failed lists
        """
        entries = []
        for i, msg in enumerate(messages):
            if isinstance(msg, dict):
                msg = json.dumps(msg)
            entries.append({
                'Id': str(i),
                'MessageBody': msg,
                'DelaySeconds': delay_seconds,
            })

        # SQS allows max 10 messages per batch
        results = {'Successful': [], 'Failed': []}
        for batch_start in range(0, len(entries), 10):
            batch = entries[batch_start:batch_start + 10]
            response = self.client.send_message_batch(
                QueueUrl=self.queue_url,
                Entries=batch
            )
            results['Successful'].extend(response.get('Successful', []))
            results['Failed'].extend(response.get('Failed', []))

        return results

    def receive(self, max_messages=1, wait_time=0, visibility_timeout=None, attributes=None):
        """
        Receive messages from the queue.

        Args:
            max_messages: Maximum messages to receive (1-10)
            wait_time: Long polling wait time in seconds (0-20)
            visibility_timeout: Visibility timeout in seconds
            attributes: List of attribute names to return

        Yields:
            SQSMessage objects
        """
        receive_args = {
            'QueueUrl': self.queue_url,
            'MaxNumberOfMessages': min(max_messages, 10),
            'WaitTimeSeconds': wait_time,
        }

        if visibility_timeout is not None:
            receive_args['VisibilityTimeout'] = visibility_timeout

        if attributes:
            receive_args['MessageAttributeNames'] = attributes
        else:
            receive_args['MessageAttributeNames'] = ['All']

        response = self.client.receive_message(**receive_args)

        for message in response.get('Messages', []):
            yield SQSMessage(message, self)

    def delete_message(self, receipt_handle):
        """Delete a message from the queue."""
        self.client.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle
        )

    def delete_batch(self, receipt_handles):
        """Delete multiple messages."""
        entries = [
            {'Id': str(i), 'ReceiptHandle': rh}
            for i, rh in enumerate(receipt_handles)
        ]

        # Max 10 per batch
        for batch_start in range(0, len(entries), 10):
            batch = entries[batch_start:batch_start + 10]
            self.client.delete_message_batch(
                QueueUrl=self.queue_url,
                Entries=batch
            )

    def change_visibility(self, receipt_handle, timeout):
        """Change message visibility timeout."""
        self.client.change_message_visibility(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle,
            VisibilityTimeout=timeout
        )

    def purge(self):
        """Purge all messages from the queue."""
        self.client.purge_queue(QueueUrl=self.queue_url)

    def get_attributes(self, attributes=None):
        """Get queue attributes."""
        if attributes is None:
            attributes = ['All']

        response = self.client.get_queue_attributes(
            QueueUrl=self.queue_url,
            AttributeNames=attributes
        )
        return response.get('Attributes', {})

    @property
    def message_count(self):
        """Get approximate number of messages in queue."""
        attrs = self.get_attributes(['ApproximateNumberOfMessages'])
        return int(attrs.get('ApproximateNumberOfMessages', 0))

    def _format_attributes(self, attributes):
        """Format attributes for SQS."""
        formatted = {}
        for key, value in attributes.items():
            if isinstance(value, str):
                formatted[key] = {'DataType': 'String', 'StringValue': value}
            elif isinstance(value, (int, float)):
                formatted[key] = {'DataType': 'Number', 'StringValue': str(value)}
            elif isinstance(value, bytes):
                formatted[key] = {'DataType': 'Binary', 'BinaryValue': value}
            else:
                formatted[key] = {'DataType': 'String', 'StringValue': str(value)}
        return formatted


def send_message(queue_name, message, delay_seconds=0, **kwargs):
    """
    Send a message to an SQS queue.

    Args:
        queue_name: Queue name or URL
        message: Message string or dict
        delay_seconds: Delay in seconds
        **kwargs: Additional send_message arguments

    Returns:
        dict: SQS response
    """
    queue = SQSQueue(queue_name=queue_name)
    return queue.send(message, delay_seconds=delay_seconds, **kwargs)


def receive_messages(queue_name, max_messages=1, wait_time=0, delete=False):
    """
    Receive messages from an SQS queue.

    Args:
        queue_name: Queue name or URL
        max_messages: Maximum messages to receive
        wait_time: Long polling wait time
        delete: Whether to delete messages after receiving

    Returns:
        list: List of message bodies
    """
    queue = SQSQueue(queue_name=queue_name)
    messages = []

    for msg in queue.receive(max_messages=max_messages, wait_time=wait_time):
        messages.append(msg.body)
        if delete:
            msg.delete()

    return messages


def delete_message(queue_name, receipt_handle):
    """Delete a message from an SQS queue."""
    queue = SQSQueue(queue_name=queue_name)
    queue.delete_message(receipt_handle)


def create_queue(queue_name, attributes=None, tags=None, fifo=False):
    """
    Create an SQS queue.

    Args:
        queue_name: Queue name (add .fifo suffix for FIFO queues)
        attributes: Optional queue attributes
        tags: Optional tags dict
        fifo: Whether to create a FIFO queue

    Returns:
        str: Queue URL
    """
    client = get_sqs_client()

    create_args = {'QueueName': queue_name}

    if attributes is None:
        attributes = {}

    if fifo:
        if not queue_name.endswith('.fifo'):
            queue_name += '.fifo'
            create_args['QueueName'] = queue_name
        attributes['FifoQueue'] = 'true'

    if attributes:
        create_args['Attributes'] = attributes

    if tags:
        create_args['Tags'] = tags

    response = client.create_queue(**create_args)
    return response['QueueUrl']


def get_queue_url(queue_name):
    """Get the URL for a queue by name."""
    client = get_sqs_client()
    response = client.get_queue_url(QueueName=queue_name)
    return response['QueueUrl']


def delete_queue(queue_url):
    """Delete an SQS queue."""
    client = get_sqs_client()
    client.delete_queue(QueueUrl=queue_url)
