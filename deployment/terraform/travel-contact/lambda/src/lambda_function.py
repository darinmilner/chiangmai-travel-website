"""
SES Lambda - Sends emails
"""
import json
from typing import Dict, Any, List, Optional

# Import from shared layer
from shared.logger import get_logger
from shared.clients.ses import SESClient

logger = get_logger(__name__)


class SESProcessor:
    """SES processing logic - Lambda specific"""

    def __init__(self):
        self.ses = SESClient()

    def send_booking_confirmation(
        self,
        to: List[str],
        booking_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send booking confirmation"""
        html = self._render_booking_confirmation(booking_data)

        return self.ses.send_email(
            to=to,
            subject=f"Booking Confirmed - {booking_data.get('villa_name', 'Villa')}",
            html_body=html,
            text_body=f"Booking confirmed for {booking_data.get('villa_name', 'Villa')}"
        )

    def send_contact_response(
        self,
        to: List[str],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send contact form response"""
        html = self._render_contact_response(data)

        return self.ses.send_email(
            to=to,
            subject="Thank you for contacting us",
            html_body=html,
            text_body=f"Thank you {data.get('name', '')}"
        )

    def _render_booking_confirmation(self, data: Dict[str, Any]) -> str:
        """Render booking confirmation HTML - Lambda specific"""
        return f"""
        <h2>Booking Confirmed!</h2>
        <p>Dear {data.get('guest_name', 'Guest')},</p>
        <p>Your booking has been confirmed.</p>
        <ul>
            <li><strong>Booking ID:</strong> {data.get('booking_id', 'N/A')}</li>
            <li><strong>Villa:</strong> {data.get('villa_name', 'Villa')}</li>
            <li><strong>Check-in:</strong> {data.get('check_in', 'N/A')}</li>
            <li><strong>Check-out:</strong> {data.get('check_out', 'N/A')}</li>
        </ul>
        <p>Thank you for choosing us!</p>
        """

    def _render_contact_response(self, data: Dict[str, Any]) -> str:
        """Render contact response HTML - Lambda specific"""
        return f"""
        <h2>Thank You!</h2>
        <p>Dear {data.get('name', 'Guest')},</p>
        <p>We have received your message and will respond within 24 hours.</p>
        """


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler"""
    logger.info(f"Event: {json.dumps(event)}")

    processor = SESProcessor()

    # Handle direct invocation
    if 'to' in event:
        result = processor.send_booking_confirmation(
            to=event.get('to', []),
            booking_data=event.get('booking_data', {})
        )
        return {
            'statusCode': 200 if result.get('success') else 400,
            'body': json.dumps(result)
        }

    # Handle SQS events
    results = []
    for record in event.get('Records', []):
        body = json.loads(record.get('body', '{}'))
        result = processor.send_booking_confirmation(
            to=body.get('to', []),
            booking_data=body.get('booking_data', {})
        )
        results.append(result)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Emails processed',
            'results': results
        })
    }