"""
SES processing logic
"""
import os
from typing import Dict, Any, List

from python.clients.ses import SESClient
from python.logger import get_logger
from templates import EmailTemplates


logger = get_logger(__name__)


class SESProcessor:
    """Handles SES email processing"""

    def __init__(self):
        self.ses = SESClient()
        self.templates = EmailTemplates()
        self.from_email = os.environ.get('SES_FROM_EMAIL', '')
        self.environment = os.environ.get('ENVIRONMENT', 'development')

    def process_email_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an email request

        Args:
            request: Email request data

        Returns:
            Dict with processing results
        """
        try:
            email_type = request.get('type', 'generic')
            to = request.get('to', [])

            if not to:
                return {
                    'success': False,
                    'error': 'No recipients specified'
                }

            logger.info(f"Processing {email_type} email for {len(to)} recipients")

            # Handle different email types
            if email_type == 'booking_confirmation':
                return self._send_booking_confirmation(to, request.get('data', {}))
            elif email_type == 'contact_response':
                return self._send_contact_response(to, request.get('data', {}))
            else:
                return self._send_generic_email(to, request)

        except Exception as e:
            logger.error(f"Failed to process email: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _send_booking_confirmation(
        self,
        to: List[str],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send booking confirmation email"""
        subject = f"Booking Confirmed - Villa #{data.get('booking_id', '')}"
        html_body = self.templates.booking_confirmation(data)
        text_body = self.templates.booking_confirmation_text(data)

        return self.ses.send_email(
            to=to,
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )

    def _send_contact_response(
        self,
        to: List[str],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send contact form response email"""
        subject = "Thank you for contacting us"
        html_body = self.templates.contact_response(data)
        text_body = self.templates.contact_response_text(data)

        return self.ses.send_email(
            to=to,
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )

    def _send_generic_email(
        self,
        to: List[str],
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send generic email"""
        subject = request.get('subject', '')
        html_body = request.get('html_body', '')
        text_body = request.get('text_body', '')

        return self.ses.send_email(
            to=to,
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )
