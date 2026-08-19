"""
Tests for configuration module
"""
import importlib
from python import config
from python.config import load_config


class TestConfig:

    def test_config_loads_from_env(self):
        importlib.reload(config)

        config_obj = load_config()
        assert config_obj.aws_region == 'ap-southeast-7'
        assert config_obj.aws_account_id == '123456789012'
        assert config_obj.s3_bucket == 'test-bucket'
        assert config_obj.ses_from_email == 'test@example.com'

    def test_config_defaults(self, monkeypatch):
        for key in ['AWS_REGION', 'S3_BUCKET', 'SES_FROM_EMAIL']:
            monkeypatch.delenv(key, raising=False)

        importlib.reload(config)

        config_obj = load_config()
        assert config_obj.aws_region == 'ap-southeast-7'
        assert config_obj.s3_bucket == ''
        assert config_obj.ses_from_email == ''

    def test_config_with_missing_optional(self, monkeypatch):
        monkeypatch.delenv('CLOUDFRONT_URL', raising=False)

        importlib.reload(config)

        config_obj = load_config()
        assert config_obj.cloudfront_url == ''
