import pytest
import json
import os
from unittest.mock import patch, MagicMock, call
import io
from PIL import Image

# Import the lambda function
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from index import lambda_handler, process_image, is_image_file, resize_image

class TestImageProcessor:
    """Test suite for image processor lambda"""

    def test_lambda_handler_success(self, mock_s3_event, mock_s3_client, mock_pil_image):
        """Test successful lambda handler execution"""
        with patch('index.process_image') as mock_process:
            result = lambda_handler(mock_s3_event, None)

            assert result['statusCode'] == 200
            assert 'successfully' in result['body']
            mock_process.assert_called_once_with('test-bucket', 'villa/test-image.jpg')

    def test_lambda_handler_no_records(self, mock_s3_client):
        """Test lambda handler with no records"""
        event = {"Records": []}
        result = lambda_handler(event, None)

        assert result['statusCode'] == 400
        assert 'No records found' in result['body']

    def test_lambda_handler_multiple_records(self, mock_multiple_events, mock_s3_client):
        """Test lambda handler with multiple records"""
        with patch('index.process_image') as mock_process:
            result = lambda_handler(mock_multiple_events, None)

            assert result['statusCode'] == 200
            assert mock_process.call_count == 2
            mock_process.assert_any_call('test-bucket', 'villa/image1.jpg')
            mock_process.assert_any_call('test-bucket', 'villa/image2.jpg')

    def test_lambda_handler_skip_processed(self, mock_s3_event, mock_s3_client):
        """Test lambda handler skips already processed images"""
        event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "test-bucket"},
                        "object": {"key": "villa/thumb_test-image.jpg"}
                    }
                }
            ]
        }

        with patch('index.process_image') as mock_process:
            result = lambda_handler(event, None)

            assert result['statusCode'] == 200
            mock_process.assert_not_called()

    def test_lambda_handler_skip_non_image(self, mock_s3_event, mock_s3_client):
        """Test lambda handler skips non-image files"""
        event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "test-bucket"},
                        "object": {"key": "villa/test-file.txt"}
                    }
                }
            ]
        }

        with patch('index.process_image') as mock_process:
            result = lambda_handler(event, None)

            assert result['statusCode'] == 200
            mock_process.assert_not_called()

    def test_lambda_handler_error(self, mock_s3_event):
        """Test lambda handler error handling"""
        with patch('index.process_image', side_effect=Exception("Test error")):
            result = lambda_handler(mock_s3_event, None)

            assert result['statusCode'] == 500
            assert 'Error' in result['body']

    @patch('index.s3_client')
    @patch('index.BytesIO')
    @patch('index.Image')
    def test_process_image_success(self, mock_image, mock_bytesio, mock_s3_client):
        """Test successful image processing"""
        # Setup mocks
        mock_img = MagicMock()
        mock_img.size = (1920, 1080)
        mock_img.mode = 'RGB'
        mock_image.open.return_value = mock_img

        mock_img_resized = MagicMock()
        mock_img_resized.size = (800, 600)
        mock_img_resized.mode = 'RGB'
        mock_img.copy.return_value = mock_img_resized

        mock_bytesio_instance = MagicMock()
        mock_bytesio.return_value = mock_bytesio_instance

        # Call function
        process_image('test-bucket', 'villa/test-image.jpg')

        # Assert S3 get_object was called
        mock_s3_client.get_object.assert_called_once_with(
            Bucket='test-bucket',
            Key='villa/test-image.jpg'
        )

        # Assert upload was called for each size
        expected_uploads = [
            'villa/thumb_test-image.jpg',
            'villa/medium_test-image.jpg',
            'villa/carousel_test-image.jpg'
        ]

        assert mock_s3_client.upload_fileobj.call_count >= 3

    @patch('index.s3_client')
    def test_process_image_error(self, mock_s3_client):
        """Test image processing error handling"""
        mock_s3_client.get_object.side_effect = Exception("S3 Error")

        with pytest.raises(Exception) as exc_info:
            process_image('test-bucket', 'villa/test-image.jpg')

        assert 'S3 Error' in str(exc_info.value)

    def test_is_image_file(self):
        """Test image file detection"""
        assert is_image_file('image.jpg') is True
        assert is_image_file('image.jpeg') is True
        assert is_image_file('image.png') is True
        assert is_image_file('image.webp') is True
        assert is_image_file('image.gif') is True
        assert is_image_file('image.txt') is False
        assert is_image_file('image.pdf') is False
        assert is_image_file('') is False

    def test_resize_image_with_height(self):
        """Test image resize with both width and height"""
        mock_img = MagicMock()
        mock_img.width = 1920
        mock_img.height = 1080

        # Create a copy mock
        mock_img_copy = MagicMock()
        mock_img_copy.width = 800
        mock_img_copy.height = 600
        mock_img.copy.return_value = mock_img_copy

        result = resize_image(mock_img, (800, 600))

        mock_img.copy.assert_called_once()
        mock_img_copy.thumbnail.assert_called_once_with((800, 600), Image.Resampling.LANCZOS)

    def test_resize_image_no_height(self):
        """Test image resize with only width specified"""
        mock_img = MagicMock()
        mock_img.width = 1920
        mock_img.height = 1080

        result = resize_image(mock_img, (800, 0))

        mock_img.resize.assert_called_once()
        # Check that aspect ratio is maintained
        call_args = mock_img.resize.call_args[0][0]
        assert call_args[0] == 800
        assert call_args[1] == 450  # 1080 * (800/1920)

    @patch('index.s3_client')
    @patch('index.BytesIO')
    @patch('index.Image')
    def test_webp_generation(self, mock_image, mock_bytesio, mock_s3_client):
        """Test WebP version generation"""
        mock_img = MagicMock()
        mock_img.mode = 'RGB'
        mock_image.open.return_value = mock_img

        mock_bytesio_instance = MagicMock()
        mock_bytesio.return_value = mock_bytesio_instance

        process_image('test-bucket', 'villa/test-image.jpg')

        # Check that WebP upload was attempted
        webp_upload_calls = [
            call for call in mock_s3_client.upload_fileobj.call_args_list
            if 'webp' in str(call)
        ]
        assert len(webp_upload_calls) >= 1

    @patch('index.logger')
    @patch('index.s3_client')
    def test_webp_generation_error(self, mock_s3_client, mock_logger):
        """Test WebP generation error handling"""
        mock_s3_client.get_object.return_value = {
            'Body': MagicMock(read=lambda: b'mock_image_data')
        }

        with patch('index.Image.open', side_effect=Exception("PIL Error")):
            with pytest.raises(Exception):
                process_image('test-bucket', 'villa/test-image.jpg')
