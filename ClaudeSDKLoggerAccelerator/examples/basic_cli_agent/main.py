from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from auth_accelerator.options import build_options
from claude_agent_sdk import HookMatcher, query

import sdk_logger_accelerator as logger


async def main() -> None:
    config_path = Path(__file__).parent / "logger_config.json"
    logger.configure(json.loads(config_path.read_text()))

    options = build_options(
        environment=os.environ.get("ENVIRONMENT", "local"),
        hooks={
            "PreToolUse": [HookMatcher(hooks=[logger.pre_tool_use_hook])],
            "PostToolUse": [HookMatcher(hooks=[logger.post_tool_use_hook])],
        },
    )

    prompt = "List the files in the current directory, then say hello."
    stream = query(prompt=prompt, options=options)
    try:
        async for message in stream:
            print(message)
    finally:
        await stream.aclose()


if __name__ == "__main__":
    asyncio.run(main())
