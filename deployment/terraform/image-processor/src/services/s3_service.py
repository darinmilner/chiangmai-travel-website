"""
S3 service for the Lambda function
"""
import boto3
import os
from typing import Optional, Dict, Any, BinaryIO
from io import BytesIO

from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class S3Service:
    """Service for interacting with S3"""

    def __init__(self):
        self.client = boto3.client('s3')
        self.bucket = settings.s3_bucket

    def download_file(self, key: str) -> BytesIO:
        """
        Download a file from S3

        Args:
            key: S3 object key

        Returns:
            BytesIO: File content as bytes buffer
        """
        try:
            logger.info(f"Downloading file: {key}")
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=key
            )
            content = response['Body'].read()
            logger.info(f"Downloaded {len(content)} bytes from {key}")
            return BytesIO(content)

        except Exception as e:
            logger.error(f"Failed to download {key}: {str(e)}")
            raise

    def upload_file(
        self,
        content: BinaryIO,
        key: str,
        content_type: str = "image/jpeg",
        metadata: Optional[Dict[str, str]] = None,
        cache_control: str = "max-age=31536000"
    ) -> str:
        """
        Upload a file to S3

        Args:
            content: File content as bytes buffer
            key: S3 object key
            content_type: MIME type
            metadata: Additional metadata
            cache_control: Cache control header

        Returns:
            str: S3 object key
        """
        try:
            extra_args = {
                'ContentType': content_type,
                'CacheControl': cache_control,
                'Metadata': metadata or {}
            }

            self.client.upload_fileobj(
                content,
                self.bucket,
                key,
                ExtraArgs=extra_args
            )

            logger.info(f"Uploaded file to {key}")
            return key

        except Exception as e:
            logger.error(f"Failed to upload {key}: {str(e)}")
            raise

    def delete_file(self, key: str) -> None:
        """Delete a file from S3"""
        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=key
            )
            logger.info(f"Deleted file: {key}")
        except Exception as e:
            logger.error(f"Failed to delete {key}: {str(e)}")
            raise

    def file_exists(self, key: str) -> bool:
        """Check if a file exists in S3"""
        try:
            self.client.head_object(
                Bucket=self.bucket,
                Key=key
            )
            return True
        except Exception:
            return False

    def get_metadata(self, key: str) -> Dict[str, str]:
        """Get object metadata"""
        try:
            response = self.client.head_object(
                Bucket=self.bucket,
                Key=key
            )
            return response.get('Metadata', {})
        except Exception as e:
            logger.error(f"Failed to get metadata for {key}: {str(e)}")
            return {}