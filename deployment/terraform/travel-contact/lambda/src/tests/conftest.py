"""
Test configuration with fake layer for SES processor
"""
import os
import sys
from unittest.mock import patch

import pytest

# Get the absolute path to the tests directory
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)  # lambda directory
SRC_PATH = os.path.join(PROJECT_ROOT, "src")

# Add paths BEFORE any imports
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, SRC_PATH)
sys.path.insert(0, os.path.join(TESTS_DIR, "fake_layer"))

# Now we can import from src
try:
    from lambda_function import lambda_handler
    from processor import SESProcessor
    from templates import EmailTemplates
except ImportError as e:
    print(f"Could not import from src: {e}")
    if os.path.exists(SRC_PATH):
        print(f"Files in {SRC_PATH}: {os.listdir(SRC_PATH)}")
    raise


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for tests"""
    with patch.dict(os.environ, {
        'AWS_REGION': 'ap-southeast-1',
        'AWS_ACCOUNT_ID': '123456789012',
        'SES_REGION': 'ap-southeast-1',
        'SES_FROM_EMAIL': 'test@example.com',
        'LOG_LEVEL': 'DEBUG',
        'ENVIRONMENT': 'test'
    }):
        yield


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