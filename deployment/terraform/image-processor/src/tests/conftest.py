"""
Test configuration with fake layer for Image Processor Lambda
"""
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Get the absolute path to the tests directory
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)  # src directory
FAKE_LAYER_DIR = os.path.join(TESTS_DIR, "fake_layer")

# CRITICAL: Insert fake_layer at position 0 to override real shared-layer imports
if FAKE_LAYER_DIR not in sys.path:
    sys.path.insert(0, FAKE_LAYER_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(1, PROJECT_ROOT)


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for tests"""
    env_vars = {
        # AWS Dummy Credentials for Boto3
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_SECURITY_TOKEN': 'testing',
        'AWS_SESSION_TOKEN': 'testing',
        'AWS_DEFAULT_REGION': 'ap-southeast-1',
        'AWS_REGION': 'ap-southeast-1',
        'AWS_ACCOUNT_ID': '123456789012',

        # S3 Bucket env variables (covering all possible key names used in code)
        'S3_BUCKET': 'test-bucket',
        'BUCKET_NAME': 'test-bucket',
        'SOURCE_BUCKET_NAME': 'test-bucket',
        'PROCESSED_BUCKET_NAME': 'test-bucket',
        'S3_PREFIX': 'villa/',

        # Image Processor settings
        'CLOUDFRONT_URL': 'https://test.cloudfront.net',
        'THUMBNAIL_SIZE': '300,200',
        'MEDIUM_SIZE': '800,600',
        'CAROUSEL_SIZE': '1200,800',
        'QUALITY': '85',
        'LOG_LEVEL': 'DEBUG',
        'ENVIRONMENT': 'test',
        'MAX_IMAGE_SIZE_MB': '10',
    }

    with patch.dict(os.environ, env_vars, clear=False):
        yield


@pytest.fixture
def mock_pil_image():
    """Mock PIL Image for tests"""
    with patch('PIL.Image.open') as mock_open:
        mock_img = MagicMock()
        mock_img.width = 1920
        mock_img.height = 1080
        mock_img.mode = 'RGB'

        # Mock copy for resize
        mock_img_copy = MagicMock()
        mock_img_copy.width = 800
        mock_img_copy.height = 600
        mock_img_copy.mode = 'RGB'
        mock_img.copy.return_value = mock_img_copy

        # Mock thumbnail
        mock_img.thumbnail = MagicMock()

        # Mock resize with width only
        mock_img_resized = MagicMock()
        mock_img_resized.width = 800
        mock_img_resized.height = 450
        mock_img_resized.mode = 'RGB'
        mock_img.resize.return_value = mock_img_resized

        mock_open.return_value = mock_img
        yield mock_img


@pytest.fixture
def s3_event():
    """Sample S3 event"""
    return {
        'Records': [
            {
                's3': {
                    'bucket': {'name': 'test-bucket'},
                    'object': {'key': 'villa/test-image.jpg'}
                }
            }
        ]
    }


@pytest.fixture
def s3_event_multiple():
    """Sample S3 event with multiple records"""
    return {
        'Records': [
            {
                's3': {
                    'bucket': {'name': 'test-bucket'},
                    'object': {'key': 'villa/image1.jpg'}
                }
            },
            {
                's3': {
                    'bucket': {'name': 'test-bucket'},
                    'object': {'key': 'villa/image2.jpg'}
                }
            }
        ]
    }


@pytest.fixture
def s3_event_thumb():
    """Sample S3 event with already processed image"""
    return {
        'Records': [
            {
                's3': {
                    'bucket': {'name': 'test-bucket'},
                    'object': {'key': 'villa/test-image_thumb.jpg'}
                }
            }
        ]
    }
