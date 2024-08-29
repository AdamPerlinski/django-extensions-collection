"""Tests for AWS S3 Storage."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from io import BytesIO
from django.core.files.base import ContentFile

from .storage import S3Storage, s3_upload, s3_download, get_presigned_url


class TestS3Storage:
    """Test cases for S3Storage."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.AWS_S3_BUCKET_NAME = 'test-bucket'
        settings.AWS_S3_REGION = 'us-east-1'
        settings.AWS_ACCESS_KEY_ID = 'test-key'
        settings.AWS_SECRET_ACCESS_KEY = 'test-secret'
        return settings

    @pytest.fixture
    def mock_client(self):
        """Create mock boto3 client."""
        return MagicMock()

    @pytest.fixture
    def storage(self, mock_settings, mock_client):
        """Create storage instance with mocked client."""
        with patch('django_extensions.aws_s3_storage.storage.get_boto3_client', return_value=mock_client):
            s = S3Storage()
            s._client = mock_client
            return s

    def test_init_with_settings(self, mock_settings):
        """Test storage initializes from settings."""
        with patch('django_extensions.aws_s3_storage.storage.get_boto3_client'):
            storage = S3Storage()
            assert storage.bucket_name == 'test-bucket'
            assert storage.region == 'us-east-1'

    def test_init_with_params(self, mock_settings):
        """Test storage initializes with explicit params."""
        with patch('django_extensions.aws_s3_storage.storage.get_boto3_client'):
            storage = S3Storage(
                bucket_name='custom-bucket',
                region='eu-west-1',
                custom_domain='cdn.example.com'
            )
            assert storage.bucket_name == 'custom-bucket'
            assert storage.region == 'eu-west-1'
            assert storage.custom_domain == 'cdn.example.com'

    def test_init_requires_bucket(self, settings):
        """Test storage requires bucket name."""
        settings.AWS_S3_BUCKET_NAME = None
        with pytest.raises(ValueError):
            S3Storage()

    def test_normalize_name(self, storage):
        """Test path normalization."""
        assert storage._normalize_name('/path/to/file.txt') == 'path/to/file.txt'
        assert storage._normalize_name('path/to/file.txt') == 'path/to/file.txt'

    def test_get_content_type(self, storage):
        """Test content type detection."""
        assert storage._get_content_type('file.txt') == 'text/plain'
        assert storage._get_content_type('file.jpg') == 'image/jpeg'
        assert storage._get_content_type('file.pdf') == 'application/pdf'
        assert storage._get_content_type('file.unknown') == 'application/octet-stream'

    def test_save(self, storage, mock_client):
        """Test saving a file."""
        content = ContentFile(b'test content', name='test.txt')

        result = storage._save('path/to/test.txt', content)

        assert result == 'path/to/test.txt'
        mock_client.put_object.assert_called_once()
        call_kwargs = mock_client.put_object.call_args[1]
        assert call_kwargs['Bucket'] == 'test-bucket'
        assert call_kwargs['Key'] == 'path/to/test.txt'

    def test_open(self, storage, mock_client):
        """Test opening a file."""
        mock_client.get_object.return_value = {
            'Body': MagicMock(read=lambda: b'file contents')
        }

        result = storage._open('path/to/test.txt')

        assert result.read() == b'file contents'
        mock_client.get_object.assert_called_once()

    def test_delete(self, storage, mock_client):
        """Test deleting a file."""
        storage.delete('path/to/test.txt')

        mock_client.delete_object.assert_called_once_with(
            Bucket='test-bucket',
            Key='path/to/test.txt'
        )

    def test_exists_true(self, storage, mock_client):
        """Test exists returns True when file exists."""
        mock_client.head_object.return_value = {}

        assert storage.exists('path/to/test.txt') is True

    def test_exists_false(self, storage, mock_client):
        """Test exists returns False when file doesn't exist."""
        mock_client.head_object.side_effect = Exception('Not found')

        assert storage.exists('path/to/test.txt') is False

    def test_size(self, storage, mock_client):
        """Test getting file size."""
        mock_client.head_object.return_value = {'ContentLength': 1024}

        assert storage.size('path/to/test.txt') == 1024

    def test_url(self, storage):
        """Test generating URL."""
        url = storage.url('path/to/file.txt')
        assert 'test-bucket' in url
        assert 'path/to/file.txt' in url

    def test_url_with_custom_domain(self, mock_settings, mock_client):
        """Test URL with custom domain."""
        with patch('django_extensions.aws_s3_storage.storage.get_boto3_client', return_value=mock_client):
            storage = S3Storage(custom_domain='cdn.example.com')
            storage._client = mock_client

            url = storage.url('path/to/file.txt')
            assert url == 'https://cdn.example.com/path/to/file.txt'

    def test_get_presigned_url(self, storage, mock_client):
        """Test generating presigned URL."""
        mock_client.generate_presigned_url.return_value = 'https://signed-url'

        url = storage.get_presigned_url('path/to/file.txt', expires=7200)

        assert url == 'https://signed-url'
        mock_client.generate_presigned_url.assert_called_once()


class TestS3Functions:
    """Test S3 helper functions."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.AWS_S3_BUCKET_NAME = 'test-bucket'
        settings.AWS_S3_REGION = 'us-east-1'
        settings.AWS_ACCESS_KEY_ID = 'test-key'
        settings.AWS_SECRET_ACCESS_KEY = 'test-secret'
        return settings

    def test_s3_upload_bytes(self, mock_settings):
        """Test uploading bytes."""
        with patch('django_extensions.aws_s3_storage.storage.get_boto3_client') as mock_get:
            mock_client = MagicMock()
            mock_get.return_value = mock_client

            url = s3_upload(b'test data', 'path/to/file.txt')

            assert 'test-bucket' in url
            mock_client.put_object.assert_called_once()

    def test_s3_upload_file_object(self, mock_settings):
        """Test uploading file object."""
        with patch('django_extensions.aws_s3_storage.storage.get_boto3_client') as mock_get:
            mock_client = MagicMock()
            mock_get.return_value = mock_client

            file_obj = BytesIO(b'test data')
            url = s3_upload(file_obj, 'path/to/file.txt')

            assert 'test-bucket' in url

    def test_s3_upload_with_metadata(self, mock_settings):
        """Test uploading with metadata."""
        with patch('django_extensions.aws_s3_storage.storage.get_boto3_client') as mock_get:
            mock_client = MagicMock()
            mock_get.return_value = mock_client

            s3_upload(
                b'test data',
                'path/to/file.txt',
                metadata={'author': 'test'}
            )

            call_kwargs = mock_client.put_object.call_args[1]
            assert call_kwargs['Metadata'] == {'author': 'test'}

    def test_s3_download(self, mock_settings):
        """Test downloading a file."""
        with patch('django_extensions.aws_s3_storage.storage.get_boto3_client') as mock_get:
            mock_client = MagicMock()
            mock_client.get_object.return_value = {
                'Body': MagicMock(read=lambda: b'file contents')
            }
            mock_get.return_value = mock_client

            data = s3_download('path/to/file.txt')

            assert data == b'file contents'

    def test_get_presigned_url(self, mock_settings):
        """Test getting presigned URL."""
        with patch('django_extensions.aws_s3_storage.storage.get_boto3_client') as mock_get:
            mock_client = MagicMock()
            mock_client.generate_presigned_url.return_value = 'https://signed-url'
            mock_get.return_value = mock_client

            url = get_presigned_url('path/to/file.txt', expires=3600)

            assert url == 'https://signed-url'
            mock_client.generate_presigned_url.assert_called_once()

    def test_get_presigned_url_for_upload(self, mock_settings):
        """Test getting presigned URL for upload."""
        with patch('django_extensions.aws_s3_storage.storage.get_boto3_client') as mock_get:
            mock_client = MagicMock()
            mock_client.generate_presigned_url.return_value = 'https://upload-url'
            mock_get.return_value = mock_client

            url = get_presigned_url('path/to/file.txt', method='put_object')

            mock_client.generate_presigned_url.assert_called_with(
                'put_object',
                Params={'Bucket': 'test-bucket', 'Key': 'path/to/file.txt'},
                ExpiresIn=3600
            )
