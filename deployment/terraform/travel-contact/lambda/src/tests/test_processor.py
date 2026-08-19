"""
Tests for SES processor using fake layer
"""
from processor import SESProcessor


class TestSESProcessor:
    """Test SES processor logic"""

    def test_init(self):
        """Test processor initialization"""
        processor = SESProcessor()

        assert processor.from_email == 'test@example.com'
        assert processor.environment == 'test'
        assert processor.ses is not None
        assert processor.templates is not None

    def test_process_booking_confirmation(self, booking_request):
        """Test booking confirmation email"""
        processor = SESProcessor()
        result = processor.process_email_request(booking_request)

        assert result['success'] is True
        assert result['message_id'] == 'test-message-id-123'
        assert result['recipients'] == 1

        # Verify email was sent with correct content
        sent_emails = processor.ses.get_sent_emails()
        assert len(sent_emails) == 1
        email = sent_emails[0]
        assert email['to'] == ['test@example.com']
        assert 'Booking Confirmed' in email['subject']
        assert 'John Doe' in email['html_body']
        assert 'B123' in email['html_body']

    def test_process_contact_response(self, contact_request):
        """Test contact response email"""
        processor = SESProcessor()
        result = processor.process_email_request(contact_request)

        assert result['success'] is True

        sent_emails = processor.ses.get_sent_emails()
        assert len(sent_emails) == 1
        email = sent_emails[0]
        assert email['subject'] == 'Thank you for contacting us'
        assert 'John Doe' in email['html_body']
        assert 'I want to book a villa' in email['html_body']

    def test_process_generic_email(self, generic_request):
        """Test generic email"""
        processor = SESProcessor()
        result = processor.process_email_request(generic_request)

        assert result['success'] is True

        sent_emails = processor.ses.get_sent_emails()
        assert len(sent_emails) == 1
        email = sent_emails[0]
        assert email['subject'] == 'Test Subject'
        assert '<h1>Test Email</h1>' in email['html_body']

    def test_process_email_no_recipients(self):
        """Test email with no recipients"""
        processor = SESProcessor()
        request = {
            'type': 'generic',
            'to': []
        }

        result = processor.process_email_request(request)

        assert result['success'] is False
        assert 'No recipients specified' in result['error']

    def test_process_email_error(self):
        """Test email processing error"""
        processor = SESProcessor()
        processor.ses.set_fail_mode(True, 'SES error')

        request = {
            'type': 'generic',
            'to': ['test@example.com'],
            'subject': 'Test',
            'html_body': '<h1>Test</h1>'
        }

        result = processor.process_email_request(request)

        assert result['success'] is False
        assert 'SES error' in result['error']

    def test_unknown_email_type(self):
        """Test unknown email type"""
        processor = SESProcessor()
        request = {
            'type': 'unknown_type',
            'to': ['test@example.com'],
            'subject': 'Test',
            'html_body': '<h1>Test</h1>'
        }

        result = processor.process_email_request(request)

        assert result['success'] is True
        sent_emails = processor.ses.get_sent_emails()
        assert len(sent_emails) == 1
