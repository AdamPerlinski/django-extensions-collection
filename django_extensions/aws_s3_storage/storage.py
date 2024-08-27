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
        )

        return name

    def _open(self, name, mode='rb'):
        """Open file from S3."""
        name = self._normalize_name(name)

        response = self.client.get_object(
            Bucket=self.bucket_name,
            Key=name
        )

        return ContentFile(response['Body'].read(), name=name)

    def delete(self, name):
        """Delete file from S3."""
        name = self._normalize_name(name)
        self.client.delete_object(
            Bucket=self.bucket_name,
            Key=name
        )

    def exists(self, name):
        """Check if file exists in S3."""
        name = self._normalize_name(name)
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=name
            )
            return True
        except Exception:
            return False

    def listdir(self, path=''):
        """List contents of a path in S3."""
        path = self._normalize_name(path)
        if path and not path.endswith('/'):
            path += '/'

        directories = set()
        files = []

        paginator = self.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=self.bucket_name, Prefix=path, Delimiter='/'):
            # Get directories
            for prefix in page.get('CommonPrefixes', []):
                directories.add(prefix['Prefix'][len(path):].rstrip('/'))

            # Get files
            for obj in page.get('Contents', []):
                key = obj['Key'][len(path):]
                if key:
                    files.append(key)

        return list(directories), files

    def size(self, name):
        """Get file size."""
        name = self._normalize_name(name)
        response = self.client.head_object(
            Bucket=self.bucket_name,
            Key=name
        )
        return response['ContentLength']

    def url(self, name):
        """Get URL for file."""
        name = self._normalize_name(name)

        if self.custom_domain:
            return f"https://{self.custom_domain}/{name}"

        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{name}"

    def get_presigned_url(self, name, expires=3600, method='get_object'):
        """Get a presigned URL for the file."""
        name = self._normalize_name(name)

        params = {
            'Bucket': self.bucket_name,
            'Key': name,
        }

        return self.client.generate_presigned_url(
            method,
            Params=params,
            ExpiresIn=expires
        )

    def get_accessed_time(self, name):
        """Not supported by S3."""
        raise NotImplementedError("S3 doesn't track access time")

    def get_created_time(self, name):
        """Not supported by S3."""
        raise NotImplementedError("S3 doesn't track creation time")

    def get_modified_time(self, name):
        """Get last modified time."""
        name = self._normalize_name(name)
        response = self.client.head_object(
            Bucket=self.bucket_name,
            Key=name
        )
        return response['LastModified']


def s3_upload(file_obj, key, bucket=None, content_type=None, acl=None, metadata=None):
    """
    Upload a file to S3.

    Args:
        file_obj: File object or bytes to upload
        key: S3 key (path)
        bucket: Bucket name (defaults to AWS_S3_BUCKET_NAME)
        content_type: Content type (auto-detected if not provided)
        acl: Access control (default: private)
        metadata: Optional metadata dict

    Returns:
        str: URL of uploaded file
    """
    client = get_boto3_client('s3')
    bucket = bucket or getattr(settings, 'AWS_S3_BUCKET_NAME')
    region = getattr(settings, 'AWS_S3_REGION', 'us-east-1')

    extra_args = {}

    if content_type:
        extra_args['ContentType'] = content_type
    else:
        ct, _ = mimetypes.guess_type(key)
        if ct:
            extra_args['ContentType'] = ct

    if acl:
        extra_args['ACL'] = acl

    if metadata:
        extra_args['Metadata'] = metadata

    # Handle different input types
    if hasattr(file_obj, 'read'):
        file_obj.seek(0)
        data = file_obj.read()
    elif isinstance(file_obj, bytes):
        data = file_obj
    else:
        data = str(file_obj).encode()

    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=data,
        **extra_args
    )

    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"


def s3_download(key, bucket=None):
    """
    Download a file from S3.

    Args:
        key: S3 key (path)
        bucket: Bucket name

    Returns:
        bytes: File contents
    """
    client = get_boto3_client('s3')
    bucket = bucket or getattr(settings, 'AWS_S3_BUCKET_NAME')

    response = client.get_object(
        Bucket=bucket,
        Key=key
    )

    return response['Body'].read()


def get_presigned_url(key, bucket=None, expires=3600, method='get_object'):
    """
    Get a presigned URL for an S3 object.

    Args:
        key: S3 key (path)
        bucket: Bucket name
        expires: Expiration time in seconds (default: 1 hour)
        method: S3 method ('get_object' or 'put_object')

    Returns:
        str: Presigned URL
    """
    client = get_boto3_client('s3')
    bucket = bucket or getattr(settings, 'AWS_S3_BUCKET_NAME')

    return client.generate_presigned_url(
        method,
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=expires
    )


def s3_delete(key, bucket=None):
    """
    Delete a file from S3.

    Args:
        key: S3 key (path)
        bucket: Bucket name
    """
    client = get_boto3_client('s3')
    bucket = bucket or getattr(settings, 'AWS_S3_BUCKET_NAME')

    client.delete_object(
        Bucket=bucket,
        Key=key
    )


def s3_copy(source_key, dest_key, source_bucket=None, dest_bucket=None):
    """
    Copy a file within S3.

    Args:
        source_key: Source S3 key
        dest_key: Destination S3 key
        source_bucket: Source bucket (defaults to AWS_S3_BUCKET_NAME)
        dest_bucket: Destination bucket (defaults to source bucket)
    """
    client = get_boto3_client('s3')
    source_bucket = source_bucket or getattr(settings, 'AWS_S3_BUCKET_NAME')
    dest_bucket = dest_bucket or source_bucket

    client.copy_object(
        CopySource={'Bucket': source_bucket, 'Key': source_key},
        Bucket=dest_bucket,
        Key=dest_key
    )
