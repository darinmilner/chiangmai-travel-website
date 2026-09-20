"""
Test configuration for Image Processor Lambda
"""
import os
import sys
from io import BytesIO
import pytest
from PIL import Image


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)  # src directory
FAKE_LAYER_DIR = os.path.join(TESTS_DIR, "fake_layer")

if FAKE_LAYER_DIR not in sys.path:
    sys.path.insert(0, FAKE_LAYER_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(1, PROJECT_ROOT)


class MockS3Client:
    def __init__(self, bucket: str = "test-bucket"):
        self.bucket = bucket
        self.should_fail = False
        self.error_message = "S3 Error"

    def set_fail_mode(self, fail: bool, message: str = "S3 Error"):
        self.should_fail = fail
        self.error_message = message

    def download_file(self, Bucket=None, Key=None, Filename=None, *args, **kwargs):
        # Fall back to positional args if called positionally
        bucket = Bucket or (args[0] if len(args) > 0 else None)
        key = Key or (args[1] if len(args) > 1 else None)
        filename = Filename or (args[2] if len(args) > 2 else None)
        print(f"Bucket location = {bucket/key} Filename = {filename}")

        # Ensure destination file exists so PIL.Image.open can read it
        if filename:
            from PIL import Image
            img = Image.new('RGB', (100, 100), color="red")
            img.save(filename)

    def upload_file(self, filename=None, bucket=None, key=None, *args, **kwargs):
        if self.should_fail:
            raise Exception(self.error_message)
        return True

    def get_object_url(self, bucket, key):
        return f"https://d1111111111111.cloudfront.net/{key}"


@pytest.fixture
def mock_s3_client():
    return MockS3Client()


@pytest.fixture(autouse=True)
def mock_s3_client_patch(mocker, mock_s3_client):
    """Patch S3Client in modules that exist in image-processor."""
    mocker.patch('processor.S3Client', return_value=mock_s3_client, create=True)
    mocker.patch('lambda_function.S3Client', return_value=mock_s3_client, create=True)
    return mock_s3_client


@pytest.fixture
def mock_pil_image():
    """Fixture providing a PIL Image object in memory."""
    img = Image.new("RGB", (1000, 1000), color="blue")
    buf = BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return Image.open(buf)


@pytest.fixture
def s3_event():
    """Fixture for single S3 event."""
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "test-bucket"},
                    "object": {"key": "static/villa/test-image.jpg"}
                }
            }
        ]
    }


@pytest.fixture
def s3_event_thumb():
    """Fixture for S3 event pointing to an already processed thumbnail."""
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "test-bucket"},
                    "object": {"key": "static/villa/test-image_thumb.jpg"}
                }
            }
        ]
    }


@pytest.fixture
def s3_event_multiple():
    """Fixture for multiple S3 event records."""
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "test-bucket"},
                    "object": {"key": "static/villa/image1.jpg"}
                }
            },
            {
                "s3": {
                    "bucket": {"name": "test-bucket"},
                    "object": {"key": "static/villa/image2.jpg"}
                }
            }
        ]
    }


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    env_vars = {
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_SECURITY_TOKEN': 'testing',
        'AWS_SESSION_TOKEN': 'testing',
        'AWS_DEFAULT_REGION': 'ap-southeast-1',
        'AWS_REGION': 'ap-southeast-1',
        'S3_BUCKET': 'test-bucket',
        'S3_BUCKET_NAME': 'test-bucket',
        'S3_PREFIX': 'villa/',
        'CLOUDFRONT_URL': 'https://test.cloudfront.net',
        'THUMBNAIL_SIZE': '300,200',
        'MEDIUM_SIZE': '800,600',
        'CAROUSEL_SIZE': '1200,800',
        'QUALITY': '85',
        'LOG_LEVEL': 'DEBUG',
        'ENVIRONMENT': 'test',
        'MAX_IMAGE_SIZE_MB': '10',
    }
    for key, val in env_vars.items():
        monkeypatch.setenv(key, val)
