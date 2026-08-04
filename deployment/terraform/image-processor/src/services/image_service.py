"""
Image processing service for the Lambda function
"""
import os
from io import BytesIO
from PIL import Image
from typing import Tuple, Optional, List

from ..models.image import ImageConfig, ImageSize, ImageFormat
from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ImageService:
    """Service for processing images"""

    def __init__(self, config: Optional[ImageConfig] = None):
        self.config = config or ImageConfig()

    def process_image(
        self,
        image_data: BytesIO,
        filename: str
    ) -> dict:
        """
        Process image and generate multiple sizes

        Args:
            image_data: Original image data
            filename: Original filename

        Returns:
            dict: Processing results with sizes and formats
        """
        try:
            # Open image with PIL
            img = Image.open(image_data)

            # Get original dimensions
            original_width, original_height = img.size

            logger.info(f"Processing image: {filename} ({original_width}x{original_height})")

            # Generate different sizes
            results = {
                'original_size': (original_width, original_height),
                'variants': []
            }

            # Convert RGBA to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                img = self._convert_to_rgb(img)

            # Generate variants
            size_variants = [
                (ImageSize.THUMBNAIL, self.config.thumbnail_size),
                (ImageSize.MEDIUM, self.config.medium_size),
                (ImageSize.CAROUSEL, self.config.carousel_size),
            ]

            base_name = os.path.splitext(filename)[0]

            for size_name, size_dims in size_variants:
                for format_name in self.config.formats:
                    # Resize image
                    resized_img = self._resize_image(img, size_dims)

                    # Create variant info
                    variant = {
                        'size': size_name.value,
                        'format': format_name.value,
                        'dimensions': resized_img.size,
                        'key': f"{settings.s3_prefix}{size_name.value}_{base_name}.{format_name.value}",
                        'content_type': self._get_content_type(format_name)
                    }

                    # Save to buffer
                    buffer = BytesIO()
                    self._save_image(resized_img, buffer, format_name)
                    variant['buffer'] = buffer

                    results['variants'].append(variant)

            logger.info(f"Generated {len(results['variants'])} variants for {filename}")
            return results

        except Exception as e:
            logger.error(f"Failed to process image {filename}: {str(e)}")
            raise

    def _convert_to_rgb(self, img: Image.Image) -> Image.Image:
        """Convert image to RGB mode"""
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            return background
        elif img.mode in ('LA', 'P'):
            return img.convert('RGB')
        return img

    def _resize_image(self, img: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """Resize image maintaining aspect ratio"""
        if size[1] == 0:
            # Only width specified
            width = size[0]
            ratio = width / img.width
            height = int(img.height * ratio)
            return img.resize((width, height), Image.Resampling.LANCZOS)
        else:
            # Both width and height - thumbnail
            img_copy = img.copy()
            img_copy.thumbnail(size, Image.Resampling.LANCZOS)
            return img_copy

    def _save_image(self, img: Image.Image, buffer: BytesIO, format_name: ImageFormat) -> None:
        """Save image to buffer in specified format"""
        save_kwargs = {'optimize': True}

        if format_name == ImageFormat.JPEG:
            save_kwargs['quality'] = self.config.quality
            save_kwargs['format'] = 'JPEG'
        elif format_name == ImageFormat.WEBP:
            save_kwargs['quality'] = self.config.quality
            save_kwargs['format'] = 'WEBP'
        elif format_name == ImageFormat.PNG:
            save_kwargs['format'] = 'PNG'
            save_kwargs['compress_level'] = 6
        elif format_name == ImageFormat.AVIF:
            save_kwargs['quality'] = self.config.quality
            save_kwargs['format'] = 'AVIF'
        else:
            save_kwargs['format'] = format_name.value.upper()

        img.save(buffer, **save_kwargs)
        buffer.seek(0)

    def _get_content_type(self, format_name: ImageFormat) -> str:
        """Get content type for format"""
        content_types = {
            ImageFormat.JPEG: 'image/jpeg',
            ImageFormat.PNG: 'image/png',
            ImageFormat.WEBP: 'image/webp',
            ImageFormat.AVIF: 'image/avif',
            ImageFormat.GIF: 'image/gif',
        }
        return content_types.get(format_name, 'image/jpeg')

    def get_image_info(self, image_data: BytesIO) -> dict:
        """Get basic image information"""
        img = Image.open(image_data)
        return {
            'width': img.width,
            'height': img.height,
            'mode': img.mode,
            'format': img.format,
            'size': len(image_data.getvalue())
        }