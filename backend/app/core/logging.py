"""
Structured Logging Configuration.
"""

import logging
import sys
from typing import Any
from datetime import datetime

from app.core.config import settings


class Formatter(logging.Formatter):
    """Custom formatter with colors for development."""

    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
        "RESET": "\033[0m",
    }

    def format(self, record: logging.LogRecord) -> str:
        if sys.stderr.isatty() and not settings.is_production:
            color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"

        return super().format(record)


def setup_logging() -> None:
    """Configure application logging."""
    log_format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(Formatter(log_format, datefmt=date_format))

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    root_logger.handlers = [handler]

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    return logging.getLogger(name)


class RequestLogger:
    """Context manager for request logging."""

    def __init__(self, logger: logging.Logger, request_id: str, method: str, path: str):
        self.logger = logger
        self.request_id = request_id
        self.method = method
        self.path = path
        self.start_time: float = 0

    def __enter__(self) -> "RequestLogger":
        self.start_time = datetime.utcnow().timestamp()
        self.logger.info(
            f"{self.method} {self.path} [Request: {self.request_id}] - Started"
        )
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        duration = datetime.utcnow().timestamp() - self.start_time

        if exc_type:
            self.logger.error(
                f"{self.method} {self.path} [Request: {self.request_id}] - "
                f"Failed after {duration:.3f}s - Error: {exc_val}"
            )
        else:
            self.logger.info(
                f"{self.method} {self.path} [Request: {self.request_id}] - "
                f"Completed in {duration:.3f}s"
            )
