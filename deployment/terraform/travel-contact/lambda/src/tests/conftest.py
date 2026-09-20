"""
Test configuration for Travel Contact Lambda
"""
import os
import sys
import pytest


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
FAKE_LAYER_DIR = os.path.join(TESTS_DIR, "fake_layer")

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

    def send_email(self, to=None, to_addresses=None, subject=None, html_body=None, text_body=None, **kwargs):
        if self.should_fail:
            raise Exception(self.error_message)

        recipients = to or to_addresses
        email_data = {
            'to': recipients,
            'subject': subject,
            'html_body': html_body,
            'text_body': text_body,
            'message_id': 'test-message-id-123'
        }
        self.sent_emails.append(email_data)
        return 'test-message-id-123'

    def get_sent_emails(self):
        return self.sent_emails


@pytest.fixture
def mock_ses_client():
    return MockSESClient()


@pytest.fixture(autouse=True)
def mock_ses_client_patch(mocker, mock_ses_client):
    """Patch SESClient in modules that exist in travel-contact."""
    mocker.patch('processor.SESClient', return_value=mock_ses_client, create=True)
    mocker.patch('lambda_function.SESClient', return_value=mock_ses_client, create=True)
    return mock_ses_client


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    env_vars = {
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_SECURITY_TOKEN': 'testing',
        'AWS_SESSION_TOKEN': 'testing',
        'AWS_DEFAULT_REGION': 'ap-southeast-1',
        'AWS_REGION': 'ap-southeast-1',
        'SES_REGION': 'ap-southeast-1',
        'SES_FROM_EMAIL': 'test@example.com',
        'LOG_LEVEL': 'DEBUG',
        'ENVIRONMENT': 'test',
        'BUCKET_NAME': 'test-bucket',
        'S3_BUCKET_NAME': 'test-bucket',
        'S3_BUCKET': 'test-bucket'
    }
    for key, val in env_vars.items():
        monkeypatch.setenv(key, val)


@pytest.fixture
def booking_request():
    return {
        'type': 'booking_confirmation',
        'to': ['guest@example.com'],
        'booking_id': 'BK-1001',
        'customer_name': 'Fatimah Doe',
        'tour_name': 'Chiang Mai Old City Tour',
        'tour_date': '2026-10-01',
        'guests': 2,
        'total_amount': '$120'
    }


@pytest.fixture
def contact_request():
    return {
        'type': 'contact_response',
        'to': ['user@example.com'],
        'name': 'Ali Doe',
        'message': 'Inquiry regarding availability.'
    }


@pytest.fixture
def generic_request():
    return {
        'type': 'generic',
        'to': ['user@example.com'],
        'subject': 'Welcome to Chiang Mai',
        'html_body': '<h1>Welcome!</h1>'
    }
