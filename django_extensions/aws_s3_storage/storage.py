"""
AWS S3 Storage Backend for Django.

Usage:
    # settings.py
    DEFAULT_FILE_STORAGE = 'django_extensions.aws_s3_storage.S3Storage'

    AWS_S3_BUCKET_NAME = 'my-bucket'
    AWS_S3_REGION = 'us-east-1'
    AWS_ACCESS_KEY_ID = 'your-key'
    AWS_SECRET_ACCESS_KEY = 'your-secret'

    # Or use directly
    from django_extensions.aws_s3_storage import s3_upload, get_presigned_url

    url = s3_upload(file_obj, 'path/to/file.txt')
    signed_url = get_presigned_url('path/to/file.txt', expires=3600)
"""

import os
import mimetypes
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


def get_boto3_client(service='s3'):
    """Get boto3 client with credentials from settings."""
    try:
        import boto3
    except ImportError:
        raise ImportError("boto3 is required. Install it with: pip install boto3")

    return boto3.client(
        service,
        region_name=getattr(settings, 'AWS_S3_REGION', 'us-east-1'),
        aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
        aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
    )


def get_boto3_resource(service='s3'):
    """Get boto3 resource with credentials from settings."""
    try:
        import boto3
    except ImportError:
        raise ImportError("boto3 is required. Install it with: pip install boto3")

    return boto3.resource(
        service,
        region_name=getattr(settings, 'AWS_S3_REGION', 'us-east-1'),
        aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
        aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
    )


@deconstructible
class S3Storage(Storage):
    """
    Custom S3 storage backend for Django.

    Settings:
        AWS_S3_BUCKET_NAME: The S3 bucket name
        AWS_S3_REGION: AWS region (default: us-east-1)
        AWS_ACCESS_KEY_ID: AWS access key
        AWS_SECRET_ACCESS_KEY: AWS secret key
        AWS_S3_CUSTOM_DOMAIN: Custom domain for URLs (optional)
        AWS_S3_FILE_OVERWRITE: Whether to overwrite files (default: True)
        AWS_S3_DEFAULT_ACL: Default ACL (default: 'private')
        AWS_S3_OBJECT_PARAMETERS: Extra object parameters (optional)
    """

    def __init__(self, bucket_name=None, region=None, custom_domain=None):
        self.bucket_name = bucket_name or getattr(settings, 'AWS_S3_BUCKET_NAME', None)
        self.region = region or getattr(settings, 'AWS_S3_REGION', 'us-east-1')
        self.custom_domain = custom_domain or getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', None)
        self.file_overwrite = getattr(settings, 'AWS_S3_FILE_OVERWRITE', True)
        self.default_acl = getattr(settings, 'AWS_S3_DEFAULT_ACL', 'private')
        self.object_parameters = getattr(settings, 'AWS_S3_OBJECT_PARAMETERS', {})

        if not self.bucket_name:
            raise ValueError("AWS_S3_BUCKET_NAME must be set")

        self._client = None
        self._resource = None

    @property
    def client(self):
        if self._client is None:
            self._client = get_boto3_client('s3')
        return self._client

    @property
    def bucket(self):
        if self._resource is None:
            self._resource = get_boto3_resource('s3')
        return self._resource.Bucket(self.bucket_name)

    def _normalize_name(self, name):
        """Normalize the path name."""
        return name.lstrip('/')

    def _get_content_type(self, name):
        """Get content type for a file."""
        content_type, _ = mimetypes.guess_type(name)
        return content_type or 'application/octet-stream'

    def _save(self, name, content):
        """Save file to S3."""
        name = self._normalize_name(name)

        extra_args = {
            'ContentType': self._get_content_type(name),
            **self.object_parameters,
        }

        if self.default_acl:
            extra_args['ACL'] = self.default_acl

        # Read content
        content.seek(0)
        data = content.read()

        self.client.put_object(
            Bucket=self.bucket_name,
            Key=name,
            Body=data,
            **extra_args
