# src/sdk_logger_accelerator/hooks.py
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from claude_agent_sdk import HookContext, HookInput, HookJSONOutput

from .schema import Scope, TraceRecord
from .writer import write_trace

_pending_starts: dict[str, float] = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def pre_tool_use_hook(
    input_data: HookInput, tool_use_id: str | None, context: HookContext | None = None
) -> HookJSONOutput:
    """PreToolUse HookCallback (see claude_agent_sdk.types.HookCallback).
    input_data is a PreToolUseHookInput dict: session_id, tool_name,
    tool_input, tool_use_id are all read from it, not from context (context
    is currently just {"signal": None})."""
    key = tool_use_id or input_data.get("tool_use_id")
    if key is not None:
        _pending_starts[key] = time.monotonic()
    record = TraceRecord(
        scope=Scope.TOOL_CALL,
        session_id=input_data.get("session_id", "unknown-session"),
        turn_index=0,
        timestamp=_now_iso(),
        tool_name=input_data.get("tool_name"),
        tool_input=input_data.get("tool_input"),
        metadata={"tool_use_id": key, "phase": "pre"},
    )
    await write_trace(record)
    return {}


async def post_tool_use_hook(
    input_data: HookInput, tool_use_id: str | None, context: HookContext | None = None
) -> HookJSONOutput:
    """PostToolUse HookCallback. Pairs with the pre-hook via tool_use_id to
    compute latency_ms."""
    key = tool_use_id or input_data.get("tool_use_id")
    start = _pending_starts.pop(key, None) if key is not None else None
    latency_ms = (time.monotonic() - start) * 1000 if start is not None else None
    record = TraceRecord(
        scope=Scope.TOOL_CALL,
        session_id=input_data.get("session_id", "unknown-session"),
        turn_index=0,
        timestamp=_now_iso(),
        tool_name=input_data.get("tool_name"),
        tool_input=input_data.get("tool_input"),
        tool_result=input_data.get("tool_response"),
        latency_ms=latency_ms,
        metadata={"tool_use_id": key, "phase": "post"},
    )
    await write_trace(record)
    return {}


async def log_event(
    scope: Scope,
    session_id: str,
    turn_index: int = 0,
    **fields: Any,
) -> None:
    """General-purpose entry point for USER_INPUT, ASSISTANT_TEXT, FULL_TURN,
    ERROR, INFO, WARNING, DEBUG records from anywhere in a turn loop."""
    record = TraceRecord(
        scope=scope,
        session_id=session_id,
        turn_index=turn_index,
        timestamp=_now_iso(),
        **fields,
    )
    await write_trace(record)
