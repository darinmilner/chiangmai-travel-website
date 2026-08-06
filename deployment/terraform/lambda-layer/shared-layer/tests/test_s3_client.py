"""
Tests for S3 client
"""
from io import BytesIO
from unittest.mock import MagicMock

import importlib
import pytest
from python.clients.s3 import S3Client
from python.clients import s3


class TestS3Client:

    def test_init(self, mock_s3):
        importlib.reload(s3)

        client = S3Client()
        assert client.bucket == 'test-bucket'

    def test_download_file_success(self, mock_s3):
        importlib.reload(s3)
        from python.clients.s3 import S3Client

        mock_body = MagicMock()
        mock_body.read.return_value = b'test data'
        mock_s3.get_object.return_value = {'Body': mock_body}

        client = S3Client()
        result = client.download_file('test-key.jpg')

        mock_s3.get_object.assert_called_with(Bucket='test-bucket', Key='test-key.jpg')
        assert isinstance(result, BytesIO)
        assert result.getvalue() == b'test data'

    def test_download_file_error(self, mock_s3):
        importlib.reload(s3)

        mock_s3.get_object.side_effect = Exception('S3 error')

        client = S3Client()
        with pytest.raises(Exception) as exc:
            client.download_file('test-key.jpg')
        assert 'S3 error' in str(exc.value)

    def test_upload_file_success(self, mock_s3):
        importlib.reload(s3)

        content = BytesIO(b'test content')
        client = S3Client()
        client.upload_file(content, 'test-key.jpg', 'image/jpeg', {'test': 'metadata'})

        mock_s3.upload_fileobj.assert_called_once()

    def test_upload_file_error(self, mock_s3):
        importlib.reload(s3)

        mock_s3.upload_fileobj.side_effect = Exception('Upload error')

        client = S3Client()
        content = BytesIO(b'test content')
        with pytest.raises(Exception) as exc:
            client.upload_file(content, 'test-key.jpg')
        assert 'Upload error' in str(exc.value)

    def test_delete_file_success(self, mock_s3):
        importlib.reload(s3)

        client = S3Client()
        client.delete_file('test-key.jpg')

        mock_s3.delete_object.assert_called_with(Bucket='test-bucket', Key='test-key.jpg')

    def test_delete_file_error(self, mock_s3):
        importlib.reload(s3)

        mock_s3.delete_object.side_effect = Exception('Delete error')

        client = S3Client()
        with pytest.raises(Exception) as exc:
            client.delete_file('test-key.jpg')
        assert 'Delete error' in str(exc.value)

    def test_file_exists_true(self, mock_s3):
        importlib.reload(s3)

        mock_s3.head_object.return_value = {}

        client = S3Client()
        result = client.file_exists('test-key.jpg')

        assert result is True
        mock_s3.head_object.assert_called_with(Bucket='test-bucket', Key='test-key.jpg')

    def test_file_exists_false(self, mock_s3):
        importlib.reload(s3)

        mock_s3.head_object.side_effect = Exception('Not found')

        client = S3Client()
        result = client.file_exists('test-key.jpg')

        assert result is False

    def test_list_files(self, mock_s3, sample_s3_keys):
        importlib.reload(s3)

        mock_s3.list_objects_v2.return_value = {'Contents': [{'Key': k} for k in sample_s3_keys]}

        client = S3Client()
        result = client.list_files(prefix='villa/')

        mock_s3.list_objects_v2.assert_called_with(Bucket='test-bucket', Prefix='villa/', MaxKeys=100)
        assert result == sample_s3_keys

    def test_list_files_empty(self, mock_s3):
        importlib.reload(s3)

        mock_s3.list_objects_v2.return_value = {'Contents': []}

        client = S3Client()
        result = client.list_files()

        assert result == []