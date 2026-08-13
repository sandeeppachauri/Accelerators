# release-notes-agent

Summarizes a git diff into a one-line release-note bullet, using the Claude Agent SDK. Credentials are resolved via [`claude-auth-accelerator`](../claude-auth-accelerator/README.md) (console API key -> ambient `claude` CLI OAuth -> OS-mounted session).

## Install

From the workspace root (`d:\Claude\Accelerators`):

```bash
pip install -e claude-auth-accelerator
pip install -e release-notes-agent
```

## Configure

Copy `.env.example` to `.env` and fill in as needed:

```bash
cp .env.example .env
```

- `ANTHROPIC_API_KEY` — console key, works anywhere, takes priority if set.
- `ENVIRONMENT` — `local` (default) enables ambient OAuth from `claude login`; any other value requires `ANTHROPIC_API_KEY` or an OS-mounted session.

If you're logged in locally via `claude login`, you can leave `ANTHROPIC_API_KEY` blank.

## Try it

Create a sample diff file:

```bash
printf 'diff --git a/foo.py b/foo.py\n+def foo(): pass\n' > sample.diff
```

Run it via the console script:

```bash
release-notes sample.diff
```

Or as a module:

```bash
python -m release_notes_agent.cli sample.diff
```

Expected output (wording varies):

```
- Added `foo()` function to `foo.py`.
```

## Module layout

- `agent.py` — `summarize` / `summarize_sync`: sends the diff to Claude via `query()`, returns the `ResultMessage.result` text.
- `cli.py` — `main`: argparse entry point, reads a `.diff` file path and prints the summary. Registered as the `release-notes` console script.
