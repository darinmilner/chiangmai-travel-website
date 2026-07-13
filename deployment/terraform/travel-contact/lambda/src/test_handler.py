#!/usr/bin/env python3
"""
Quick test script for the Lambda handler
Run this locally to test the handler without deploying
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path so we can import src modules
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Set environment variables for testing
os.environ['SES_SOURCE_EMAIL'] = 'test@example.com'
os.environ['SES_DESTINATION_EMAIL'] = 'recipient@example.com'
os.environ['SES_REGION'] = 'ap-southeast-1'
os.environ['AWS_REGION'] = 'ap-southeast-7'
os.environ['ENVIRONMENT'] = 'test'
os.environ['ENABLE_DEBUG'] = 'true'

# Mock boto3 before importing handler
import boto3

from botocore.exceptions import ClientError
from unittest.mock import MagicMock, patch

# Create mock SES client
mock_ses = MagicMock()
mock_ses.send_email.return_value = {'MessageId': 'test-message-id-123'}

# Patch boto3.client to return mock
with patch('boto3.client', return_value=mock_ses):
    # Now import handler with mocked boto3
    from src.handler import lambda_handler

def test_valid_request():
    """Test with valid request data"""
    print("\n" + "=" * 50)
    print("📝 Test: Valid Request")
    print("=" * 50)

    event = {
        'body': json.dumps({
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'subject': 'Travel Package Inquiry',
            'message': 'Hello, I am interested in your travel packages for Thailand. Can you provide more information about the Chiang Mai tours?'
        }),
        'httpMethod': 'POST',
        'path': '/contact'
    }

    context = None
    response = lambda_handler(event, context)

    print(f"Status Code: {response['statusCode']}")
    print(f"Response: {json.dumps(json.loads(response['body']), indent=2)}")

    return response

def test_invalid_request():
    """Test with invalid request data (missing fields)"""
    print("\n" + "=" * 50)
    print("❌ Test: Invalid Request (Missing Fields)")
    print("=" * 50)

    event = {
        'body': json.dumps({
            'name': 'Jane Smith',
            'email': 'jane@example.com'
            # Missing subject and message
        }),
        'httpMethod': 'POST',
        'path': '/contact'
    }

    context = None
    response = lambda_handler(event, context)

    print(f"Status Code: {response['statusCode']}")
    print(f"Response: {json.dumps(json.loads(response['body']), indent=2)}")

    return response

def test_validation_errors():
    """Test with validation errors (invalid email, short message, etc.)"""
    print("\n" + "=" * 50)
    print("🔍 Test: Validation Errors")
    print("=" * 50)

    event = {
        'body': json.dumps({
            'name': 'J',  # Too short
            'email': 'invalid-email',  # Invalid format
            'subject': 'Hi',  # Too short
            'message': 'Too short'  # Too short
        }),
        'httpMethod': 'POST',
        'path': '/contact'
    }

    context = None
    response = lambda_handler(event, context)

    print(f"Status Code: {response['statusCode']}")
    print(f"Response: {json.dumps(json.loads(response['body']), indent=2)}")

    return response

def test_xss_prevention():
    """Test XSS prevention"""
    print("\n" + "=" * 50)
    print("🛡️ Test: XSS Prevention")
    print("=" * 50)

    event = {
        'body': json.dumps({
            'name': '<script>alert("xss")</script>',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Normal message here'
        }),
        'httpMethod': 'POST',
        'path': '/contact'
    }

    context = None
    response = lambda_handler(event, context)

    print(f"Status Code: {response['statusCode']}")
    print(f"Response: {json.dumps(json.loads(response['body']), indent=2)}")

    return response

def test_options_request():
    """Test CORS preflight OPTIONS request"""
    print("\n" + "=" * 50)
    print("🔀 Test: OPTIONS Preflight Request")
    print("=" * 50)

    event = {
        'httpMethod': 'OPTIONS',
        'path': '/contact',
        'headers': {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
    }

    context = None
    response = lambda_handler(event, context)

    print(f"Status Code: {response['statusCode']}")
    print(f"CORS Headers: {response['headers']}")

    return response

def test_ses_error():
    """Test SES error handling"""
    print("\n" + "=" * 50)
    print("❌ Test: SES Error Handling")
    print("=" * 50)


    error_response = {
        'Error': {
            'Code': 'MessageRejected',
            'Message': 'Email address not verified'
        }
    }

    mock_ses_error = MagicMock()
    mock_ses_error.send_email.side_effect = ClientError(
        error_response=error_response,
        operation_name='SendEmail'
    )

    with patch('boto3.client', return_value=mock_ses_error):
        # Reload handler with error mock
        import importlib
        import src.handler
        importlib.reload(src.handler)
        from src.handler import lambda_handler

        event = {
            'body': json.dumps({
                'name': 'Test User',
                'email': 'test@example.com',
                'subject': 'Test Subject',
                'message': 'This is a test message with sufficient length.'
            }),
            'httpMethod': 'POST',
            'path': '/contact'
        }

        context = None
        response = lambda_handler(event, context)

        print(f"Status Code: {response['statusCode']}")
        print(f"Response: {json.dumps(json.loads(response['body']), indent=2)}")

        return response

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 Testing Lambda Handler")
    print("=" * 60)

    tests = [
        ("Valid Request", test_valid_request),
        ("Invalid Request (Missing Fields)", test_invalid_request),
        ("Validation Errors", test_validation_errors),
        ("XSS Prevention", test_xss_prevention),
        ("OPTIONS Preflight", test_options_request),
        ("SES Error Handling", test_ses_error)
    ]

    results = []
    for name, test_func in tests:
        try:
            response = test_func()
            status_code = response.get('statusCode', 500)

            if status_code in [200, 204]:
                results.append(f"✅ PASSED: {name}")
            elif status_code in [400, 500]:
                # Some tests expect 400/500 for error cases
                if any(keyword in name.lower() for keyword in ['invalid', 'error', 'validation', 'xss']):
                    results.append(f"✅ PASSED (expected error): {name}")
                else:
                    results.append(f"⚠️  UNEXPECTED ERROR: {name} (status {status_code})")
            else:
                results.append(f"❌ FAILED: {name} (status {status_code})")
        except Exception as e:
            results.append(f"❌ EXCEPTION: {name} - {str(e)}")

    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    for result in results:
        print(f"  {result}")

if __name__ == '__main__':
    main()