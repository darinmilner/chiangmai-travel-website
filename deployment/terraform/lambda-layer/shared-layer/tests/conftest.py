"""
Test configuration for shared layer
"""
import os
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for all tests"""
    with patch.dict(os.environ, {
        'AWS_REGION': 'ap-southeast-7',
        'SES_REGION': 'ap-southeast-1',
        'AWS_ACCOUNT_ID': '123456789012',
        'S3_BUCKET': 'test-bucket',
        'S3_PREFIX': 'test/',
        'CLOUDFRONT_URL': 'https://test.cloudfront.net',
        'SES_FROM_EMAIL': 'test@example.com',
        'LOG_LEVEL': 'DEBUG'
    }):
        yield


@pytest.fixture
def mock_s3():
    """Mock S3 client"""
    with patch('boto3.client') as mock_client:
        mock_s3 = MagicMock()
        mock_client.side_effect = lambda service, **kwargs: mock_s3 if service == 's3' else MagicMock()
        yield mock_s3


@pytest.fixture
def mock_ses():
    """Mock SES client"""
    with patch('boto3.client') as mock_client:
        mock_ses = MagicMock()
        mock_client.side_effect = lambda service, **kwargs: mock_ses if service == 'ses' else MagicMock()
        yield mock_ses


@pytest.fixture
def sample_s3_keys():
    """Sample S3 keys for testing"""
    return ['villa/exterior.jpg', 'villa/pool.jpg', 'villa/thumb_exterior.jpg', 'villa/medium_pool.jpg']
