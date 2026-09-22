"""
Image processor for optimizing images for web display
"""
from io import BytesIO
from PIL import Image, ImageOps

from logger import get_logger
from s3 import S3Client

logger = get_logger(__name__)


class ImageProcessor:
    """Handles image downloading, web optimization, and re-uploading"""

    def __init__(self):
        self.s3_client = S3Client()

    def process_image(self, key: str) -> dict:
        """
        Downloads an image from S3, resizes and compresses it for web performance,
        and uploads it back to S3.
        """
        logger.info(f"Processing image: {key}")

        try:
            # 1. Download image from S3 into memory
            image_stream = self.s3_client.download_file(key)

            # 2. Open image and handle EXIF orientation
            with Image.open(image_stream) as img:
                img = ImageOps.exif_transpose(img)

                # Detect transparent PNGs vs standard JPEGs
                is_png = img.format == 'PNG' or img.mode in ('RGBA', 'P')

                if is_png and img.mode != 'RGBA':
                    img = img.convert('RGBA')
                elif not is_png:
                    img = img.convert('RGB')

                # Resize image if larger than 1920px on the longest side
                max_dimension = 1920
                if max(img.width, img.height) > max_dimension:
                    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

                # Save compressed image to buffer
                output_buffer = BytesIO()
                if is_png:
                    img.save(output_buffer, format='PNG', optimize=True)
                    content_type = 'image/png'
                else:
                    # quality=82 provides optimal web compression without noticeable visual loss
                    img.save(output_buffer, format='JPEG', quality=82, optimize=True)
                    content_type = 'image/jpeg'

                output_buffer.seek(0)

            # 3. Upload compressed image using explicit keyword arguments
            self.s3_client.upload_file(
                content=output_buffer,
                key=key,
                content_type=content_type
            )

            logger.info(f"Successfully optimized and uploaded: {key}")
            return {
                'success': True,
                'key': key
            }

        except Exception as e:
            logger.error(f"Failed to process {key}: {str(e)}")
            raise
