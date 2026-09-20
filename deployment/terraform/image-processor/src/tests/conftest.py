"""
Test configuration for Image Processor Lambda
"""
import os
import sys
import pytest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)  # src directory
FAKE_LAYER_DIR = os.path.join(TESTS_DIR, "fake_layer")

if FAKE_LAYER_DIR not in sys.path:
    sys.path.insert(0, FAKE_LAYER_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(1, PROJECT_ROOT)


class MockS3Client:
    def __init__(self):
        self.should_fail = False
        self.error_message = "S3 Error"

    def set_fail_mode(self, fail: bool, message: str = "S3 Error"):
        self.should_fail = fail
        self.error_message = message

    def download_file(self, bucket, key, destination):
        if self.should_fail:
            raise Exception(self.error_message)
        return True

    def upload_file(self, file_path, bucket, key, content_type=None):
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
