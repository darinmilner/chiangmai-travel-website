"""
Test configuration with fake layer for SES processor
"""
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add fake layer to path BEFORE importing any src modules
FAKE_LAYER = os.path.join(os.path.dirname(__file__), "fake_layer")
sys.path.insert(0, FAKE_LAYER)

# Add src to path
SRC_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
sys.path.insert(0, SRC_PATH)


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
def password_reset_request():
    """Sample password reset request"""
    return {
        'type': 'password_reset',
        'to': ['test@example.com'],
        'data': {
            'name': 'John Doe',
            'reset_link': 'https://example.com/reset/123'
        }
    }


@pytest.fixture
def newsletter_request():
    """Sample newsletter request"""
    return {
        'type': 'newsletter',
        'to': ['test@example.com'],
        'data': {
            'title': 'Weekly Villa Update',
            'content': '<p>Check out our new villas!</p>',
            'unsubscribe_link': 'https://example.com/unsubscribe'
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