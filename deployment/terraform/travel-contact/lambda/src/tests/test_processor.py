"""
Tests for email templates
"""
import pytest

from templates import EmailTemplates


class TestEmailTemplates:
    """Test email templates"""

    def test_booking_confirmation(self):
        """Test booking confirmation template"""
        templates = EmailTemplates()
        data = {
            'booking_id': 'B123',
            'villa_name': 'Test Villa',
            'guest_name': 'John Doe',
            'check_in': '2024-01-01',
            'check_out': '2024-01-05',
            'guests': 2,
            'total_price': 500
        }

        html = templates.booking_confirmation(data)
        text = templates.booking_confirmation_text(data)

        assert 'Booking Confirmed' in html
        assert 'John Doe' in html
        assert 'B123' in html
        assert 'Test Villa' in html
        assert '2024-01-01' in html
        assert '$500' in html

        assert 'Booking Confirmed' in text
        assert 'John Doe' in text
        assert 'B123' in text

    def test_booking_confirmation_missing_data(self):
        """Test booking confirmation with missing data"""
        templates = EmailTemplates()
        html = templates.booking_confirmation({})
        text = templates.booking_confirmation_text({})

        assert 'Guest' in html  # Default
        assert 'N/A' in html  # Default for missing fields
        assert 'Guest' in text

    def test_contact_response(self):
        """Test contact response template"""
        templates = EmailTemplates()
        data = {
            'name': 'Jane Doe',
            'message': 'Hello, I have a question'
        }

        html = templates.contact_response(data)
        text = templates.contact_response_text(data)

        assert 'Thank You for Contacting Us' in html
        assert 'Jane Doe' in html
        assert 'Hello, I have a question' in html

        assert 'Thank You for Contacting Us' in text
        assert 'Jane Doe' in text
        assert 'Hello, I have a question' in text

    def test_password_reset(self):
        """Test password reset template"""
        templates = EmailTemplates()
        data = {
            'name': 'John Doe',
            'reset_link': 'https://example.com/reset/123'
        }

        html = templates.password_reset(data)
        text = templates.password_reset_text(data)

        assert 'Password Reset' in html
        assert 'John Doe' in html
        assert 'https://example.com/reset/123' in html

        assert 'Password Reset' in text
        assert 'https://example.com/reset/123' in text

    def test_newsletter(self):
        """Test newsletter template"""
        templates = EmailTemplates()
        data = {
            'title': 'Weekly Update',
            'content': '<p>New villas available!</p>',
            'unsubscribe_link': 'https://example.com/unsubscribe'
        }

        html = templates.newsletter(data)
        text = templates.newsletter_text(data)

        assert 'Weekly Update' in html
        assert 'New villas available!' in html
        assert 'https://example.com/unsubscribe' in html

        assert 'Weekly Update' in text
        assert 'New villas available!' in text