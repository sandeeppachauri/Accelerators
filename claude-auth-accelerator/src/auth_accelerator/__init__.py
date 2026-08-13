# src/auth_accelerator/__init__.py
from __future__ import annotations

from .exceptions import AuthResolutionError
from .options import build_options
from .providers import ResolvedCredential
from .resolver import resolve_auth

__all__ = [
    "AuthResolutionError",
    "ResolvedCredential",
    "build_options",
    "resolve_auth",
]
