"""
Shared SES client
"""
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, List, Optional

import boto3

from python.config import config
from python.logger import get_logger

logger = get_logger(__name__)


class SESClient:
    """SES client for sending emails"""

    def __init__(self):
        region = config.ses_region or config.aws_region
        self.client = boto3.client('ses', region_name=region)
        self.from_email = config.ses_from_email

    def send_email(
        self,
        to: List[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send email via SES"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to)

            if cc:
                msg['Cc'] = ', '.join(cc)

            if text_body:
                msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            recipients = to.copy()
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)

            response = self.client.send_raw_email(
                Source=self.from_email,
                Destinations=recipients,
                RawMessage={'Data': msg.as_string()}
            )

            logger.info(f"Email sent to {len(to)} recipients")
            return {
                'success': True,
                'message_id': response.get('MessageId', ''),
                'recipients': len(recipients)
            }

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message_id': None,
                'recipients': 0
            }