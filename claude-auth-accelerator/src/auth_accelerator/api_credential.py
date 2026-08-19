# src/auth_accelerator/api_credential.py
from __future__ import annotations
from .resolver import resolve_auth
from .exceptions import AuthResolutionError


def build_api_credential(environment: str = "local") -> str:
    """Resolve a credential usable with the raw Messages API (no SDK import)."""
    credential = resolve_auth(environment)
    if credential.kind != "api_key":
        raise AuthResolutionError(
            f"Ambient {credential.kind} found ({credential.detail}) but it cannot "
            "be used with the raw Messages API. Set ANTHROPIC_API_KEY instead."
        )
    return credential.env["ANTHROPIC_API_KEY"]
