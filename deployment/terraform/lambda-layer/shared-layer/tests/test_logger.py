"""
Tests for logger module
"""
import importlib
import json
import logging
from python.logger import get_logger
from python.logger import JSONFormatter
from python import logger


class TestLogger:

    def test_get_logger_creates_logger(self):
        importlib.reload(logger)

        log = get_logger('test_module')
        assert log.name == 'test_module'
        assert log.level == logging.DEBUG

    def test_get_logger_reuses_existing(self):
        importlib.reload(logger)

        log1 = get_logger('test_module')
        log2 = get_logger('test_module')
        assert log1 is log2

    def test_json_formatter(self):
        importlib.reload(logger)

        formatter = JSONFormatter()
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='test.py',
            lineno=10, msg='Test message', args=(), exc_info=None
        )

        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert data['level'] == 'INFO'
        assert data['message'] == 'Test message'
        assert data['module'] == 'test'
        assert 'timestamp' in data

    def test_json_formatter_with_exception(self):
        importlib.reload(logger)

        formatter = JSONFormatter()
        try:
            raise ValueError('Test error')
        except ValueError as e:
            record = logging.LogRecord(
                name='test', level=logging.ERROR, pathname='test.py',
                lineno=10, msg='Error occurred', args=(),
                exc_info=(type(e), e, e.__traceback__)
            )

        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert data['level'] == 'ERROR'
        assert 'exception' in data
        assert 'Test error' in data['exception']

    def test_logger_level_from_env(self, monkeypatch):
        monkeypatch.setenv('LOG_LEVEL', 'ERROR')

        importlib.reload(logger)

        log = get_logger('test_module_level')
        assert log.level == logging.ERROR
