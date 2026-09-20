"""
Tests for SES lambda handler using fake layer
"""
import json
from lambda_function import lambda_handler


class TestLambdaHandler:
    """Test lambda handler"""

    def test_lambda_handler_direct_invocation(self, booking_request):
        """Test direct invocation with valid booking request"""
        result = lambda_handler(booking_request, None)
        assert result['statusCode'] == 200

        body = json.loads(result['body'])
        assert body['success'] is True

    def test_lambda_handler_error(self, booking_request, mock_ses_client):
        """Test handler handling processor error"""
        mock_ses_client.set_fail_mode(True, "SES Error")
        result = lambda_handler(booking_request, None)
        assert result['statusCode'] == 500
