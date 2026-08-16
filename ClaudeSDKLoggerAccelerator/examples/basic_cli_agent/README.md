# basic_cli_agent

Minimal end-to-end example: a Claude Agent SDK session with `sdk_logger_accelerator`'s hooks wired into `PreToolUse`/`PostToolUse`. Uses `claude-auth-accelerator` for credentials — that's a dependency of this sample only, not of `sdk_logger_accelerator` itself.

## Run

```bash
pip install -e ../.. -e ../../../claude-auth-accelerator
python main.py
```

Requires an authenticated `claude` CLI session (or `ANTHROPIC_API_KEY` set) — see `claude-auth-accelerator`'s README.

## Expected output

`./logs/trace.log` is created with one JSON line per `TOOL_CALL` (pre + post) the agent makes while listing files, e.g.:

```json
{"scope": "TOOL_CALL", "session_id": "...", "turn_index": 0, "timestamp": "...", "tool_name": "Bash", "tool_input": {"command": "ls"}, "tool_result": null, "error": null, "latency_ms": null, "model": null, "payload": null, "user_message": null, "metadata": {"tool_use_id": "...", "phase": "pre"}, "schema_version": "1.0"}
{"scope": "TOOL_CALL", "session_id": "...", "turn_index": 0, "timestamp": "...", "tool_name": "Bash", "tool_input": {"command": "ls"}, "tool_result": "main.py\nlogger_config.json\n...", "error": null, "latency_ms": 42.1, "model": null, "payload": null, "user_message": null, "metadata": {"tool_use_id": "...", "phase": "post"}, "schema_version": "1.0"}
```
