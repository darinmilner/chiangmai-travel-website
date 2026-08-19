"""
Tests for SES lambda handler using fake layer
"""
import json
from unittest.mock import patch

from lambda_function import lambda_handler


class TestLambdaHandler:
    """Test lambda handler"""

    def test_lambda_handler_direct_invocation(self, booking_request):
        """Test direct invocation"""
        result = lambda_handler(booking_request, None)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['message_id'] == 'test-message-id-123'

    def test_lambda_handler_sqs_event(self, sqs_event):
        """Test SQS event processing"""
        result = lambda_handler(sqs_event, None)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['message'] == 'Emails processed'
        assert len(body['results']) == 1
        assert body['results'][0]['success'] is True

    def test_lambda_handler_sqs_multiple(self, sqs_event_multiple):
        """Test SQS event with multiple records"""
        result = lambda_handler(sqs_event_multiple, None)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['message'] == 'Emails processed'
        assert len(body['results']) == 2
        assert body['results'][0]['success'] is True
        assert body['results'][1]['success'] is True

    def test_lambda_handler_error(self, booking_request):
        """Test lambda handler error"""
        # We need to patch the SES client to fail
        with patch('processor.SESClient') as MockSESClient:
            mock_ses = MockSESClient.return_value
            mock_ses.send_email.return_value = {
                'success': False,
                'error': 'SES error'
            }

            result = lambda_handler(booking_request, None)

            assert result['statusCode'] == 400
            body = json.loads(result['body'])
            assert body['success'] is False
            assert 'SES error' in body['error']

    def test_lambda_handler_missing_to(self):
        """Test lambda handler with missing 'to' field"""
        event = {
            'type': 'booking_confirmation',
            'data': {'villa_name': 'Test Villa'}
        }

        result = lambda_handler(event, None)

        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['success'] is False
        assert 'error' in body

    def test_lambda_handler_empty_sqs_records(self):
        """Test lambda handler with empty SQS records"""
        event = {'Records': []}

        result = lambda_handler(event, None)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert len(body['results']) == 0
