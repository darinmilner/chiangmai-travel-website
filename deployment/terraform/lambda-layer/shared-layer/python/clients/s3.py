"""
Shared S3 client
"""
from io import BytesIO
from typing import Dict, BinaryIO, List, Optional

import boto3

from python.config import config
from python.logger import get_logger

logger = get_logger(__name__)


class S3Client:
    """S3 client for common operations"""

    def __init__(self):
        self.client = boto3.client('s3', region_name=config.aws_region)
        self.bucket = config.s3_bucket

    def download_file(self, key: str) -> BytesIO:
        """Download file from S3"""
        try:
            logger.info(f"Downloading: {key}")
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return BytesIO(response['Body'].read())
        except Exception as e:
            logger.error(f"Failed to download {key}: {str(e)}")
            raise

    def upload_file(
        self,
        content: BinaryIO,
        key: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
        cache_control: str = "max-age=31536000"
    ) -> str:
        """Upload file to S3"""
        try:
            extra_args = {
                'ContentType': content_type,
                'CacheControl': cache_control,
                'Metadata': metadata or {}
            }
            self.client.upload_fileobj(content, self.bucket, key, ExtraArgs=extra_args)
            logger.info(f"Uploaded: {key}")
            return key
        except Exception as e:
            logger.error(f"Failed to upload {key}: {str(e)}")
            raise

    def delete_file(self, key: str) -> None:
        """Delete file from S3"""
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            logger.info(f"Deleted: {key}")
        except Exception as e:
            logger.error(f"Failed to delete {key}: {str(e)}")
            raise

    def file_exists(self, key: str) -> bool:
        """Check if file exists"""
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False

    def list_files(self, prefix: str = "", max_keys: int = 100) -> List[str]:
        """List files in bucket"""
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            return [obj['Key'] for obj in response.get('Contents', [])]
        except Exception as e:
            logger.error(f"Failed to list files: {str(e)}")
            return []
