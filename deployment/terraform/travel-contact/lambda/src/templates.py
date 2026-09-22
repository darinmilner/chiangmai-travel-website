"""
Email templates for contact and booking
"""
from typing import Dict, Any


class EmailTemplates:
    """Email templates for contact and booking use cases"""

    def booking_confirmation(self, data: Dict[str, Any]) -> str:
        """Booking confirmation HTML template"""
        data = data or {}
        guest_name = (
            data.get('guest_name')
            or data.get('customer_name')
            or data.get('name')
            or 'Guest'
        )

        booking_ref = (
            data.get('booking_reference')
            or data.get('booking_id')
            or data.get('reference')
            or 'N/A'
        )

        villa = (
            data.get('villa_name')
            or data.get('villa_id')
            or data.get('villa')
            or data.get('property_id')
            or 'N/A'
        )

        check_in = data.get('check_in', 'N/A')
        check_out = data.get('check_out', 'N/A')

        known_keys = {
            'guest_name', 'customer_name', 'name',
            'booking_reference', 'booking_id', 'reference',
            'villa_name', 'villa_id', 'villa', 'property_id',
            'check_in', 'check_out', 'type', 'to', 'subject'
        }

        details_html = (
            f"<p><strong>Booking Reference:</strong> {booking_ref}</p>\n"
            f"<p><strong>Villa:</strong> {villa}</p>\n"
            f"<p><strong>Check-in:</strong> {check_in}</p>\n"
            f"<p><strong>Check-out:</strong> {check_out}</p>\n"
        )

        # Include any additional payload key-values dynamically
        for key, value in data.items():
            if key not in known_keys:
                label = key.replace('_', ' ').title()
                details_html += f"<p><strong>{label}:</strong> {value}</p>\n"

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
                    <p>Dear {guest_name},</p>
                    <p>Your booking has been confirmed. Here are your booking details:</p>

                    <div class="booking-details">
                    {details_html}
                </div>
                    <p>If you have any questions, please don't hesitate to contact us.</p>
                    <p>We look forward to welcoming you!</p>
                </div>
                <div class="footer">
                    <p>&copy; 2026 Chiang Mai Villa. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

    def booking_confirmation_text(self, data: Dict[str, Any]) -> str:
        """Booking confirmation plain text template"""
        data = data or {}
        guest_name = (
            data.get('guest_name')
            or data.get('customer_name')
            or data.get('name')
            or 'Guest'
        )

        booking_ref = (
            data.get('booking_reference')
            or data.get('booking_id')
            or data.get('reference')
            or 'N/A'
        )

        villa = (
            data.get('villa_name')
            or data.get('villa_id')
            or data.get('villa')
            or data.get('property_id')
            or 'N/A'
        )

        check_in = data.get('check_in', 'N/A')
        check_out = data.get('check_out', 'N/A')

        known_keys = {
            'guest_name', 'customer_name', 'name',
            'booking_reference', 'booking_id', 'reference',
            'villa_name', 'villa_id', 'villa', 'property_id',
            'check_in', 'check_out', 'type', 'to', 'subject'
        }

        details_text = (
            f"Booking Reference: {booking_ref}\n"
            f"Villa: {villa}\n"
            f"Check-in: {check_in}\n"
            f"Check-out: {check_out}\n"
        )

        for key, value in data.items():
            if key not in known_keys:
                label = key.replace('_', ' ').title()
                details_text += f"        {label}: {value}\n"

        return f"""
        Booking Confirmed!

        Dear {guest_name},

        Your booking has been confirmed.

        {details_text}
        We look forward to welcoming you!
        """

    def contact_response(self, data: Dict[str, Any]) -> str:
        """Contact response HTML template"""
        data = data or {}
        name = (
            data.get('name')
            or data.get('customer_name')
            or data.get('guest_name')
            or 'Guest'
        )
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
                    <p>Dear {name},</p>
                    <p>Thank you for reaching out to us. We have received your message:</p>

                    <div class="message">
                        <p>{data.get('message', '')}</p>
                    </div>

                    <p>We will get back to you within 24 hours.</p>
                    <p>In the meantime, feel free to check out our website for more information.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2026 Chiang Mai Villa. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

    def contact_response_text(self, data: Dict[str, Any]) -> str:
        """Contact response plain text template"""
        data = data or {}
        name = (
            data.get('name')
            or data.get('customer_name')
            or data.get('guest_name')
            or 'Guest'
        )
        return f"""
        Thank You for Contacting Us!

        Dear {name},

        We have received your message:

        {data.get('message', '')}

        We will get back to you within 24 hours.
        """
