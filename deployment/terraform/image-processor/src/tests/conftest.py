"""
Test configuration for image processor lambda
"""
import pytest
from unittest.mock import MagicMock, patch
from io import BytesIO


@pytest.fixture
def mock_s3_client():
    """Mock S3 client"""
    with patch('shared.clients.s3.S3Client') as mock:
        client = MagicMock()
        client.download_file.return_value = BytesIO(b'mock image data')
        client.upload_file.return_value = 'uploaded-key'
        mock.return_value = client
        yield client


@pytest.fixture
def mock_pil_image():
    """Mock PIL Image"""
    with patch('PIL.Image.open') as mock_open:
        mock_img = MagicMock()
        mock_img.width = 1920
        mock_img.height = 1080
        mock_img.mode = 'RGB'
        mock_img.copy.return_value = mock_img

        # Mock resize
        mock_resized = MagicMock()
        mock_resized.width = 800
        mock_resized.height = 600
        mock_resized.mode = 'RGB'
        mock_img.resize.return_value = mock_resized

        # Mock thumbnail
        mock_img.thumbnail = MagicMock()
        mock_img_copy = MagicMock()
        mock_img_copy.width = 300
        mock_img_copy.height = 200
        mock_img.copy.return_value = mock_img_copy

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