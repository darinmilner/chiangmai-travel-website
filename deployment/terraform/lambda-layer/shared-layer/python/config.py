"""
Shared configuration for all Lambdas
"""
import os
from dataclasses import dataclass, field


@dataclass
class Config:
    """Global configuration"""
    aws_region: str = field(default_factory=lambda: os.environ.get('AWS_REGION', 'ap-southeast-7'))
    aws_account_id: str = field(default_factory=lambda: os.environ.get('AWS_ACCOUNT_ID', ''))
    s3_bucket: str = field(default_factory=lambda: os.environ.get('S3_BUCKET', ''))
    s3_prefix: str = field(default_factory=lambda: os.environ.get('S3_PREFIX', 'villa/'))
    cloudfront_url: str = field(default_factory=lambda: os.environ.get('CLOUDFRONT_URL', ''))
    ses_region: str = field(default_factory=lambda: os.environ.get('SES_REGION', 'ap-southeast-1'))
    ses_from_email: str = field(default_factory=lambda: os.environ.get('SES_FROM_EMAIL', ''))
    log_level: str = field(default_factory=lambda: os.environ.get('LOG_LEVEL', 'INFO'))


def load_config() -> Config:
    """Load configuration from environment"""
    return Config()


config = load_config()
