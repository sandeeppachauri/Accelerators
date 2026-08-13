# src/auth_accelerator/exceptions.py
from __future__ import annotations


class AuthResolutionError(RuntimeError):
    """Raised when no credential provider could resolve a Claude credential."""
