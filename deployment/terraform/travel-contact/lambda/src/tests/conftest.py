"""
Test configuration with fake layer for SES processor
"""
import os
import sys
from unittest.mock import MagicMock, patch
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


@pytest.fixture(autouse=True)
def mock_ses_client(mocker):
    mock_client = MagicMock()
    mock_client.send_raw_email.return_value = {"MessageId": "test-message-id"}
    mocker.patch("clients.ses.boto3.client", return_value=mock_client)
    return mock_client


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for tests"""
    env_vars = {
        # AWS Dummy Credentials for Boto3
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_SECURITY_TOKEN': 'testing',
        'AWS_SESSION_TOKEN': 'testing',
        'AWS_DEFAULT_REGION': 'ap-southeast-1',
        'AWS_REGION': 'ap-southeast-1',
        'AWS_ACCOUNT_ID': '123456789012',

        # SES settings
        'SES_REGION': 'ap-southeast-1',
        'SES_FROM_EMAIL': 'test@example.com',
        'LOG_LEVEL': 'DEBUG',
        'ENVIRONMENT': 'test'
    }

    with patch.dict(os.environ, env_vars, clear=False):
        yield


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    monkeypatch.setenv("BUCKET_NAME", "test-bucket")
    monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")


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
    import json
    return {
        'Records': [
            {
                'body': json.dumps(booking_request)
            }
        ]
    }


@pytest.fixture
def sqs_event_multiple(booking_request, contact_request):
    """Sample SQS event with multiple records"""
    import json
    return {
        'Records': [
            {'body': json.dumps(booking_request)},
            {'body': json.dumps(contact_request)}
        ]
    }
