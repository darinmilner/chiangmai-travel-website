"""
Image processing logic
"""
import os
from io import BytesIO
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageOps
from clients.s3 import S3Client
from logger import get_logger

logger = get_logger(__name__)


class ImageProcessor:
    """Handles image processing operations"""

    def __init__(self):
        self.s3 = S3Client()

        self.thumbnail_size = self._parse_size(os.environ.get('THUMBNAIL_SIZE', '300,200'))
        self.medium_size = self._parse_size(os.environ.get('MEDIUM_SIZE', '800,600'))
        self.carousel_size = self._parse_size(os.environ.get('CAROUSEL_SIZE', '1200,800'))
        self.quality = int(os.environ.get('QUALITY', '85'))
        self.cloudfront_url = os.environ.get('CLOUDFRONT_URL', '')
        self.output_prefix = os.environ.get('OUTPUT_PREFIX', 'uploads/static')
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.webp', '.gif']

    def process_image(self, bucket: str, key: str) -> Dict[str, Any]:
        """Process a single image"""
        try:
            logger.info(f"Processing image: {key}")

            ext = os.path.splitext(key)[1].lower()
            if ext not in self.supported_formats:
                raise ValueError(f"Unsupported file type: {ext}")

            # Download image data
            image_data = self.s3.download_file(key)
            img = Image.open(image_data)

            # Safely transpose EXIF orientation if a valid numeric orientation tag exists
            try:
                exif = img.getexif() if hasattr(img, 'getexif') else None
                if exif and isinstance(exif.get(0x0112), int):
                    img = ImageOps.exif_transpose(img)
            except Exception as e:
                logger.warning(f"Could not parse EXIF orientation: {str(e)}")

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
        """Validate image total megapixels to avoid Lambda memory exhaustion"""
        max_megapixels = int(os.environ.get('MAX_MEGAPIXELS', '25'))
        width = getattr(img, 'width', 0)
        height = getattr(img, 'height', 0)

        if isinstance(width, int) and isinstance(height, int) and width > 0 and height > 0:
            total_pixels = width * height
            if total_pixels > (max_megapixels * 1_000_000):
                raise ValueError(
                    f"Image resolution too high: {width}x{height} "
                    f"({total_pixels / 1_000_000:.1f}MP). Max allowed: {max_megapixels}MP"
                )

    def _generate_variants(self, img: Image.Image, key: str) -> List[Dict]:
        """Generate image variants"""
        variants = []
        self._validate_image(img, key)

        sizes = [
            ('thumb', self.thumbnail_size),
            ('medium', self.medium_size),
            ('carousel', self.carousel_size),
        ]

        for name, dims in sizes:
            try:
                resized = self._resize_image(img, dims)
                resized = self._convert_to_rgb(resized)

                variant_key = self._generate_key(key, name)
                buffer = BytesIO()
                resized.save(buffer, format='JPEG', quality=self.quality, optimize=True)
                buffer.seek(0)

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

                variants.append({
                    'key': variant_key,
                    'url': self._build_url(variant_key),
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
            width = size[0]
            ratio = width / img.width
            height = int(img.height * ratio)
            return img.resize((width, height), Image.Resampling.LANCZOS)
        else:
            img_copy = img.copy()
            img_copy.thumbnail(size, Image.Resampling.LANCZOS)
            return img_copy

    def _convert_to_rgb(self, img: Image.Image) -> Image.Image:
        """Safely convert any image mode (RGBA, LA, P, CMYK) to RGB mode for JPEG saving"""
        mode = getattr(img, 'mode', 'RGB')

        if not isinstance(mode, str) or mode not in ('RGBA', 'LA', 'P', 'CMYK', '1', 'L'):
            return img

        if mode in ('RGBA', 'LA') or (mode == 'P' and 'transparency' in getattr(img, 'info', {})):
            alpha_img = img.convert('RGBA') if mode != 'RGBA' else img
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(alpha_img, mask=alpha_img.split()[-1])
            return background

        return img.convert('RGB')

    def _generate_key(self, original_key: str, variant: str) -> str:
        """
        Preserves subfolder hierarchy (villa, home, hostel) while swapping input and output prefixes.
        Example:
        original_key: 'uploads/villa/bedroom.jpg'
        Result: 'static/villa/bedroom_thumb.jpg'
        """
        input_prefix = os.environ.get('INPUT_PREFIX', 'uploads').strip('/')
        output_prefix = os.environ.get('OUTPUT_PREFIX', 'static').strip('/')

        # Strip input prefix if present
        relative_key = original_key
        if relative_key.startswith(f"{input_prefix}/"):
            relative_key = relative_key[len(f"{input_prefix}/"):]

        # Separate directory path and filename
        dirname, filename = os.path.split(relative_key)
        name_without_ext = os.path.splitext(filename)[0]

        # Reconstruct path under the output prefix
        if dirname:
            return f"{output_prefix}/{dirname}/{name_without_ext}_{variant}.jpg"
        return f"{output_prefix}/{name_without_ext}_{variant}.jpg"

    def _build_url(self, key: str) -> str:
        """Build normalized CloudFront or S3 URL"""
        if self.cloudfront_url:
            base_url = self.cloudfront_url.rstrip('/')
            if not base_url.startswith(('http://', 'https://')):
                base_url = f"https://{base_url}"
            return f"{base_url}/{key}"
        return f"https://{self.s3.bucket}.s3.amazonaws.com/{key}"

    def _parse_size(self, size_str: str) -> Tuple[int, int]:
        """Parse size string into tuple"""
        parts = size_str.split(',')
        if len(parts) != 2:
            raise ValueError(f"Invalid size format: {size_str}")
        return (int(parts[0]), int(parts[1]))
