"""
Tests for Lambda handler
"""
from unittest.mock import patch
from lambda_function import lambda_handler


class TestLambdaHandler:
    """Test suite for lambda_handler entry point"""

    @patch('lambda_function.ImageProcessor')
    def test_lambda_handler_s3_event(self, mock_processor_cls):
        mock_processor = mock_processor_cls.return_value
        mock_processor.process_image.return_value = {'success': True, 'key': 'uploads/villa.jpg'}

        event = {
            'Records': [
                {
                    's3': {
                        'bucket': {
                            'name': 'chiangmai-villa-assets'
                        },
                        'object': {
                            'key': 'uploads/villa.jpg'
                        }
                    }
                }
            ]
        }

        response = lambda_handler(event, None)

        assert response['statusCode'] == 200
        mock_processor.process_image.assert_called_once_with('uploads/villa.jpg')
