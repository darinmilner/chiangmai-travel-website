"""
Fake SES client for testing
"""
from typing import List, Dict, Any, Optional
from unittest.mock import MagicMock


class SESClient:
    """Fake SES client for testing"""

    def __init__(self):
        self.client = MagicMock()
        self.from_email = 'test@example.com'
        self._sent_emails = []
        self._should_fail = False
        self._fail_message = None

    def send_email(
        self,
        to: List[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Mock send email"""
        if self._should_fail:
            raise Exception(self._fail_message or 'SES error')

        # Store the email for verification
        email = {
            'to': to,
            'subject': subject,
            'html_body': html_body,
            'text_body': text_body,
            'cc': cc,
            'bcc': bcc
        }
        self._sent_emails.append(email)

        return {
            'success': True,
            'message_id': 'test-message-id-123',
            'recipients': len(to) + (len(cc) if cc else 0) + (len(bcc) if bcc else 0)
        }

    def get_sent_emails(self) -> List[Dict[str, Any]]:
        """Get all sent emails for verification"""
        return self._sent_emails

    def clear_sent_emails(self):
        """Clear sent emails"""
        self._sent_emails.clear()

    def set_fail_mode(self, should_fail: bool, message: str = None):
        """Set fail mode for testing errors"""
        self._should_fail = should_fail
        self._fail_message = message
