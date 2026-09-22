"""
Tests for ImageProcessor
"""
from io import BytesIO
from unittest.mock import MagicMock, patch
import pytest
from PIL import Image

from processor import ImageProcessor


def create_test_image_bytes(width: int = 1000, height: int = 1000, fmt: str = 'JPEG') -> BytesIO:
    """Helper to create test image bytes"""
    buf = BytesIO()
    img = Image.new('RGB', (width, height), color='red')
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf


class TestImageProcessor:
    """Test suite for ImageProcessor"""

    @patch('processor.S3Client')
    def test_process_image_success(self, mock_s3_cls):
        mock_s3 = MagicMock()
        mock_s3_cls.return_value = mock_s3
        mock_s3.download_file.return_value = create_test_image_bytes(800, 600, 'JPEG')

        processor = ImageProcessor()
        result = processor.process_image("uploads/photo.jpg")

        assert result['success'] is True
        assert result['key'] == "uploads/photo.jpg"
        mock_s3.download_file.assert_called_once_with("uploads/photo.jpg")
        mock_s3.upload_file.assert_called_once()

    @patch('processor.S3Client')
    def test_process_image_resizes_large_images(self, mock_s3_cls):
        mock_s3 = MagicMock()
        mock_s3_cls.return_value = mock_s3
        # Image exceeding 1920px threshold
        mock_s3.download_file.return_value = create_test_image_bytes(3000, 2000, 'JPEG')

        processor = ImageProcessor()
        processor.process_image("uploads/large_photo.jpg")

        # Verify upload content was generated and resized
        mock_s3.upload_file.assert_called_once()
        _, kwargs = mock_s3.upload_file.call_args
        uploaded_bytes = kwargs['content']
        uploaded_img = Image.open(uploaded_bytes)
        assert max(uploaded_img.width, uploaded_img.height) <= 1920

    @patch('processor.S3Client')
    def test_process_image_handles_failure(self, mock_s3_cls):
        mock_s3 = MagicMock()
        mock_s3_cls.return_value = mock_s3
        mock_s3.download_file.side_effect = Exception("S3 Download Error")

        processor = ImageProcessor()
        with pytest.raises(Exception, match="S3 Download Error"):
            processor.process_image("uploads/missing.jpg")
