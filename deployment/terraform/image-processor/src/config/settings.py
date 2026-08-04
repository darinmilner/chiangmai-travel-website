"""
Configuration settings for the Lambda function
"""
import os
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings"""
    # Image processing settings
    thumbnail_size: Tuple[int, int] = (300, 200)
    medium_size: Tuple[int, int] = (800, 600)
    carousel_size: Tuple[int, int] = (1200, 800)
    quality: int = 85

    # Supported formats
    supported_formats: List[str] = None
    output_formats: List[str] = None

    # S3 settings
    s3_bucket: str = None
    s3_prefix: str = "villa/"

    # Logging
    log_level: str = "INFO"

    # Timeouts
    processing_timeout: int = 30

    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif']
        if self.output_formats is None:
            self.output_formats = ['jpg', 'webp']

        # Load from environment
        self.s3_bucket = os.environ.get('S3_BUCKET', self.s3_bucket)
        self.log_level = os.environ.get('LOG_LEVEL', self.log_level)

        # Parse sizes from environment
        if thumb := os.environ.get('THUMBNAIL_SIZE'):
            self.thumbnail_size = tuple(map(int, thumb.split(',')))
        if medium := os.environ.get('MEDIUM_SIZE'):
            self.medium_size = tuple(map(int, medium.split(',')))
        if carousel := os.environ.get('CAROUSEL_SIZE'):
            self.carousel_size = tuple(map(int, carousel.split(',')))
        if quality := os.environ.get('QUALITY'):
            self.quality = int(quality)


# Global settings instance
settings = Settings()
