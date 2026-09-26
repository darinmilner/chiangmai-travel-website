"""
SES processing logic
"""
import os

from clients.ses import SESClient
from logger import get_logger
from templates import EmailTemplates


logger = get_logger(__name__)


class SESProcessor:
    def __init__(self):
        self.ses = SESClient()
        self.templates = EmailTemplates()
        self.from_email = os.environ.get('SES_FROM_EMAIL', '')
        # Fall back to recipient env variable or default back to from_email
        self.recipient_email = os.environ.get('CONTACT_RECIPIENT_EMAIL', self.from_email)
        self.environment = os.environ.get('ENVIRONMENT', 'development')

    def process_email_request(self, request: dict) -> dict:
        try:
            # 1. Fall back to environment variable if 'to' is missing in request
            to = request.get('to')
            if not to:
                if self.recipient_email:
                    to = [self.recipient_email] if isinstance(self.recipient_email, str) else self.recipient_email
                else:
                    return {
                        'success': False,
                        'error': 'No recipients specified in request or environment'
                    }

            # Normalize string to list
            if isinstance(to, str):
                to = [to]

            # 2. Default email_type to 'contact_response' if missing
            email_type = request.get('type', 'contact_response')

            if email_type == 'booking_confirmation':
                return self._send_booking_confirmation(to, request)
            elif email_type == 'contact_response':
                return self._send_contact_response(to, request)
            elif email_type == 'generic':
                return self._send_generic_email(to, request)
            else:
                return {
                    'success': False,
                    'error': f'Unknown email type: {email_type}'
                }

        except Exception as e:
            logger.error(f"Failed to process email: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }