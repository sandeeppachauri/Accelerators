# claude-sdk-logger-accelerator-tester

Standalone project that test-drives `claude-sdk-logger-accelerator` with every `enabled_scopes` value turned on, and produces at least one log line per `Scope`. Not a usage doc (see `ClaudeSDKLoggerAccelerator/examples/basic_cli_agent` for that) — this is a scope-coverage smoke test.

Depends on `claude-sdk-logger-accelerator` and (for its own SDK invocation only) `claude-auth-accelerator`. Neither the core logger package nor this tester depend on each other in the other direction.

## Install

```bash
pip install -e ../ClaudeSDKLoggerAccelerator -e ../claude-auth-accelerator -e .
```

## Run

```bash
logger-tester
# or: python -m logger_tester.run
```

Requires an authenticated `claude` CLI session (or `ANTHROPIC_API_KEY` set) for the one real tool-call turn — see `claude-auth-accelerator`'s README.

## What it does

1. Configures the logger with all 8 scopes enabled (`logger_config.json`).
2. Runs one real Claude Agent SDK turn with `pre_tool_use_hook`/`post_tool_use_hook` wired in — covers `TOOL_CALL`.
3. Calls `log_event()` directly once for each of `USER_INPUT`, `ASSISTANT_TEXT`, `FULL_TURN`, `ERROR`, `INFO`, `WARNING`, `DEBUG`.
4. Prints the path to the resulting `./logs/trace.log`, which contains one JSON line per scope (two for `TOOL_CALL`: pre + post), each with `schema_version` set.
