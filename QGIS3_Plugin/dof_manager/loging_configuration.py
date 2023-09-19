"""Logging configuration"""
import logging
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter
import os


def configure_logging(
        log_dir: str = "logs",
        log_file: str = "dof_manager.log",
        log_format: str = "%(asctime)s | %(levelname)s | %(message)s"
) -> None:
    """Configure logging.
    :param log_dir: directory with logs
    :type log_dir: str
    :param log_file: log file
    :type log_file: str
    :param log_format: logging message format
    :type log_format: str
    """
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = TimedRotatingFileHandler(
        filename=log_path,
        when='midnight',
        backupCount=7
    )

    if logger.hasHandlers():
        logger.handlers.clear()

    handler.setLevel(logging.INFO)
    formatter = Formatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
