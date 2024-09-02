# AWS S3 Storage

Amazon S3 file storage backend for Django.

## Installation

```bash
pip install boto3
```

```python
INSTALLED_APPS = [
    'django_extensions.aws_s3_storage',
]
```

## Configuration

```python
# settings.py
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_S3_BUCKET_NAME = 'my-bucket'
AWS_S3_REGION = 'us-east-1'

# Optional
AWS_S3_CUSTOM_DOMAIN = 'cdn.example.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
AWS_DEFAULT_ACL = 'public-read'
```

## Usage

### As Default Storage

```python
# settings.py
DEFAULT_FILE_STORAGE = 'django_extensions.aws_s3_storage.S3Storage'
```

### Direct Upload

```python
from django_extensions.aws_s3_storage import s3_upload, s3_download

# Upload file
url = s3_upload(file_obj, 'uploads/image.png')
# https://my-bucket.s3.amazonaws.com/uploads/image.png

# Upload with options
url = s3_upload(
    file_obj,
    'uploads/document.pdf',
    acl='private',
    content_type='application/pdf',
    metadata={'user_id': '123'}
)

# Download file
content = s3_download('uploads/image.png')
```

### Storage Class

```python
from django_extensions.aws_s3_storage import S3Storage

storage = S3Storage(bucket_name='my-bucket')

# Save file
name = storage.save('path/file.txt', content)

# Open file
f = storage.open('path/file.txt')

# Delete file
storage.delete('path/file.txt')

# Check existence
exists = storage.exists('path/file.txt')

# Get URL
url = storage.url('path/file.txt')
```

### Model Integration

```python
from django.db import models

class Document(models.Model):
    file = models.FileField(upload_to='documents/')
    # Files automatically stored in S3
```

## Presigned URLs

```python
from django_extensions.aws_s3_storage import generate_presigned_url

# For download
url = generate_presigned_url('private/document.pdf', expiration=3600)

# For upload
upload_url = generate_presigned_upload_url('uploads/new-file.pdf')
```

## License

MIT
