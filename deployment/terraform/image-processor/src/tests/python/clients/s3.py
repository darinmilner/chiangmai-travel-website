"""
Fake S3 client for testing
"""
from io import BytesIO
from typing import Dict, BinaryIO, List, Optional


class S3Client:
    """Fake S3 client for testing"""

    def __init__(self):
        self.bucket = 'test-bucket'
        self._files = {}
        self._should_fail = False
        self._fail_message = None

    def download_file(self, key: str) -> BytesIO:
        """Mock download file"""
        if self._should_fail:
            raise Exception(self._fail_message or 'Download error')

        # Return mock image data
        return BytesIO(b'mock image data')

    def upload_file(
        self,
        content: BinaryIO,
        key: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
        cache_control: str = "max-age=31536000"
    ) -> str:
        """Mock upload file"""
        if self._should_fail:
            raise Exception(self._fail_message or 'Upload error')

        self._files[key] = content.read()
        return key

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