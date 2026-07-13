import os
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@dataclass
class AppConfig:
    """Application configuration from environment variables"""

    # Required: SES configuration (Singapore region)
    ses_source_email: str
    ses_destination_email: str
    ses_region: str

    # Required: Lambda configuration (Bangkok region)
    aws_region: str

    # Optional with defaults
    max_email_size_kb: int = 10240
    rate_limit_per_minute: int = 10
    environment: str = "production"
    enable_debug: bool = False

    @classmethod
    def from_env(cls) -> 'AppConfig':
        """
        Load configuration from environment variables

        Required environment variables:
            SES_SOURCE_EMAIL: Verified sender email in SES
            SES_DESTINATION_EMAIL: Recipient email for contact forms
            SES_REGION: AWS region for SES (e.g., ap-southeast-1)
            AWS_REGION: AWS region for Lambda (e.g., ap-southeast-7)
        """
        required_vars = [
            'SES_SOURCE_EMAIL',
            'SES_DESTINATION_EMAIL',
            'SES_REGION',
            'AWS_REGION'
        ]

        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            error_msg = f"Missing required environment variables: {', '.join(missing)}"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)

        # Validate regions
        ses_region = os.getenv('SES_REGION')
        aws_region = os.getenv('AWS_REGION')

        if ses_region == aws_region:
            logger.warning(f"⚠️ SES and Lambda are in the same region: {ses_region}")
            logger.warning("   Consider using different regions for redundancy")

        # Load config
        config = cls(
            ses_source_email=os.getenv('SES_SOURCE_EMAIL'),
            ses_destination_email=os.getenv('SES_DESTINATION_EMAIL'),
            ses_region=ses_region,
            aws_region=aws_region,
            max_email_size_kb=int(os.getenv('MAX_EMAIL_SIZE_KB', '10240')),
            rate_limit_per_minute=int(os.getenv('RATE_LIMIT_PER_MINUTE', '10')),
            environment=os.getenv('ENVIRONMENT', 'production'),
            enable_debug=os.getenv('ENABLE_DEBUG', 'false').lower() == 'true'
        )

        # Validate email addresses
        if '@' not in config.ses_source_email:
            raise ValueError(f"Invalid SES source email: {config.ses_source_email}")
        if '@' not in config.ses_destination_email:
            raise ValueError(f"Invalid SES destination email: {config.ses_destination_email}")

        logger.info("✅ Configuration loaded successfully")
        logger.info(f"   Environment: {config.environment}")
        logger.info(f"   Lambda region: {config.aws_region}")
        logger.info(f"   SES region: {config.ses_region}")
        logger.info(f"   Debug mode: {config.enable_debug}")

        return config