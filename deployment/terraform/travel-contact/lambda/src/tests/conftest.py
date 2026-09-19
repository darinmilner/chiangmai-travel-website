"""
Test configuration with fake layer for SES processor
"""
import json
import os
import sys
import pytest

# Get the absolute path to the tests directory
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)  # lambda directory
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
FAKE_LAYER_DIR = os.path.join(TESTS_DIR, "fake_layer")

# CRITICAL: Insert fake_layer at position 0 to override real shared-layer imports
if FAKE_LAYER_DIR not in sys.path:
    sys.path.insert(0, FAKE_LAYER_DIR)
if SRC_PATH not in sys.path:
    sys.path.insert(1, SRC_PATH)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(2, PROJECT_ROOT)


class MockSESClient:
    def __init__(self):
        self.sent_emails = []
        self.should_fail = False
        self.error_message = "SES Error"

    def set_fail_mode(self, fail: bool, message: str = "SES Error"):
        self.should_fail = fail
        self.error_message = message

    def send_email(self, to_addresses, subject, html_body, text_body=None):
        if self.should_fail:
            raise Exception(self.error_message)

        email_data = {
            'to': to_addresses,
            'subject': subject,
            'html_body': html_body,
            'text_body': text_body,
            'message_id': 'test-message-id-123'
        }
        self.sent_emails.append(email_data)
        return 'test-message-id-123'

    def get_sent_emails(self):
        return self.sent_emails


@pytest.fixture(autouse=True)
def mock_ses_client(mocker):
    """Auto-patch SESClient everywhere so SESProcessor uses the mock instance."""
    mock_client = MockSESClient()
    mocker.patch('processor.SESClient', return_value=mock_client, create=True)
    mocker.patch('clients.ses.SESClient', return_value=mock_client, create=True)
    mocker.patch('lambda_function.SESClient', return_value=mock_client, create=True)
    return mock_client


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    """Unified environment variable setup for all tests"""
    env_vars = {
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_SECURITY_TOKEN': 'testing',
        'AWS_SESSION_TOKEN': 'testing',
        'AWS_DEFAULT_REGION': 'ap-southeast-1',
        'AWS_REGION': 'ap-southeast-1',
        'AWS_ACCOUNT_ID': '123456789012',
        'SES_REGION': 'ap-southeast-1',
        'SES_FROM_EMAIL': 'test@example.com',
        'LOG_LEVEL': 'DEBUG',
        'ENVIRONMENT': 'test',
        'BUCKET_NAME': 'test-bucket',
        'S3_BUCKET': 'test-bucket'
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def booking_request():
    """Sample booking confirmation request"""
    return {
        'type': 'booking_confirmation',
        'to': ['test@example.com'],
        'data': {
            'booking_id': 'B123',
            'villa_name': 'Test Villa',
            'guest_name': 'John Doe',
            'check_in': '2024-01-01',
            'check_out': '2024-01-05',
            'guests': 2,
            'total_price': 500
        }
    }


@pytest.fixture
def contact_request():
    """Sample contact response request"""
    return {
        'type': 'contact_response',
        'to': ['test@example.com'],
        'data': {
            'name': 'John Doe',
            'message': 'I want to book a villa'
        }
    }


@pytest.fixture
def generic_request():
    """Sample generic email request"""
    return {
        'to': ['test@example.com'],
        'subject': 'Test Subject',
        'html_body': '<h1>Test Email</h1>',
        'text_body': 'Test email body'
    }


@pytest.fixture
def sqs_event(booking_request):
    """Sample SQS event"""
    return {
        'Records': [
            {'body': json.dumps(booking_request)}
        ]
    }


@pytest.fixture
def sqs_event_multiple(booking_request, contact_request):
    """Sample SQS event with multiple records"""
    return {
        'Records': [
            {'body': json.dumps(booking_request)},
            {'body': json.dumps(contact_request)}
        ]
    }
