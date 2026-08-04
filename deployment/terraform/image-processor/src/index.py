"""
Lambda entry point
"""
from .handlers.image_processor import lambda_handler

# Export handler for Lambda
__all__ = ['lambda_handler']