"""
AWS Lambda Handler for Image Processing
"""
import urllib.parse
from logger import get_logger
from processor import ImageProcessor

logger = get_logger(__name__)


def lambda_handler(event, context):
    records = event.get('Records', [])
    logger.info(f"Received event with {len(records)} records")

    try:
        processor = ImageProcessor()

        for record in records:
            s3_data = record.get('s3', {})
            object_data = s3_data.get('object', {})
            raw_key = object_data.get('key', '')

            if not raw_key:
                continue

            # Unquote URL encoding in S3 keys (e.g. spaces converted to + or %20)
            key = urllib.parse.unquote_plus(raw_key)
            processor.process_image(key)

        return {
            'statusCode': 200,
            'body': 'Successfully processed image(s)'
        }

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Error processing image: {str(e)}"
        }
