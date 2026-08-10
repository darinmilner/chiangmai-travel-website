"""
Tests for email templates
"""
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
        assert '$500' in html or '500' in html  # Check for price without $ sign

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

    def test_contact_response_missing_data(self):
        """Test contact response with missing data"""
        templates = EmailTemplates()
        html = templates.contact_response({})
        text = templates.contact_response_text({})

        assert 'Guest' in html  # Default
        assert 'Guest' in text