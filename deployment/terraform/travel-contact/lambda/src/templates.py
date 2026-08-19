"""
Email templates for contact and booking
"""
from typing import Dict, Any


class EmailTemplates:
    """Email templates for contact and booking use cases"""

    def booking_confirmation(self, data: Dict[str, Any]) -> str:
        """Booking confirmation HTML template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1b5e20; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .booking-details {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Booking Confirmed! 🎉</h1>
                </div>
                <div class="content">
                    <p>Dear {data.get('guest_name', 'Guest')},</p>
                    <p>Your booking has been confirmed. Here are your booking details:</p>

                    <div class="booking-details">
                        <p><strong>Booking ID:</strong> {data.get('booking_id', 'N/A')}</p>
                        <p><strong>Villa:</strong> {data.get('villa_name', 'Villa')}</p>
                        <p><strong>Check-in:</strong> {data.get('check_in', 'N/A')}</p>
                        <p><strong>Check-out:</strong> {data.get('check_out', 'N/A')}</p>
                        <p><strong>Guests:</strong> {data.get('guests', 0)}</p>
                        <p><strong>Total Price:</strong> ${data.get('total_price', 0)}</p>
                    </div>

                    <p>If you have any questions, please don't hesitate to contact us.</p>
                    <p>We look forward to welcoming you!</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Villa App. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

    def booking_confirmation_text(self, data: Dict[str, Any]) -> str:
        """Booking confirmation plain text template"""
        return f"""
        Booking Confirmed!

        Dear {data.get('guest_name', 'Guest')},

        Your booking has been confirmed.

        Booking ID: {data.get('booking_id', 'N/A')}
        Villa: {data.get('villa_name', 'Villa')}
        Check-in: {data.get('check_in', 'N/A')}
        Check-out: {data.get('check_out', 'N/A')}
        Guests: {data.get('guests', 0)}
        Total Price: ${data.get('total_price', 0)}

        We look forward to welcoming you!
        """

    def contact_response(self, data: Dict[str, Any]) -> str:
        """Contact response HTML template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1b5e20; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .message {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Thank You for Contacting Us</h1>
                </div>
                <div class="content">
                    <p>Dear {data.get('name', 'Guest')},</p>
                    <p>Thank you for reaching out to us. We have received your message:</p>

                    <div class="message">
                        <p>{data.get('message', '')}</p>
                    </div>

                    <p>We will get back to you within 24 hours.</p>
                    <p>In the meantime, feel free to check out our website for more information.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Villa App. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

    def contact_response_text(self, data: Dict[str, Any]) -> str:
        """Contact response plain text template"""
        return f"""
        Thank You for Contacting Us!

        Dear {data.get('name', 'Guest')},

        We have received your message:

        {data.get('message', '')}

        We will get back to you within 24 hours.
        """
