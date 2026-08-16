# src/logger_tester/run.py
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from auth_accelerator.options import build_options
from claude_agent_sdk import HookMatcher, query

import sdk_logger_accelerator as logger
from sdk_logger_accelerator import Scope

SESSION_ID = "tester-session"


async def _drive_tool_call() -> None:
    """Covers Scope.TOOL_CALL via the real pre/post hook pair."""
    options = build_options(
        environment=os.environ.get("ENVIRONMENT", "local"),
        hooks={
            "PreToolUse": [HookMatcher(hooks=[logger.pre_tool_use_hook])],
            "PostToolUse": [HookMatcher(hooks=[logger.post_tool_use_hook])],
        },
    )
    stream = query(prompt="List the files in the current directory.", options=options)
    try:
        async for _message in stream:
            pass
    finally:
        await stream.aclose()


async def _drive_remaining_scopes() -> None:
    """Covers every Scope besides TOOL_CALL via direct log_event() calls."""
    await logger.log_event(
        Scope.USER_INPUT, session_id=SESSION_ID, turn_index=1,
        user_message="List the files in the current directory.",
    )
    await logger.log_event(
        Scope.ASSISTANT_TEXT, session_id=SESSION_ID, turn_index=1,
        payload="Here are the files in the current directory: ...",
    )
    await logger.log_event(
        Scope.FULL_TURN, session_id=SESSION_ID, turn_index=1,
        payload={"tool_calls": 1, "outcome": "success"},
    )
    await logger.log_event(
        Scope.ERROR, session_id=SESSION_ID, turn_index=1,
        error="Simulated error for scope coverage",
    )
    await logger.log_event(
        Scope.INFO, session_id=SESSION_ID, turn_index=1,
        payload="Session started",
    )
    await logger.log_event(
        Scope.WARNING, session_id=SESSION_ID, turn_index=1,
        payload="Simulated warning for scope coverage",
    )
    await logger.log_event(
        Scope.DEBUG, session_id=SESSION_ID, turn_index=1,
        payload={"note": "Simulated debug payload"},
    )


async def _run() -> None:
    config_path = Path(__file__).parent.parent.parent / "logger_config.json"
    logger.configure(json.loads(config_path.read_text()))

    await _drive_tool_call()
    await _drive_remaining_scopes()

    log_path = Path(logger.get_config().log_dir) / logger.get_config().filename_pattern
    print(f"Wrote trace log covering all {len(Scope)} scopes to: {log_path}")


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
