import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Use relative imports for local modules
from .config import AppConfig
from .email_service import EmailService
from .validators import ContactFormValidator

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize configuration from environment
try:
    config = AppConfig.from_env()
    logger.info(f"✅ Lambda initialized successfully")
    logger.info(f"   Lambda region: {config.aws_region}")
    logger.info(f"   SES region: {config.ses_region}")
    logger.info(f"   Source email: {config.ses_source_email}")
    logger.info(f"   Destination email: {config.ses_destination_email}")
except Exception as e:
    logger.error(f"❌ Failed to load configuration: {str(e)}")
    raise

# Initialize email service with SES
email_service = EmailService(
    region=config.ses_region,
    source_email=config.ses_source_email,
    destination_email=config.ses_destination_email
)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for processing contact form submissions

    Expected event structure (from API Gateway):
    {
        "body": "{\"name\":\"John\",\"email\":\"john@example.com\",\"subject\":\"Hello\",\"message\":\"Test\"}",
        "headers": {
            "Content-Type": "application/json"
        },
        "httpMethod": "POST",
        "path": "/contact",
        "requestContext": {
            "requestId": "abc123"
        }
    }

    Returns:
        Dict with statusCode, headers, and body
    """

    # Log incoming request
    request_id = context.aws_request_id if context else 'local-test'
    logger.info(f"📨 Processing request: {request_id}")

    # Mask sensitive data in logs
    safe_event = {k: v for k, v in event.items() if k != 'body'}
    if event.get('body'):
        try:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
            safe_body = {k: '***' if k == 'email' else v for k, v in body.items()}
            safe_event['body'] = safe_body
        except:
            safe_event['body'] = '*** masked ***'

    logger.debug(f"Event: {json.dumps(safe_event, default=str)}")

    try:
        # 1. Handle OPTIONS method (CORS preflight)
        if event.get('httpMethod') == 'OPTIONS' or event.get('routeKey') == 'OPTIONS':
            logger.info("✅ Handling OPTIONS preflight request")
            return format_response(200, {}, {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-Requested-With',
                'Access-Control-Max-Age': '300'
            })

        # 2. Parse request body
        body = parse_request_body(event)
        if body is None:
            return format_response(400, {
                'error': 'Invalid request body',
                'message': 'Request body must be valid JSON'
            })

        # 3. Validate required fields
        required_fields = ['name', 'email', 'subject', 'message']
        missing_fields = [field for field in required_fields if field not in body or not body[field]]

        if missing_fields:
            logger.warning(f"⚠️ Missing required fields: {missing_fields}")
            return format_response(400, {
                'error': 'Missing required fields',
                'missing_fields': missing_fields,
                'message': f'Required fields: {", ".join(required_fields)}'
            })

        # 4. Validate form data
        logger.info("🔍 Validating form data...")
        is_valid, errors, cleaned_data = ContactFormValidator.validate_all(body)

        if not is_valid:
            logger.warning(f"⚠️ Validation failed: {errors}")
            return format_response(400, {
                'error': 'Validation failed',
                'errors': errors,
                'message': 'Please check your input and try again'
            })

        logger.info(f"✅ Validation passed for: {cleaned_data.get('email', 'unknown')}")

        # 5. Send email via SES
        logger.info("📧 Sending email via SES...")
        result = email_service.send_email(cleaned_data)

        if result['success']:
            logger.info(f"✅ Email sent successfully. MessageId: {result['message_id']}")
            return format_response(200, {
                'success': True,
                'message': 'Your message was sent successfully!',
                'message_id': result['message_id'],
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            logger.error(f"❌ Failed to send email: {result.get('error')}")
            return format_response(500, {
                'error': 'Failed to send email',
                'details': result.get('error', 'Unknown error'),
                'message': result.get('friendly_message', 'Unable to send your message. Please try again later.')
            })

    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parsing error: {str(e)}")
        return format_response(400, {
            'error': 'Invalid JSON format',
            'message': 'The request body contains invalid JSON'
        })

    except ValueError as e:
        logger.error(f"❌ Configuration error: {str(e)}")
        return format_response(500, {
            'error': 'Server configuration error',
            'message': 'Please contact support'
        })

    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
        return format_response(500, {
            'error': 'Internal server error',
            'message': 'An unexpected error occurred. Please try again later.'
        })

def parse_request_body(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parse request body from API Gateway event

    Handles:
    - String body (API Gateway proxy integration)
    - Already parsed dict body
    - Base64 encoded body (for binary content)
    """
    body = event.get('body')

    if body is None:
        return None

    # If body is already a dict, return it
    if isinstance(body, dict):
        return body

    # If body is a string, try to parse as JSON
    if isinstance(body, str):
        # Check if body is base64 encoded
        is_base64 = event.get('isBase64Encoded', False)
        if is_base64:
            import base64
            try:
                body = base64.b64decode(body).decode('utf-8')
            except Exception as e:
                logger.warning(f"Failed to decode base64 body: {str(e)}")
                return None

        try:
            return json.loads(body)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON body: {str(e)}")
            return None

    return None

def format_response(status_code: int, body: Dict[str, Any], custom_headers: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Format API Gateway response with CORS headers

    Args:
        status_code: HTTP status code
        body: Response body as dict (will be JSON serialized)
        custom_headers: Optional additional headers
    """

    # Default headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, X-Requested-With'
    }

    # Merge custom headers
    if custom_headers:
        headers.update(custom_headers)

    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(body, default=str)
    }

# Optional: Health check endpoint
def health_check(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Health check handler for monitoring

    Can be used with API Gateway /health endpoint
    """
    return format_response(200, {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'contact-form',
        'version': '1.0.0',
        'regions': {
            'lambda': config.aws_region,
            'ses': config.ses_region
        },
        'ses_configured': bool(config.ses_source_email and config.ses_destination_email)
    })