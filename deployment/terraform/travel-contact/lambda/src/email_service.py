import boto3
from typing import Dict, Any
from botocore.exceptions import ClientError
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class EmailService:
    """Handle email sending via SES in Singapore region"""

    def __init__(self, region: str, source_email: str, destination_email: str):
        """
        Initialize email service with SES client

        Args:
            region: AWS region for SES (Singapore)
            source_email: Verified sender email
            destination_email: Recipient email for contact forms
        """
        self.ses_client = boto3.client('ses', region_name=region)
        self.source_email = source_email
        self.destination_email = destination_email

        logger.info(f"EmailService initialized with SES in region: {region}")

    def get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    def format_email_body(self, name: str, email: str, subject: str, message: str) -> str:
        """Create HTML email template"""
        # Escape special characters for HTML safety
        import html
        name = html.escape(name)
        email = html.escape(email)
        subject = html.escape(subject)
        message = html.escape(message)

        # Convert newlines to <br> tags
        message_html = message.replace('\n', '<br>')

        # Get current timestamp
        timestamp = self.get_timestamp()

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    padding: 0;
                    background-color: #ffffff;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 30px 20px;
                    border-radius: 8px 8px 0 0;
                    color: white;
                }}
                .header h2 {{
                    margin: 0;
                    font-weight: 400;
                    font-size: 24px;
                }}
                .content {{
                    padding: 30px 25px;
                }}
                .field {{
                    margin: 20px 0;
                    padding: 15px;
                    background-color: #f8f9fa;
                    border-radius: 6px;
                    border-left: 4px solid #667eea;
                }}
                .field-label {{
                    font-weight: 600;
                    color: #555;
                    font-size: 12px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-bottom: 4px;
                }}
                .field-value {{
                    font-size: 16px;
                    color: #333;
                    word-wrap: break-word;
                }}
                .message-content {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 6px;
                    margin-top: 10px;
                    white-space: pre-wrap;
                    font-family: 'Courier New', Courier, monospace;
                    font-size: 14px;
                    line-height: 1.5;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #999;
                    font-size: 12px;
                    border-top: 1px solid #eee;
                }}
                .badge {{
                    display: inline-block;
                    background: #28a745;
                    color: white;
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 11px;
                    margin-left: 8px;
                }}
                .reply-note {{
                    background: #fff3cd;
                    padding: 12px 15px;
                    border-radius: 6px;
                    margin-top: 20px;
                    font-size: 14px;
                    border-left: 4px solid #ffc107;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>📧 New Contact Form Submission</h2>
                    <p style="margin: 5px 0 0; opacity: 0.9;">Travel Website Inquiry</p>
                </div>

                <div class="content">
                    <div class="field">
                        <div class="field-label">👤 From</div>
                        <div class="field-value">
                            <strong>{name}</strong>
                            <span class="badge">Verified</span>
                            <br>
                            <a href="mailto:{email}" style="color: #667eea;">{email}</a>
                        </div>
                    </div>

                    <div class="field">
                        <div class="field-label">📌 Subject</div>
                        <div class="field-value">{subject}</div>
                    </div>

                    <div class="field">
                        <div class="field-label">💬 Message</div>
                        <div class="message-content">{message_html}</div>
                    </div>

                    <div class="reply-note">
                        <strong>💡 Reply Note:</strong> To reply to this message, simply reply to this email.
                        The sender's email address is <a href="mailto:{email}">{email}</a>.
                    </div>
                </div>

                <div class="footer">
                    <p>
                        This email was sent from your travel website contact form.<br>
                        <span style="color: #ccc;">Powered by AWS SES</span>
                    </p>
                    <p style="font-size: 11px; color: #ccc;">
                        Received: {timestamp}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

    def format_plain_body(self, name: str, email: str, subject: str, message: str) -> str:
        """Create plain text email body"""
        timestamp = self.get_timestamp()

        return f"""
NEW CONTACT FORM SUBMISSION
===========================

From: {name} <{email}>
Subject: {subject}
Received: {timestamp}

Message:
----------
{message}
----------

To reply, send email to: {email}
"""

    def send_email(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send email using SES in Singapore region

        Args:
            form_data: Cleaned form data with 'name', 'email', 'subject', 'message'

        Returns:
            Dict with success status, message_id, and any errors
        """
        try:
            # Build email content
            html_body = self.format_email_body(
                form_data['name'],
                form_data['email'],
                form_data['subject'],
                form_data['message']
            )

            plain_body = self.format_plain_body(
                form_data['name'],
                form_data['email'],
                form_data['subject'],
                form_data['message']
            )

            # Send email via SES
            # Note: ReplyToAddresses is at the top level, not inside Destination
            response = self.ses_client.send_email(
                Source=self.source_email,
                Destination={
                    'ToAddresses': [self.destination_email]
                },
                ReplyToAddresses=[form_data['email']],  # This is correct - top level
                Message={
                    'Subject': {
                        'Data': f"Contact Form: {form_data['subject']}",
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': plain_body,
                            'Charset': 'UTF-8'
                        },
                        'Html': {
                            'Data': html_body,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )

            message_id = response.get('MessageId', 'unknown')
            logger.info(f"✅ Email sent successfully. Message ID: {message_id}")

            return {
                'success': True,
                'message_id': message_id,
                'status': 'Email sent successfully'
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"❌ SES Error: {error_code} - {error_message}")

            # Provide user-friendly error messages
            friendly_messages = {
                'MessageRejected': 'Email was rejected. Please check the email address.',
                'MailFromDomainNotVerified': 'Sender domain is not verified in SES.',
                'InvalidParameterValue': 'Invalid email parameters. Please check your input.',
                'LimitExceeded': 'Sending limit exceeded. Please try again later.',
            }

            friendly_message = friendly_messages.get(
                error_code,
                'Failed to send email. Please try again later.'
            )

            return {
                'success': False,
                'error': error_message,
                'error_code': error_code,
                'friendly_message': friendly_message
            }

        except Exception as e:
            logger.error(f"❌ Unexpected error sending email: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNEXPECTED_ERROR',
                'friendly_message': 'An unexpected error occurred. Please try again.'
            }
