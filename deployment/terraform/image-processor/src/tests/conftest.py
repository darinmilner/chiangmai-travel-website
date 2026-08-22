"""
Test configuration with fake layer
"""
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Get the absolute path to the tests directory
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)  # src directory

# Add paths BEFORE any imports
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(TESTS_DIR, "fake_layer"))


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for tests"""
    with patch.dict(os.environ, {
        'AWS_REGION': 'ap-southeast-7',
        'AWS_ACCOUNT_ID': '123456789012',
        'S3_BUCKET': 'test-bucket',
        'S3_PREFIX': 'villa/',
        'CLOUDFRONT_URL': 'https://test.cloudfront.net',
        'THUMBNAIL_SIZE': '300,200',
        'MEDIUM_SIZE': '800,600',
        'CAROUSEL_SIZE': '1200,800',
        'QUALITY': '85',
        'LOG_LEVEL': 'DEBUG',
        'ENVIRONMENT': 'test',
        'MAX_IMAGE_SIZE_MB': '10'
    }):
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
