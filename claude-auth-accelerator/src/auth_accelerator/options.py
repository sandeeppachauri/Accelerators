# src/auth_accelerator/options.py
from __future__ import annotations
from claude_agent_sdk import ClaudeAgentOptions
from .resolver import resolve_auth
 
def build_options(
    environment: str = "local",
    model: str = "claude-sonnet-4-6",
    max_turns: int = 10,
    **extra,
) -> ClaudeAgentOptions:
    """Resolve auth, then assemble ClaudeAgentOptions. A consumer never
    has to touch env vars or mount paths directly."""
    credential = resolve_auth(environment)
    return ClaudeAgentOptions(
        model=model,
        max_turns=max_turns,
        env={**credential.env, **extra.pop("env", {})},
        **extra,
    )
