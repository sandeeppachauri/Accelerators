# src/release_notes_agent/agent.py
from __future__ import annotations
import asyncio, os
from auth_accelerator.options import build_options
from claude_agent_sdk import ResultMessage, query
 
async def summarize(diff_text: str) -> str:
    options = build_options(environment=os.environ.get("ENVIRONMENT", "local"))
    prompt = f"Summarize this diff as one release-note bullet:\n\n{diff_text}"
    result = "(no result message received)"
    stream = query(prompt=prompt, options=options)
    try:
        async for message in stream:
            if isinstance(message, ResultMessage):
                result = message.result or "(no text returned)"
                break
    finally:
        await stream.aclose()
        
    return result
 
def summarize_sync(diff_text: str) -> str:
    return asyncio.run(summarize(diff_text))
