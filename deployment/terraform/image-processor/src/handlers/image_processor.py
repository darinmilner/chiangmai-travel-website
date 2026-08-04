"""
Main image processor handler
"""
import json
from typing import Dict, Any

from .s3_handler import S3EventHandler
from ..utils.logger import get_logger

logger = get_logger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler

    Args:
        event: Lambda event
        context: Lambda context

    Returns:
        Dict: Response
    """
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Create S3 event handler
        handler = S3EventHandler()

        # Process the event
        result = handler.handle_event(event)

        logger.info(f"Processing complete: {result}")
        return result

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Internal server error'
            })
        }
