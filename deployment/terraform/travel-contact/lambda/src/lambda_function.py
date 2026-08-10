"""
SES Processor Lambda - Handler
"""
import json
import os
from typing import Dict, Any

from python.logger import get_logger
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
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        processor = SESProcessor()
        results = []

        # Handle SQS events (if from SQS)
        if 'Records' in event:
            for record in event['Records']:
                body = json.loads(record.get('body', '{}'))
                result = processor.process_email_request(body)
                results.append(result)

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Emails processed',
                    'environment': os.environ.get('ENVIRONMENT', 'development'),
                    'results': results
                })
            }

        # Direct invocation
        else:
            result = processor.process_email_request(event)

            return {
                'statusCode': 200 if result.get('success') else 400,
                'body': json.dumps(result)
            }

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }