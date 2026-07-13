#!/usr/bin/env python3
"""
Quick test script for the Lambda handler
Run this locally to test the handler without deploying
"""

import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Set environment variables for testing
os.environ['SES_SOURCE_EMAIL'] = 'test@example.com'
os.environ['SES_DESTINATION_EMAIL'] = 'recipient@example.com'
os.environ['SES_REGION'] = 'ap-southeast-1'
os.environ['AWS_REGION'] = 'ap-southeast-7'

from handler import lambda_handler

def test_valid_request():
    """Test with valid request data"""
    event = {
        'body': json.dumps({
            'name': 'John Doe',
            'email': 'john@example.com',
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

def test_invalid_request():
    """Test with invalid request data"""
    event = {
        'body': json.dumps({
            'name': 'J',  # Too short
            'email': 'invalid-email',
            'subject': '',
            'message': 'short'
        }),
        'httpMethod': 'POST',
        'path': '/contact'
    }

    context = None
    response = lambda_handler(event, context)

    print(f"Status Code: {response['statusCode']}")
    print(f"Response: {json.dumps(json.loads(response['body']), indent=2)}")

if __name__ == '__main__':
    print("=" * 50)
    print("Testing Lambda Handler")
    print("=" * 50)

    print("\n📝 Testing valid request:")
    test_valid_request()

    print("\n❌ Testing invalid request:")
    test_invalid_request()