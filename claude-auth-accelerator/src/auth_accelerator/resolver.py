# src/auth_accelerator/resolver.py
from __future__ import annotations
from .providers import ApiKeyAuth, OAuthSessionAuth, OsSessionAuth, ResolvedCredential
from .exceptions import AuthResolutionError
 
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
            return credential
    raise AuthResolutionError(
        "No Claude credential resolved. Set ANTHROPIC_API_KEY, run "
        "`claude login` for local/dev OAuth, or mount an authenticated "
        "session at /home/agent/.claude for containerized OS-level auth."
    )
