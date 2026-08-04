import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_s3_event():
    """Create a mock S3 event"""
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {
                        "name": "test-bucket"
                    },
                    "object": {
                        "key": "villa/test-image.jpg"
                    }
                }
            }
        ]
    }

@pytest.fixture
def mock_multiple_events():
    """Create a mock S3 event with multiple records"""
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {
                        "name": "test-bucket"
                    },
                    "object": {
                        "key": "villa/image1.jpg"
                    }
                }
            },
            {
                "s3": {
                    "bucket": {
                        "name": "test-bucket"
                    },
                    "object": {
                        "key": "villa/image2.jpg"
                    }
                }
            }
        ]
    }

@pytest.fixture
def mock_s3_client():
    """Mock S3 client"""
    with patch('boto3.client') as mock_client:
        s3_mock = MagicMock()
        mock_client.return_value = s3_mock

        # Mock get_object response
        s3_mock.get_object.return_value = {
            'Body': MagicMock(read=lambda: b'mock_image_data')
        }

        yield s3_mock

@pytest.fixture
def mock_pil_image():
    """Mock PIL Image"""
    with patch('PIL.Image.open') as mock_open:
        mock_img = MagicMock()
        mock_img.size = (1920, 1080)
        mock_img.mode = 'RGB'

        # Mock copy and thumbnail methods
        mock_img_copy = MagicMock()
        mock_img_copy.size = (800, 600)
        mock_img_copy.mode = 'RGB'
        mock_img.copy.return_value = mock_img_copy

        mock_open.return_value = mock_img
        yield mock_img

@pytest.fixture
def mock_environment():
    """Mock environment variables"""
    with patch.dict(os.environ, {
        'THUMBNAIL_SIZE': '300,200',
        'MEDIUM_SIZE': '800,600',
        'CAROUSEL_SIZE': '1200,800',
        'QUALITY': '85',
        'LOG_LEVEL': 'DEBUG'
    }):
        yield
