# src/auth_accelerator/providers.py
from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
 
@dataclass
class ResolvedCredential:
    kind: str                    # "api_key" | "oauth_session" | "os_session"
    env: dict[str, str]          # env vars to inject into the SDK subprocess
    detail: str                  # human-readable, for logs/diagnostics
 
class ApiKeyAuth:
    """Console API key - the same rule Juri uses: if ANTHROPIC_API_KEY
    is set and is not itself an OAuth token, prefer it. Works in any
    environment, billed pay-as-you-go."""
    name = "api_key"
    def resolve(self) -> ResolvedCredential | None:
        key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if key and key.startswith("sk-ant-api"):
            return ResolvedCredential(
                kind="api_key",
                env={"ANTHROPIC_API_KEY": key},
                detail="console API key from ANTHROPIC_API_KEY",
            )
        return None
 
class OAuthSessionAuth:
    """Ambient OAuth session from an already-authenticated `claude` CLI
    (Teams/Pro/Max login via `claude login`). Only valid when driven
    through claude_agent_sdk's subprocess, never the raw Messages API.
    Enabled only in local/dev by default - the same guard Juri applies."""
    name = "oauth_session"
    def __init__(self, environment: str):
        self.environment = environment.strip().lower()
    def resolve(self) -> ResolvedCredential | None:
        if self.environment not in ("local", "dev"):
            return None
        state_file = Path.home() / ".claude.json"
        if not state_file.exists():
            return None
        return ResolvedCredential(
            kind="oauth_session",
            env={},  # no override - claude_agent_sdk uses the ambient session
            detail=f"ambient `claude` CLI OAuth session ({state_file})",
        )
 
class OsSessionAuth:
    """OS-level auth for containerized deployments: the host's
    authenticated `claude` session (~/.claude and ~/.claude.json) is
    bind-mounted into the container filesystem at a known path, so the
    container inherits the session without ever holding a raw key.
    This is how Juri runs OAuth in production Docker."""
    name = "os_session"
    def __init__(self, mount_dir: str = "/home/agent/.claude", state_file: str = "/home/agent/.claude.json"):
        self.mount_dir = Path(mount_dir)
        self.state_file = Path(state_file)
    def resolve(self) -> ResolvedCredential | None:
        if not (self.mount_dir.exists() and self.state_file.exists()):
            return None
        return ResolvedCredential(
            kind="os_session",
            env={},
            detail=f"OS-mounted session at {self.mount_dir}",
        )
