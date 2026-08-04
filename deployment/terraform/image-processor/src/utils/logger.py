"""
Logging configuration for the Lambda function
"""
import logging
import json
import os
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        if hasattr(record, 'extra'):
            log_data.update(record.extra)

        return json.dumps(log_data)


def setup_logger(name: str = "image_processor") -> logging.Logger:
    """Setup logger with JSON formatting"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

    # Set level from environment
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    logger.setLevel(getattr(logging, log_level.upper()))

    return logger


def get_logger(name: str = None) -> logging.Logger:
    """Get logger instance"""
    if name is None:
        name = "image_processor"
    return setup_logger(name)