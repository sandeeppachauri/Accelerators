# src/sdk_logger_accelerator/exceptions.py
from __future__ import annotations


class LoggerWriteError(RuntimeError):
    """Raised when a trace record could not be written to disk."""


class LoggerNotConfiguredError(RuntimeError):
    """Raised when the logger is used before configure() has been called."""
