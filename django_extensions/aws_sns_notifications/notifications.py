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

        if subject:
            publish_args['Subject'] = subject

        if attributes:
            publish_args['MessageAttributes'] = self._format_attributes(attributes)

        return self.client.publish(**publish_args)

    def _format_attributes(self, attributes):
        """Format attributes for SNS."""
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

    def subscribe(self, protocol, endpoint, attributes=None):
        """
        Subscribe to the topic.

        Args:
            protocol: Subscription protocol (email, sms, http, https, sqs, lambda)
            endpoint: Endpoint for the subscription
            attributes: Optional subscription attributes

        Returns:
            dict: SNS response with SubscriptionArn
        """
        subscribe_args = {
            'TopicArn': self.topic_arn,
            'Protocol': protocol,
            'Endpoint': endpoint,
        }

        if attributes:
            subscribe_args['Attributes'] = attributes

        return self.client.subscribe(**subscribe_args)


def publish_message(topic_arn, message, subject=None, attributes=None):
    """
    Publish a message to an SNS topic.

    Args:
        topic_arn: SNS topic ARN
        message: Message string or dict (will be JSON serialized)
        subject: Optional subject
        attributes: Optional message attributes

    Returns:
        dict: SNS response with MessageId
    """
    client = get_sns_client()

    if isinstance(message, dict):
        message = json.dumps(message)

    publish_args = {
        'TopicArn': topic_arn,
        'Message': message,
    }

    if subject:
        publish_args['Subject'] = subject

    if attributes:
        formatted = {}
        for key, value in attributes.items():
            if isinstance(value, str):
                formatted[key] = {'DataType': 'String', 'StringValue': value}
            elif isinstance(value, (int, float)):
                formatted[key] = {'DataType': 'Number', 'StringValue': str(value)}
            else:
                formatted[key] = {'DataType': 'String', 'StringValue': str(value)}
        publish_args['MessageAttributes'] = formatted

    return client.publish(**publish_args)


def publish_sms(phone_number, message, sender_id=None, message_type='Transactional'):
    """
    Send an SMS message via SNS.

    Args:
        phone_number: Phone number in E.164 format (+15551234567)
        message: SMS message (max 160 chars for standard)
        sender_id: Optional sender ID (not supported in all regions)
        message_type: 'Transactional' or 'Promotional'

    Returns:
        dict: SNS response with MessageId
    """
    client = get_sns_client()

    attributes = {
        'AWS.SNS.SMS.SMSType': {
            'DataType': 'String',
            'StringValue': message_type
        }
    }

    if sender_id:
        attributes['AWS.SNS.SMS.SenderID'] = {
            'DataType': 'String',
            'StringValue': sender_id
        }

    return client.publish(
        PhoneNumber=phone_number,
        Message=message,
        MessageAttributes=attributes
    )


def create_topic(name, attributes=None, tags=None):
    """
    Create an SNS topic.

    Args:
        name: Topic name
        attributes: Optional topic attributes
        tags: Optional tags dict

    Returns:
        dict: Response with TopicArn
    """
    client = get_sns_client()

    create_args = {'Name': name}

    if attributes:
        create_args['Attributes'] = attributes

    if tags:
        create_args['Tags'] = [{'Key': k, 'Value': v} for k, v in tags.items()]

    return client.create_topic(**create_args)


def subscribe_email(topic_arn, email):
    """
    Subscribe an email address to a topic.

    Args:
        topic_arn: Topic ARN
        email: Email address

    Returns:
        dict: Response with SubscriptionArn (pending confirmation)
    """
    client = get_sns_client()
    return client.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint=email
    )


def subscribe_sms(topic_arn, phone_number):
    """
    Subscribe a phone number to a topic.

    Args:
        topic_arn: Topic ARN
        phone_number: Phone number in E.164 format

    Returns:
        dict: Response with SubscriptionArn
    """
    client = get_sns_client()
    return client.subscribe(
        TopicArn=topic_arn,
        Protocol='sms',
        Endpoint=phone_number
    )


def subscribe_endpoint(topic_arn, protocol, endpoint, attributes=None):
    """
    Subscribe an endpoint to a topic.

    Args:
        topic_arn: Topic ARN
        protocol: Protocol (http, https, email, sms, sqs, lambda, application)
        endpoint: Endpoint URL or ARN
        attributes: Optional subscription attributes

    Returns:
        dict: Response with SubscriptionArn
    """
    client = get_sns_client()

    subscribe_args = {
        'TopicArn': topic_arn,
        'Protocol': protocol,
        'Endpoint': endpoint,
    }

    if attributes:
        subscribe_args['Attributes'] = attributes

    return client.subscribe(**subscribe_args)


def unsubscribe(subscription_arn):
    """
    Unsubscribe from a topic.

    Args:
        subscription_arn: Subscription ARN

    Returns:
        dict: SNS response
    """
    client = get_sns_client()
    return client.unsubscribe(SubscriptionArn=subscription_arn)


def delete_topic(topic_arn):
    """
    Delete an SNS topic.

    Args:
        topic_arn: Topic ARN

    Returns:
        dict: SNS response
    """
    client = get_sns_client()
    return client.delete_topic(TopicArn=topic_arn)
