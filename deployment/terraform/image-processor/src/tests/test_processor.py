"""
Tests for image processor using fake layer
"""
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

# Import from src - path is set in conftest.py
from processor import ImageProcessor


class TestImageProcessor:
    """Test image processor logic"""

    def test_init(self):
        """Test processor initialization"""
        processor = ImageProcessor()

        assert processor.thumbnail_size == (300, 200)
        assert processor.medium_size == (800, 600)
        assert processor.carousel_size == (1200, 800)
        assert processor.quality == 85
        assert processor.cloudfront_url == 'https://test.cloudfront.net'

    def test_process_image_success(self, mock_pil_image):
        """Test successful image processing"""
        processor = ImageProcessor()
        result = processor.process_image('test-bucket', 'villa/test-image.jpg')

        assert result['success'] is True
        assert result['key'] == 'villa/test-image.jpg'
        assert 'variants' in result
        assert len(result['variants']) == 3

        variant_names = [v['size'] for v in result['variants']]
        assert 'thumb' in variant_names
        assert 'medium' in variant_names
        assert 'carousel' in variant_names

    def test_process_image_with_unsupported_format(self, mock_pil_image):
        """Test processing unsupported format"""
        with patch('PIL.Image.open') as mock_open:
            processor = ImageProcessor()
            result = processor.process_image('test-bucket', 'villa/test-image.txt')

            mock_open.assert_not_called()

            assert result['success'] is False
            assert 'Unsupported file type' in result['error']

    def test_process_image_handles_download_error(self, mock_pil_image):
        """Test handling download error"""
        processor = ImageProcessor()
        processor.s3.set_fail_mode(True, 'Download error')

        with patch('PIL.Image.open') as mock_open:
            result = processor.process_image('test-bucket', 'villa/test-image.jpg')

            mock_open.assert_not_called()

            assert result['success'] is False
            assert 'Download error' in result['error']

    def test_resize_image_with_both_dimensions(self):
        """Test resize with both width and height"""
        mock_img = MagicMock()
        mock_img.width = 1920
        mock_img.height = 1080
        mock_img.mode = 'RGB'
        mock_img_copy = MagicMock()
        mock_img_copy.width = 800
        mock_img_copy.height = 600
        mock_img.copy.return_value = mock_img_copy

        processor = ImageProcessor()
        processor._resize_image(mock_img, (800, 600))

        mock_img.copy.assert_called_once()
        mock_img_copy.thumbnail.assert_called_with((800, 600), Image.Resampling.LANCZOS)

    def test_resize_image_with_width_only(self):
        """Test resize with width only"""
        mock_img = MagicMock()
        mock_img.width = 1920
        mock_img.height = 1080
        mock_img.mode = 'RGB'
        mock_img_resized = MagicMock()
        mock_img_resized.width = 800
        mock_img_resized.height = 450
        mock_img.resize.return_value = mock_img_resized

        processor = ImageProcessor()
        processor._resize_image(mock_img, (800, 0))

        mock_img.resize.assert_called_with((800, 450), Image.Resampling.LANCZOS)

    def test_convert_to_rgb_rgba(self):
        """Test converting RGBA to RGB"""
        mock_img = MagicMock()
        mock_img.mode = 'RGBA'
        mock_img.size = (100, 100)
        mock_img.split.return_value = [MagicMock() for _ in range(4)]

        with patch('PIL.Image.new') as mock_new:
            mock_rgb = MagicMock()
            mock_new.return_value = mock_rgb

            processor = ImageProcessor()
            result = processor._convert_to_rgb(mock_img)

            mock_new.assert_called_with('RGB', (100, 100), (255, 255, 255))
            mock_rgb.paste.assert_called_with(mock_img, mask=mock_img.split.return_value[-1])
            assert result == mock_rgb

    def test_convert_to_rgb_already_rgb(self):
        """Test converting already RGB image"""
        mock_img = MagicMock()
        mock_img.mode = 'RGB'
        mock_img.test_id = 'original_mock'

        processor = ImageProcessor()
        result = processor._convert_to_rgb(mock_img)

        assert result is mock_img
        mock_img.convert.assert_not_called()

    def test_generate_key(self):
        """Test key generation"""
        processor = ImageProcessor()

        key = processor._generate_key('villa/test-image.jpg', 'thumb')
        assert key == 'villa/test-image_thumb.jpg'

    def test_build_url_with_cloudfront(self):
        """Test URL building with CloudFront"""
        processor = ImageProcessor()
        url = processor._build_url('villa/test-image.jpg')
        assert url == 'https://test.cloudfront.net/villa/test-image.jpg'

    def test_build_url_without_cloudfront(self, monkeypatch):
        """Test URL building without CloudFront"""
        monkeypatch.delenv('CLOUDFRONT_URL', raising=False)

        processor = ImageProcessor()
        url = processor._build_url('villa/test-image.jpg')
        assert url == 'https://test-bucket.s3.amazonaws.com/villa/test-image.jpg'

    def test_parse_size_valid(self):
        """Test parsing valid size string"""
        processor = ImageProcessor()
        result = processor._parse_size('800,600')
        assert result == (800, 600)

    def test_parse_size_invalid(self):
        """Test parsing invalid size string"""
        processor = ImageProcessor()
        with pytest.raises(ValueError):
            processor._parse_size('invalid')
