"""
Tests for image processor lambda
"""
import json
import pytest
from unittest.mock import MagicMock, patch, call
from io import BytesIO

from lambda_function import ImageProcessor, lambda_handler


class TestImageProcessor:
    """Test image processor logic"""

    def test_init(self, mock_s3_client):
        """Test processor initialization"""
        processor = ImageProcessor()
        assert processor.s3 is not None
        assert processor.thumbnail_size == (300, 200)
        assert processor.medium_size == (800, 600)
        assert processor.carousel_size == (1200, 800)
        assert processor.quality == 85

    def test_process_success(self, mock_s3_client, mock_pil_image):
        """Test successful image processing"""
        processor = ImageProcessor()
        result = processor.process('test-bucket', 'villa/test-image.jpg')

        assert result['success'] is True
        assert result['key'] == 'villa/test-image.jpg'
        assert 'variants' in result

        # Should have generated 3 variants (thumb, medium, carousel)
        variants = result['variants']
        assert len(variants) == 3
        variant_names = [v['size'] for v in variants]
        assert 'thumb' in variant_names
        assert 'medium' in variant_names
        assert 'carousel' in variant_names

    def test_process_handles_image_error(self, mock_s3_client):
        """Test processing handles image errors"""
        mock_s3_client.download_file.side_effect = Exception('Download error')

        processor = ImageProcessor()
        result = processor.process('test-bucket', 'villa/test-image.jpg')

        assert result['success'] is False
        assert 'Download error' in result['error']

    def test_generate_key(self):
        """Test key generation"""
        processor = ImageProcessor()

        key = processor._generate_key('villa/test-image.jpg', 'thumb')
        assert key == 'villa/test-image_thumb.jpg'


class TestLambdaHandler:
    """Test lambda handler"""

    def test_lambda_handler_success(self, s3_event, mock_s3_client, mock_pil_image):
        """Test successful lambda execution"""
        mock_s3_client.download_file.return_value = BytesIO(b'mock data')

        result = lambda_handler(s3_event, None)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['message'] == 'Processing complete'
        assert len(body['results']) == 1
        assert body['results'][0]['success'] is True

    def test_lambda_handler_multiple_records(self, s3_event_multiple, mock_s3_client, mock_pil_image):
        """Test processing multiple records"""
        mock_s3_client.download_file.return_value = BytesIO(b'mock data')

        result = lambda_handler(s3_event_multiple, None)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert len(body['results']) == 2

    def test_lambda_handler_skips_processed(self, mock_s3_client, mock_pil_image):
        """Test skipping already processed images"""
        event = {
            'Records': [
                {
                    's3': {
                        'bucket': {'name': 'test-bucket'},
                        'object': {'key': 'villa/test-image_thumb.jpg'}
                    }
                }
            ]
        }

        result = lambda_handler(event, None)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert len(body['results']) == 0  # No images processed

    def test_lambda_handler_error(self, s3_event, mock_s3_client):
        """Test lambda handler error"""
        mock_s3_client.download_file.side_effect = Exception('Processing error')

        result = lambda_handler(s3_event, None)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['results'][0]['success'] is False
        assert 'Processing error' in body['results'][0]['error']