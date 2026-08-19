# claude-auth-accelerator

Reusable credential resolution for [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python) consumers. Lets a consuming app build `ClaudeAgentOptions` without touching env vars or mount paths directly.

## Install

```bash
pip install -e claude-auth-accelerator
```

Requires Python >=3.10 and `claude-agent-sdk>=0.1.0`.

## Usage

```python
from auth_accelerator.options import build_options

options = build_options(environment="local", model="claude-sonnet-4-6", max_turns=10)
```

`build_options()` resolves a credential for the given `environment`, then returns a `ClaudeAgentOptions` with that credential's env vars merged in. Any extra kwargs (including an `env` dict) are passed through to `ClaudeAgentOptions` and merged on top of the resolved credential's env.

## Direct Messages API usage

For consumers calling the raw Claude Messages API directly (no `claude_agent_sdk`), use `build_api_credential()` instead of `build_options()`:

```python
from auth_accelerator import build_api_credential

api_key = build_api_credential(environment="local")
```

This resolves a credential the same way `build_options()` does, but returns a plain string and never imports `claude_agent_sdk`. It only succeeds when the resolved credential is a console `ANTHROPIC_API_KEY` (must start with `sk-ant-api`). If resolution instead finds an ambient `claude login` session (`OAuthSessionAuth`) or an OS-mounted session (`OsSessionAuth`), it raises `AuthResolutionError` — those credential kinds only work through the SDK's subprocess, not a direct API call. Set `ANTHROPIC_API_KEY` to use this path.

## Credential resolution

`resolve_auth(environment)` (`src/auth_accelerator/resolver.py`) tries providers in order and returns the first match. First match wins, so a developer's console key never gets silently shadowed by a stale mount:

1. **`ApiKeyAuth`** — uses `ANTHROPIC_API_KEY` if set and it looks like a console key (`sk-ant-api...`). Works in any environment, billed pay-as-you-go.
2. **`OAuthSessionAuth`** — ambient OAuth session from an already-authenticated `claude` CLI (Teams/Pro/Max login via `claude login`). Only enabled when `environment` is `local` or `dev`, and only if `~/.claude.json` exists. Only valid when driven through `claude_agent_sdk`'s subprocess, never the raw Messages API.
3. **`OsSessionAuth`** — OS-level auth for containerized deployments: the host's authenticated `claude` session (`~/.claude` and `~/.claude.json`) is bind-mounted into the container at `/home/agent/.claude` / `/home/agent/.claude.json`. Lets a container inherit the session without ever holding a raw key.

If none resolve, `resolve_auth` raises `AuthResolutionError` telling the caller to set `ANTHROPIC_API_KEY`, run `claude login`, or mount an authenticated session.

## Module layout

- `providers.py` — `ResolvedCredential` dataclass plus the three provider classes above.
- `resolver.py` — `resolve_auth`, which orders and tries the providers.
- `options.py` — `build_options`, which wraps `resolve_auth` and assembles `ClaudeAgentOptions`.
- `api_credential.py` — `build_api_credential`, which wraps `resolve_auth` for raw Messages API consumers (no SDK dependency).
- `exceptions.py` — `AuthResolutionError`.

## Related Accelerators

Pair with [`claude-sdk-logger-accelerator`](../ClaudeSDKLoggerAccelerator/README.md) for trace logging of tool calls and agent activity on the same `ClaudeAgentOptions`:

```bash
pip install -e claude-auth-accelerator
pip install -e ClaudeSDKLoggerAccelerator
```

Requires Python >=3.10 and `claude-agent-sdk>=0.1.0` (same requirement as this package).
