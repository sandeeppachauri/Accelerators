# src/sdk_logger_accelerator/writer.py
from __future__ import annotations

import asyncio
import json

from .config import get_config
from .exceptions import LoggerWriteError
from .rotation import build_logger
from .schema import TraceRecord


async def write_trace(record: TraceRecord) -> None:
    """Serialize record to JSON and emit via the configured rotating file
    logger. Skipped if record.scope isn't in enabled_scopes. File I/O runs
    in a thread so it never blocks the event loop; a failure raises
    LoggerWriteError, which propagates to whoever awaited this call."""
    config = get_config()
    if record.scope not in config.enabled_scopes:
        return

    try:
        line = json.dumps(record.to_dict(), default=str)
        logger = build_logger(config)
        await asyncio.to_thread(logger.info, line)
    except OSError as exc:
        raise LoggerWriteError(f"Failed to write trace record: {exc}") from exc
