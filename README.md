# Accelerators

Reusable building blocks for apps built on the [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python).

## Projects

- [`claude-auth-accelerator`](claude-auth-accelerator/README.md) — reusable credential resolution (console API key -> ambient `claude` CLI OAuth -> OS-mounted session) so consumers never touch env vars or mount paths directly.
- [`release-notes-agent`](release-notes-agent/README.md) — summarizes a git diff into a one-line release-note bullet, built on top of `claude-auth-accelerator`.

## Install

Each project is an independently installable Python package under `src/` (PEP 660 editable installs):

```bash
pip install -e claude-auth-accelerator
pip install -e release-notes-agent
```

See each project's README for usage and configuration.
