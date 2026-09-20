"""
Fake S3 client for testing
"""
from io import BytesIO
from typing import List
from PIL import Image


class S3Client:
    """Fake S3 client for testing"""

    def __init__(self):
        self.bucket = 'test-bucket'
        self._files = {}
        self._should_fail = False
        self._fail_message = None

    def download_file(self, bucket: str, key: str = None) -> BytesIO:
        """Handle download_file(bucket, key) or download_file(key)"""
        # If called as download_file(key)
        if key is None:
            key = bucket

        if self._should_fail:
            raise Exception(self._fail_message or 'Download error')

        buffer = BytesIO()
        img = Image.new('RGB', (1000, 1000), color='white')
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        return buffer

    def upload_file(self, file_obj, bucket: str, key: str = None, **kwargs):
        """Handle upload_file(file_obj, bucket, key)"""
        if key is None:
            key = bucket

        if self._should_fail:
            raise Exception(self._fail_message or 'Upload error')

        self._files[key] = file_obj

    def delete_file(self, key: str) -> None:
        """Mock delete file"""
        if self._should_fail:
            raise Exception(self._fail_message or 'Delete error')

        if key in self._files:
            del self._files[key]

    def file_exists(self, key: str) -> bool:
        """Mock file exists"""
        return key in self._files

    def list_files(self, prefix: str = "", max_keys: int = 100) -> List[str]:
        """Mock list files"""
        return [k for k in self._files.keys() if k.startswith(prefix)]

    def set_fail_mode(self, should_fail: bool, message: str = None):
        """Set fail mode for testing errors"""
        self._should_fail = should_fail
        self._fail_message = message

    def clear_files(self):
        """Clear stored files"""
        self._files.clear()
