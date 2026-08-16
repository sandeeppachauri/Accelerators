# claude-sdk-logger-accelerator

Drop-in, on-demand tracing of [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python) tool calls and agent activity. Nothing is auto-instrumented — you wire the provided hook functions into your own `ClaudeAgentOptions` hook config, so a project can adopt this without touching anything else (auth, other Accelerators, etc).

## Install

```bash
pip install -e claude-sdk-logger-accelerator
```

Requires Python >=3.10 and `claude-agent-sdk>=0.1.0`.

## Usage

```python
from claude_agent_sdk import ClaudeAgentOptions
import sdk_logger_accelerator as logger

logger.configure({
    "log_dir": "./logs",
    "filename_pattern": "trace.log",
    "rotation": {"strategy": "size", "max_bytes": 10_000_000, "backup_count": 5},
    "enabled_scopes": ["TOOL_CALL", "ERROR", "INFO"],
})

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [logger.pre_tool_use_hook],
        "PostToolUse": [logger.post_tool_use_hook],
    },
)
```

Anywhere else in your turn loop, log the scopes that aren't tool calls directly:

```python
await logger.log_event(logger.Scope.USER_INPUT, session_id=session_id, turn_index=turn_index, user_message=text)
```

`configure()` is called once per process, at setup. `pre_tool_use_hook` / `post_tool_use_hook` are `async def` coroutines matching the SDK's hook contract — the SDK's own hook runner awaits them, so a write failure raises `LoggerWriteError` straight into the host's hook-execution context instead of being silently swallowed.

## Configuration

| Field | Type | Notes |
|---|---|---|
| `log_dir` | `str` | Directory the trace file(s) are written to |
| `filename_pattern` | `str` | Base filename, default `trace.log` |
| `rotation.strategy` | `"size"` \| `"interval"` | `size` uses `max_bytes`/`backup_count`; `interval` uses `when`/`interval`/`backup_count` (same semantics as `logging.handlers.RotatingFileHandler` / `TimedRotatingFileHandler`) |
| `enabled_scopes` | list of scope names | Filter applied at write time; omit for all 8 scopes |

## Trace schema

Every record is one JSON line, versioned via `schema_version`:

`session_id`, `turn_index`, `timestamp`, `schema_version`, `tool_name`, `tool_input`, `tool_result`, `error`, `latency_ms`, `model`, `payload`, `user_message`, `metadata`, `scope`.

`Scope` (dual-purpose: activity type + severity filter): `TOOL_CALL, ASSISTANT_TEXT, USER_INPUT, FULL_TURN, ERROR, INFO, WARNING, DEBUG`.

## Failure behavior

On write failure (bad path, disk full, etc.) `write_trace` raises `LoggerWriteError` at the point where it's running — never swallowed silently. Access control is inherited from whoever runs the host process; there is no redaction layer in v1.

## Module layout

- `schema.py` — `TraceRecord`, `Scope`, `SCHEMA_VERSION`.
- `config.py` — `LoggerConfig`, `RotationConfig`, `configure()`, `get_config()`.
- `rotation.py` — builds the stdlib rotating-file `logging.Logger` sink.
- `writer.py` — `write_trace()`, the async, scope-filtered write path.
- `hooks.py` — `pre_tool_use_hook`, `post_tool_use_hook`, `log_event()`.
- `exceptions.py` — `LoggerWriteError`, `LoggerNotConfiguredError`.

## Samples

- [`examples/basic_cli_agent`](examples/basic_cli_agent/README.md) — minimal end-to-end usage.
- [`ClaudeSDKLoggerAcceleratorTester`](../ClaudeSDKLoggerAcceleratorTester/README.md) — exercises every trace scope.
