# src/auth_accelerator/__init__.py
from __future__ import annotations

from .api_credential import build_api_credential
from .exceptions import AuthResolutionError
from .providers import ResolvedCredential
from .resolver import resolve_auth

__all__ = [
    "AuthResolutionError",
    "ResolvedCredential",
    "build_api_credential",
    "build_options",
    "resolve_auth",
]


def __getattr__(name: str):
    # Deferred so importing this package never requires claude_agent_sdk
    # unless build_options is actually used.
    if name == "build_options":
        from .options import build_options
        return build_options
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
