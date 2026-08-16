# src/sdk_logger_accelerator/rotation.py
from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from .config import LoggerConfig

_LOGGER_NAME = "sdk_logger_accelerator.trace"


def build_logger(config: LoggerConfig) -> logging.Logger:
    """Build (or return cached) stdlib logger backed by the rotation
    strategy in config. One JSON line per emitted record."""
    logger = logging.getLogger(_LOGGER_NAME)
    if logger.handlers:
        return logger

    os.makedirs(config.log_dir, exist_ok=True)
    path = os.path.join(config.log_dir, config.filename_pattern)

    if config.rotation.strategy == "size":
        handler = RotatingFileHandler(
            path,
            maxBytes=config.rotation.max_bytes,
            backupCount=config.rotation.backup_count,
            encoding="utf-8",
        )
    elif config.rotation.strategy == "interval":
        handler = TimedRotatingFileHandler(
            path,
            when=config.rotation.when,
            interval=config.rotation.interval,
            backupCount=config.rotation.backup_count,
            encoding="utf-8",
        )
    else:
        raise ValueError(f"Unknown rotation strategy: {config.rotation.strategy!r}")

    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    return logger


def reset_logger() -> None:
    """Test-only helper: drop cached handlers so build_logger() rebuilds."""
    logger = logging.getLogger(_LOGGER_NAME)
    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)
