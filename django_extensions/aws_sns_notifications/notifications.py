"""
AWS SNS Notifications for Django.

Usage:
    from django_extensions.aws_sns_notifications import publish_message, publish_sms

    # Publish to a topic
    publish_message(
        topic_arn='arn:aws:sns:us-east-1:123456789:my-topic',
        message='Hello World',
        subject='Notification'
    )

    # Send SMS
    publish_sms(
        phone_number='+15551234567',
        message='Your verification code is 123456'
    )
"""

import json
from django.conf import settings


def get_sns_client():
    """Get SNS client with credentials from settings."""
    try:
        import boto3
    except ImportError:
        raise ImportError("boto3 is required. Install it with: pip install boto3")

    return boto3.client(
        'sns',
        region_name=getattr(settings, 'AWS_SNS_REGION', getattr(settings, 'AWS_REGION', 'us-east-1')),
        aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
        aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
    )


class SNSNotifier:
    """
    AWS SNS notification helper class.

    Usage:
        notifier = SNSNotifier(topic_arn='arn:aws:sns:...')
        notifier.publish('Hello World')
        notifier.publish_json({'event': 'user_created', 'user_id': 123})
    """

    def __init__(self, topic_arn=None, default_subject=None):
        self.topic_arn = topic_arn or getattr(settings, 'AWS_SNS_TOPIC_ARN', None)
        self.default_subject = default_subject
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = get_sns_client()
        return self._client

    def publish(self, message, subject=None, attributes=None, deduplication_id=None, group_id=None):
        """
        Publish a message to the SNS topic.

        Args:
            message: Message string
            subject: Optional subject (for email subscriptions)
            attributes: Optional message attributes dict
            deduplication_id: For FIFO topics
            group_id: For FIFO topics

        Returns:
            dict: SNS response with MessageId
        """
        if not self.topic_arn:
            raise ValueError("topic_arn must be set")

        publish_args = {
            'TopicArn': self.topic_arn,
            'Message': message,
        }

        if subject or self.default_subject:
            publish_args['Subject'] = subject or self.default_subject

        if attributes:
            publish_args['MessageAttributes'] = self._format_attributes(attributes)

        if deduplication_id:
            publish_args['MessageDeduplicationId'] = deduplication_id

        if group_id:
            publish_args['MessageGroupId'] = group_id

        return self.client.publish(**publish_args)

    def publish_json(self, data, subject=None, **kwargs):
        """
        Publish a JSON message.

        Args:
            data: Dict to serialize as JSON
            subject: Optional subject
            **kwargs: Additional publish args

        Returns:
            dict: SNS response
        """
        return self.publish(json.dumps(data), subject=subject, **kwargs)

    def publish_to_target(self, target_arn, message, subject=None, attributes=None):
        """
        Publish to a specific target (endpoint ARN).

        Args:
            target_arn: Target endpoint ARN
            message: Message string
            subject: Optional subject
            attributes: Optional attributes

        Returns:
            dict: SNS response
        """
        publish_args = {
            'TargetArn': target_arn,
            'Message': message,
        }
