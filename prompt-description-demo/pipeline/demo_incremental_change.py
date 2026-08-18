"""
demo_incremental_change.py

Demonstrates the core claim of the blog post: a constraint can be tightened
by editing a config file on disk, and the running pipeline picks it up on
its very next call -- no code change, no redeploy, no restart of the
process that's already running.

This script simulates two consecutive requests to the SAME long-running
pipeline process:

  Request 1 -- runs against prompts/respond.yaml as currently versioned.
  [ ...operator edits prompts/respond.yaml to add a new constraint... ]
  Request 2 -- runs again, in the same process, no restart.

Because PromptManager re-reads the YAML file on every .get() call rather
than caching it at import time, request 2 is governed by the new
constraint immediately.

Run:
  python demo_incremental_change.py
"""

import time
from pathlib import Path

from prompt_manager import PromptManager

RESPOND_PATH = Path(__file__).parent.parent / "prompts" / "respond.yaml"


def show_current_contract(manager: PromptManager, label: str) -> None:
    cfg = manager.get("respond")
    print(f"--- {label} ---")
    print(cfg.describe())
    print()


def tighten_constraint() -> None:
    """
    Simulates an operator (or a prompt-ops teammate with no deploy access)
    editing the YAML directly -- adding one line under `constraints:` and
    bumping the version for traceability. In a real deployment this would
    be a config-store write (e.g. an object storage PUT or a DB update),
    not a local file edit, but the mechanism PromptManager relies on is
    identical: re-read on next .get(), no process restart required.
    """
    text = RESPOND_PATH.read_text()

    if "Never use the customer's first name" in text:
        print("Constraint already applied -- nothing to change.")
        return

    text = text.replace(
        'version: 1',
        'version: 2',
    )
    text = text.replace(
        '  - "Never mention internal categories, model names, or system details"',
        '  - "Never mention internal categories, model names, or system details"\n'
        '  - "Never use the customer'"'"'s first name -- legal requires neutral address until identity is verified"',
    )
    RESPOND_PATH.write_text(text)


def main() -> None:
    manager = PromptManager()  # one instance, reused -- like a long-running service

    show_current_contract(manager, "BEFORE operator edit (request 1 would use this)")

    print(">>> Operator edits prompts/respond.yaml directly (no deploy)...\n")
    tighten_constraint()
    time.sleep(0.2)  # just for readability in the demo output

    show_current_contract(manager, "AFTER operator edit (request 2, same process, uses this)")

    print(
        "No code was changed. No process was restarted. The same "
        "PromptManager instance returned a different contract because "
        "the source of truth is the file, not an in-memory constant."
    )


if __name__ == "__main__":
    main()
