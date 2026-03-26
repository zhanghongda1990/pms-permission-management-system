import logging
import os
from datetime import datetime
from pathlib import Path
from .path_utils import PathUtils


class Logger:
    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._init_logger()
        return cls._instance

    def _init_logger(self):
        log_dir = PathUtils.get_log_dir()
        PathUtils.ensure_dir(log_dir)
        
        log_file = PathUtils.get_log_file(log_dir)
        
        self._logger = logging.getLogger('PermissionSystem')
        self._logger.setLevel(logging.DEBUG)
        
        if not self._logger.handlers:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)

    @classmethod
    def debug(cls, message):
        cls()._logger.debug(message)

    @classmethod
    def info(cls, message):
        cls()._logger.info(message)

    @classmethod
    def warning(cls, message):
        cls()._logger.warning(message)

    @classmethod
    def error(cls, message):
        cls()._logger.error(message)

    @classmethod
    def critical(cls, message):
        cls()._logger.critical(message)
