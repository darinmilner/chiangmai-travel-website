"""
Fake logger for testing
"""
import logging
import os


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger for testing"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(levelname)s - %(name)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    log_level = os.environ.get('LOG_LEVEL', 'DEBUG')
    logger.setLevel(getattr(logging, log_level.upper()))

    return logger