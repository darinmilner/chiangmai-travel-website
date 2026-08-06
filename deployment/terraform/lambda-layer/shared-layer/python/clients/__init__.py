"""AWS clients package"""
from .s3 import S3Client
from .ses import SESClient

__all__ = ['S3Client', 'SESClient']