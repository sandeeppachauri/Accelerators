# tests/test_api_credential.py
from __future__ import annotations
import pytest
from auth_accelerator.api_credential import build_api_credential
from auth_accelerator.exceptions import AuthResolutionError


def test_returns_key_when_api_key_set(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-api-abc123")
    assert build_api_credential("local") == "sk-ant-api-abc123"


def test_raises_when_no_credential_resolves(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(
        "auth_accelerator.resolver.OAuthSessionAuth.resolve", lambda self: None
    )
    monkeypatch.setattr(
        "auth_accelerator.resolver.OsSessionAuth.resolve", lambda self: None
    )
    with pytest.raises(AuthResolutionError, match="No Claude credential resolved"):
        build_api_credential("local")


def test_raises_when_only_ambient_session_available(monkeypatch):
    from auth_accelerator.providers import ResolvedCredential

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(
        "auth_accelerator.resolver.OAuthSessionAuth.resolve",
        lambda self: ResolvedCredential(
            kind="oauth_session", env={}, detail="ambient `claude` CLI OAuth session"
        ),
    )
    with pytest.raises(AuthResolutionError, match="cannot be used with the raw Messages API"):
        build_api_credential("local")
