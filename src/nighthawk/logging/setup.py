"""NIGHTHAWK structured logging setup."""

import structlog
import logging
import sys
from typing import Any

from nighthawk.config.config import get_config


def configure_logging() -> None:
    """Configure structured logging for the platform."""
    cfg = get_config()

    level = cfg.log_level
    dev_mode = cfg.structlog_dev_mode

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level, logging.INFO),
    )

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if not dev_mode:
        shared_processors.extend([
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ])
    else:
        shared_processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=shared_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
        wrapper_class=structlog.BoundLogger,
    )


def get_logger(name: str = "nighthawk") -> structlog.BoundLogger:
    """Return a structured logger bound to name."""
    logger = structlog.get_logger(name)
    return logger  # type: ignore[return-value]
