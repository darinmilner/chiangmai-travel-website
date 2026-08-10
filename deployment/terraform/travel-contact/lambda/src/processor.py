"""
Image processing logic
"""
import os
from io import BytesIO
from typing import Dict, Any, List, Tuple

from PIL import Image

from python.clients.s3 import S3Client
from python.logger import get_logger

logger = get_logger(__name__)


class ImageProcessor:
    """Handles image processing operations"""

    def __init__(self):
        self.s3 = S3Client()
        print(type(self.s3))
        print(self.s3)
        # Load configuration from environment
        self.thumbnail_size = self._parse_size(os.environ.get('THUMBNAIL_SIZE', '300,200'))
        self.medium_size = self._parse_size(os.environ.get('MEDIUM_SIZE', '800,600'))
        self.carousel_size = self._parse_size(os.environ.get('CAROUSEL_SIZE', '1200,800'))
        self.quality = int(os.environ.get('QUALITY', '85'))
        self.cloudfront_url = os.environ.get('CLOUDFRONT_URL', '')

        self.supported_formats = ['.jpg', '.jpeg', '.png', '.webp', '.gif']

    def process_image(self, bucket: str, key: str) -> Dict[str, Any]:
        """
        Process a single image

        Args:
            bucket: S3 bucket name
            key: S3 object key

        Returns:
            Dict with processing results
        """
        try:
            logger.info(f"Processing image: {key}")

            # Check file extension first
            ext = os.path.splitext(key)[1].lower()
            if ext not in self.supported_formats:
                raise ValueError(f"Unsupported file type: {ext}")

            # Download image - this is where the error will be raised
            image_data = self.s3.download_file(key)
            img = Image.open(image_data)

            # Generate variants
            variants = self._generate_variants(img, key)

            return {
                'success': True,
                'key': key,
                'variants': variants,
                'original_size': f"{img.width}x{img.height}"
            }

        except Exception as e:
            logger.error(f"Failed to process {key}: {str(e)}")
            return {
                'success': False,
                'key': key,
                'error': str(e)
            }

    def _validate_image(self, img: Image.Image, key: str) -> None:
        """Validate image before processing"""
        max_size_mb = int(os.environ.get('MAX_IMAGE_SIZE_MB', '10'))
        if img.width * img.height > max_size_mb * 1024 * 1024:
            raise ValueError(f"Image too large: {img.width}x{img.height}")

    def _generate_variants(self, img: Image.Image, key: str) -> List[Dict]:
        """Generate image variants"""
        variants = []

        # Validate image
        self._validate_image(img, key)

        # Define sizes to generate
        sizes = [
            ('thumb', self.thumbnail_size),
            ('medium', self.medium_size),
            ('carousel', self.carousel_size),
        ]

        for name, dims in sizes:
            try:
                # Resize image
                resized = self._resize_image(img, dims)

                # Convert to RGB if needed
                if resized.mode in ('RGBA', 'LA', 'P'):
                    resized = self._convert_to_rgb(resized)

                # Generate JPEG
                variant_key = self._generate_key(key, name)
                buffer = BytesIO()
                resized.save(
                    buffer,
                    format='JPEG',
                    quality=self.quality,
                    optimize=True
                )
                buffer.seek(0)

                # Upload to S3
                self.s3.upload_file(
                    buffer,
                    variant_key,
                    content_type='image/jpeg',
                    metadata={
                        'original_key': key,
                        'variant': name,
                        'processed_by': 'lambda-image-processor'
                    }
                )

                # Build URL
                url = self._build_url(variant_key)

                variants.append({
                    'key': variant_key,
                    'url': url,
                    'size': name,
                    'width': resized.width,
                    'height': resized.height
                })

                logger.info(f"Generated {name} variant: {variant_key}")

            except Exception as e:
                logger.error(f"Failed to generate {name} variant: {str(e)}")
                continue

        return variants

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

    def _convert_to_rgb(self, img: Image.Image) -> Image.Image:
        """Convert image to RGB mode"""
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            return background
        return img.convert('RGB')

    def _generate_key(self, original_key: str, variant: str) -> str:
        """Generate S3 key for variant"""
        base = os.path.splitext(original_key)[0]
        return f"{base}_{variant}.jpg"

    def _build_url(self, key: str) -> str:
        """Build URL for image"""
        if self.cloudfront_url:
            return f"{self.cloudfront_url}/{key}"
        return f"https://{self.s3.bucket}.s3.amazonaws.com/{key}"

    def _parse_size(self, size_str: str) -> Tuple[int, int]:
        """Parse size string into tuple"""
        parts = size_str.split(',')
        if len(parts) != 2:
            raise ValueError(f"Invalid size format: {size_str}")
        return (int(parts[0]), int(parts[1]))