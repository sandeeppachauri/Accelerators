# src/auth_accelerator/resolver.py
from __future__ import annotations
import os
from .providers import ApiKeyAuth, OAuthSessionAuth, OsSessionAuth, ResolvedCredential
from .exceptions import AuthResolutionError

def _resolve_base_url(environment: str) -> str | None:
    return (
        os.environ.get(f"ANTHROPIC_BASE_URL_{environment.upper()}")
        or os.environ.get("ANTHROPIC_BASE_URL")
    )

def resolve_auth(environment: str = "local") -> ResolvedCredential:
    """Try providers in order: API key -> ambient OAuth -> OS-mounted
    session. First match wins - the same precedence Juri applies so a
    developer's console key never gets silently shadowed by a stale mount."""
    providers = [
        ApiKeyAuth(),
        OAuthSessionAuth(environment),
        OsSessionAuth(),
    ]
    for provider in providers:
        credential = provider.resolve()
        if credential is not None:
            base_url = _resolve_base_url(environment)
            if base_url:
                credential.env = {**credential.env, "ANTHROPIC_BASE_URL": base_url}
            return credential
    raise AuthResolutionError(
        "No Claude credential resolved. Set ANTHROPIC_API_KEY, run "
        "`claude login` for local/dev OAuth, or mount an authenticated "
        "session at /home/agent/.claude for containerized OS-level auth."
    )
