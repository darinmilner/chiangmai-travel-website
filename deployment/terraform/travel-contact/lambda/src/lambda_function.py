"""
Image Processor Lambda - Handler
"""
import json
import os
from typing import Dict, Any

from python.logger import get_logger
from processor import ImageProcessor

logger = get_logger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for image processing

    Environment variables from Terraform:
    - S3_BUCKET: S3 bucket name
    - S3_PREFIX: S3 prefix for images
    - CLOUDFRONT_URL: CloudFront distribution URL
    - THUMBNAIL_SIZE: Thumbnail dimensions (width,height)
    - MEDIUM_SIZE: Medium image dimensions (width,height)
    - CAROUSEL_SIZE: Carousel image dimensions (width,height)
    - QUALITY: JPEG quality (1-100)
    - LOG_LEVEL: Logging level
    - ENVIRONMENT: Environment name
    """
    logger.info(f"Received event with {len(event.get('Records', []))} records")

    try:
        # Initialize processor with environment variables
        processor = ImageProcessor()
        results = []

        for record in event.get('Records', []):
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']

            # Skip already processed images
            if any(x in key for x in ['_thumb', '_medium', '_carousel']):
                logger.info(f"Skipping already processed: {key}")
                continue

            # Process the image
            result = processor.process_image(bucket, key)
            results.append(result)

        success_count = sum(1 for r in results if r.get('success'))
        failed_count = len(results) - success_count

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Processing complete',
                'environment': os.environ.get('ENVIRONMENT', 'development'),
                'success_count': success_count,
                'failed_count': failed_count,
                'results': results
            })
        }

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }