"""
SES Processor Lambda - Handler
"""
import json
from typing import Dict, Any
from logger import get_logger
from processor import SESProcessor

logger = get_logger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for SES email processing

    Environment variables from Terraform:
    - SES_REGION: SES region
    - SES_FROM_EMAIL: From email address
    - LOG_LEVEL: Logging level
    - ENVIRONMENT: Environment name
    """
    logger.info(f"Received event: {json.dumps(event) if isinstance(event, dict) else event}")
    try:
        # Parse event if passed as string
        if isinstance(event, str):
            request = json.loads(event)
        else:
            request = event

        processor = SESProcessor()
        result = processor.process_email_request(request)

        if result.get('success'):
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps(result)
            }

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'error': str(e)})
        }
