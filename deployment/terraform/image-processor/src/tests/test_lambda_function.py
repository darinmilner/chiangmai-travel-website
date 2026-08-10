"""
Tests for image processor lambda handler using fake layer
"""
import json


# Import from src - path is set in conftest.py
from lambda_function import lambda_handler


class TestLambdaHandler:
    """Test lambda handler"""

    def test_lambda_handler_success(self, s3_event, mock_pil_image):
        """Test successful lambda execution"""
        result = lambda_handler(s3_event, None)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['message'] == 'Processing complete'
        assert body['success_count'] == 1
        assert body['failed_count'] == 0

    def test_lambda_handler_multiple_records(self, s3_event_multiple, mock_pil_image):
        """Test processing multiple records"""
        result = lambda_handler(s3_event_multiple, None)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success_count'] == 2
        assert body['failed_count'] == 0

    def test_lambda_handler_skips_processed(self, s3_event_thumb):
        """Test skipping already processed images"""
        result = lambda_handler(s3_event_thumb, None)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success_count'] == 0
        assert body['failed_count'] == 0

    def test_lambda_handler_with_empty_event(self):
        """Test lambda handler with empty event"""
        event = {'Records': []}
        result = lambda_handler(event, None)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['message'] == 'Processing complete'
        assert body['success_count'] == 0
        assert body['failed_count'] == 0