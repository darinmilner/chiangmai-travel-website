import os
from typing import Dict, Any, List

from clients.ses import SESClient
from logger import get_logger
from templates import EmailTemplates

logger = get_logger(__name__)


class SESProcessor:
    """Handles SES email processing"""

    def __init__(self):
        self.ses = SESClient()
        self.templates = EmailTemplates()
        self.from_email = os.environ.get('SES_FROM_EMAIL', '')
        self.recipient_email = os.environ.get('CONTACT_RECIPIENT_EMAIL', self.from_email)
        self.environment = os.environ.get('ENVIRONMENT', 'development')

    def process_email_request(self, request: dict) -> dict:
        """
        Process an email request

        Args:
            request: Email request data

        Returns:
            Dict with processing results
        """
        try:
            # Check for 'to' field. Fallback to env var only if key is not present (None)
            to = request.get('to')
            if to is None and self.recipient_email:
                to = [self.recipient_email] if isinstance(self.recipient_email, str) else self.recipient_email

            if not to:
                return {
                    'success': False,
                    'error': 'No recipients specified'
                }

            if isinstance(to, str):
                to = [to]

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

    def _send_booking_confirmation(self, to: list, request: dict) -> dict:
        """Send booking confirmation email"""
        subject = request.get('subject', 'Booking Confirmed!')
        html_body = self.templates.booking_confirmation(request)
        text_body = self.templates.booking_confirmation_text(request)

        res = self.ses.send_email(
            to=to,
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )
        if isinstance(res, dict):
            return res
        return {
            'success': True,
            'message_id': res if isinstance(res, str) else f"Booking confirmation sent to {to}",
            'recipients': len(to) if isinstance(to, list) else 1
        }

    def _send_contact_response(
        self,
        to: List[str],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send contact form response email"""
        subject = data.get('subject', 'Thank you for contacting us')
        html_body = self.templates.contact_response(data)
        text_body = self.templates.contact_response_text(data)

        res = self.ses.send_email(
            to=to,
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )
        if isinstance(res, dict):
            return res
        return {'success': True, 'message_id': res}

    def _send_generic_email(
        self,
        to: List[str],
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send generic email"""
        subject = request.get('subject', '')
        html_body = request.get('html_body', '')
        text_body = request.get('text_body', '')

        res = self.ses.send_email(
            to=to,
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )
        if isinstance(res, dict):
            return res
        return {'success': True, 'message_id': res}

    def process_contact(self, payload: dict) -> dict:
        """Alias for backward compatibility"""
        return self.process_email_request(payload)


# Backward compatibility alias
ContactProcessor = SESProcessor
