"""
Image models for the Lambda function
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum


class ImageFormat(str, Enum):
    """Supported image formats"""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    AVIF = "avif"
    GIF = "gif"


class ImageSize(str, Enum):
    """Image size variants"""
    THUMBNAIL = "thumb"
    MEDIUM = "medium"
    CAROUSEL = "carousel"
    ORIGINAL = "original"


@dataclass
class ImageConfig:
    """Image processing configuration"""
    thumbnail_size: tuple = (300, 200)
    medium_size: tuple = (800, 600)
    carousel_size: tuple = (1200, 800)
    quality: int = 85
    formats: List[ImageFormat] = None

    def __post_init__(self):
        if self.formats is None:
            self.formats = [ImageFormat.JPEG, ImageFormat.WEBP]


@dataclass
class ImageInfo:
    """Image information"""
    key: str
    bucket: str
    original_size: tuple
    processed_sizes: Dict[ImageSize, tuple]
    formats: List[ImageFormat]
    metadata: Dict[str, Any]


@dataclass
class ProcessingResult:
    """Result of image processing"""
    success: bool
    original_key: str
    processed_keys: List[str]
    errors: List[str]
    processing_time: float