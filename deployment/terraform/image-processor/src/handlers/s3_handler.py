"""
S3 event handler for the Lambda function
"""
import re
import os
from typing import Dict, Any

from ..services.s3_service import S3Service
from ..services.image_service import ImageService
from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class S3EventHandler:
    """Handler for S3 events"""

    def __init__(self):
        self.s3_service = S3Service()
        self.image_service = ImageService()
        self.supported_formats = settings.supported_formats
        self.s3_prefix = settings.s3_prefix

    def handle_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle S3 event

        Args:
            event: S3 event from Lambda

        Returns:
            Dict: Processing results
        """
        records = event.get('Records', [])
        if not records:
            logger.warning('No records found in event')
            return {'statusCode': 400, 'body': 'No records found'}

        results = {
            'success': [],
            'failed': [],
            'skipped': []
        }

        for record in records:
            # Extract bucket and key
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']

            # URL decode the key
            key = self._decode_key(key)

            # Check if should process
            if self._should_skip(key):
                results['skipped'].append(key)
                logger.info(f"Skipping file: {key}")
                continue

            # Process the image
            try:
                self._process_image(bucket, key)
                results['success'].append(key)
            except Exception as e:
                logger.error(f"Failed to process {key}: {str(e)}")
                results['failed'].append({'key': key, 'error': str(e)})

        return {
            'statusCode': 200,
            'body': {
                'message': 'Processing complete',
                'results': results
            }
        }

    def _process_image(self, bucket: str, key: str) -> None:
        """
        Process a single image

        Args:
            bucket: S3 bucket name
            key: S3 object key
        """
        logger.info(f"Processing image: {key}")

        # Download image from S3
        image_data = self.s3_service.download_file(key)

        # Get filename from key
        filename = os.path.basename(key)

        # Process image
        processed = self.image_service.process_image(image_data, filename)

        # Upload processed variants
        for variant in processed['variants']:
            variant_key = variant['key']
            content_type = variant['content_type']
            buffer = variant['buffer']

            # Prepare metadata
            metadata = {
                'original_key': key,
                'original_width': str(processed['original_size'][0]),
                'original_height': str(processed['original_size'][1]),
                'variant_size': variant['size'],
                'variant_format': variant['format'],
                'processed_by': 'lambda-image-processor'
            }

            # Upload to S3
            self.s3_service.upload_file(
                buffer,
                variant_key,
                content_type=content_type,
                metadata=metadata
            )

            logger.info(f"Uploaded variant: {variant_key}")

        logger.info(f"Completed processing: {key}")

    def _should_skip(self, key: str) -> bool:
        """
        Check if file should be skipped

        Args:
            key: S3 object key

        Returns:
            bool: True if should skip
        """
        # Skip already processed images
        processed_patterns = ['thumb_', 'medium_', 'carousel_', '_thumb', '_medium', '_carousel']
        for pattern in processed_patterns:
            if pattern in key:
                return True

        # Skip non-image files
        ext = os.path.splitext(key)[1].lower()
        if ext not in self.supported_formats:
            return True

        return False

    def _decode_key(self, key: str) -> str:
        """URL decode S3 key"""
        key = re.sub(r'\+', ' ', key)
        key = re.sub(r'%([0-9A-Fa-f]{2})', lambda m: chr(int(m.group(1), 16)), key)
        return key
