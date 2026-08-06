"""
Image Processor Lambda - Processes images uploaded to S3
"""
import os
import json
from io import BytesIO
from PIL import Image
from typing import Dict, Any, List

# Import from shared layer
from shared.config import config
from shared.logger import get_logger
from shared.clients.s3 import S3Client

logger = get_logger(__name__)


class ImageProcessor:
    """Image processing logic - Lambda specific"""

    def __init__(self):
        self.s3 = S3Client()
        self.thumbnail_size = (300, 200)
        self.medium_size = (800, 600)
        self.carousel_size = (1200, 800)
        self.quality = 85

    def process(self, bucket: str, key: str) -> Dict[str, Any]:
        """Process a single image"""
        try:
            logger.info(f"Processing: {key}")

            # Download image
            image_data = self.s3.download_file(key)
            img = Image.open(image_data)

            # Generate variants
            variants = self._generate_variants(img, key)

            return {
                'success': True,
                'key': key,
                'variants': variants
            }

        except Exception as e:
            logger.error(f"Failed to process {key}: {str(e)}")
            return {'success': False, 'key': key, 'error': str(e)}

    def _generate_variants(self, img: Image.Image, key: str) -> List[Dict]:
        """Generate image variants"""
        variants = []

        # Define sizes
        sizes = [
            ('thumb', self.thumbnail_size),
            ('medium', self.medium_size),
            ('carousel', self.carousel_size),
        ]

        for name, dims in sizes:
            # Resize
            resized = self._resize_image(img, dims)

            # Convert to RGB if needed
            if resized.mode in ('RGBA', 'LA', 'P'):
                resized = self._convert_to_rgb(resized)

            # Generate JPEG
            variant_key = self._generate_key(key, name)
            buffer = BytesIO()
            resized.save(buffer, format='JPEG', quality=self.quality, optimize=True)
            buffer.seek(0)

            # Upload
            self.s3.upload_file(
                buffer,
                variant_key,
                content_type='image/jpeg',
                metadata={
                    'variant': name,
                    'processed_by': 'lambda-image-processor'
                }
            )

            variants.append({
                'key': variant_key,
                'size': name,
                'width': resized.width,
                'height': resized.height
            })

        return variants

    def _resize_image(self, img: Image.Image, size: tuple) -> Image.Image:
        """Resize maintaining aspect ratio"""
        if size[1] == 0:
            ratio = size[0] / img.width
            height = int(img.height * ratio)
            return img.resize((size[0], height), Image.Resampling.LANCZOS)
        else:
            img_copy = img.copy()
            img_copy.thumbnail(size, Image.Resampling.LANCZOS)
            return img_copy

    def _convert_to_rgb(self, img: Image.Image) -> Image.Image:
        """Convert to RGB"""
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            return background
        return img.convert('RGB')

    def _generate_key(self, original: str, variant: str) -> str:
        """Generate variant key"""
        base = os.path.splitext(original)[0]
        return f"{base}_{variant}.jpg"


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler"""
    logger.info(f"Event records: {len(event.get('Records', []))}")

    processor = ImageProcessor()
    results = []

    for record in event.get('Records', []):
        key = record['s3']['object']['key']

        # Skip already processed
        if any(x in key for x in ['_thumb', '_medium', '_carousel']):
            logger.info(f"Skipping: {key}")
            continue

        result = processor.process(
            record['s3']['bucket']['name'],
            key
        )
        results.append(result)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Processing complete',
            'results': results
        })
    }
