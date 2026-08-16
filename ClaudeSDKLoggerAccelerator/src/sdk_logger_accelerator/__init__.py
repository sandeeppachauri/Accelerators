# src/sdk_logger_accelerator/__init__.py
from __future__ import annotations

from .config import LoggerConfig, RotationConfig, configure, get_config
from .exceptions import LoggerNotConfiguredError, LoggerWriteError
from .hooks import log_event, post_tool_use_hook, pre_tool_use_hook
from .schema import SCHEMA_VERSION, Scope, TraceRecord
from .writer import write_trace

__all__ = [
    "SCHEMA_VERSION",
    "LoggerConfig",
    "LoggerNotConfiguredError",
    "LoggerWriteError",
    "RotationConfig",
    "Scope",
    "TraceRecord",
    "configure",
    "get_config",
    "log_event",
    "post_tool_use_hook",
    "pre_tool_use_hook",
    "write_trace",
]
