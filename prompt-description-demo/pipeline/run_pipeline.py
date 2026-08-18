"""
run_pipeline.py

Ties together two independent, cleanly-separated concerns:

  1. WHAT to ask the model -- PromptManager, loading versioned prompt
     config (scope / format / constraints) from prompts/*.yaml.
  2. HOW to authenticate the call -- claude-auth-accelerator's
     build_options(), resolving credentials via the
     ApiKeyAuth -> OAuthSessionAuth -> OsSessionAuth chain.

Neither concern knows the other exists. A prompt's constraints can be
tightened by editing YAML -- zero redeploy, zero touch to auth. Auth's
resolution order can change -- zero touch to prompt logic. This mirrors
how an integration architect keeps a transformation map and a connection
pool as separately versioned, separately deployable artifacts.

Setup:
  pip install claude-agent-sdk pyyaml
  pip install -e git+https://github.com/sandeeppachauri/Accelerators.git#subdirectory=claude-auth-accelerator

  export ANTHROPIC_API_KEY=sk-ant-api...     # any environment
  # or, for local/dev:
  claude login                                # ambient OAuth session

Run:
  python run_pipeline.py
"""

import asyncio
import json
import time

from claude_agent_sdk import query, AssistantMessage, TextBlock
from auth_accelerator import build_options, AuthResolutionError

from prompt_manager import PromptManager, OutputContractError

ENVIRONMENT = "local"  # "local" | "dev" | "prod" -- passed to build_options()

# Per-step model routing -- unchanged from the original accelerator sample.
# This stays separate from prompt config on purpose: which model answers a
# step and what that step is described to do are different decisions, made
# by different people, on different cadences.
MODEL_ROUTING = {
    "classify": "claude-haiku-4-5-20251001",
    "extract": "claude-sonnet-5",
    "respond": "claude-opus-4-8",
}

prompt_manager = PromptManager()


async def call_step(step: str, user_content: str) -> str:
    """
    Run one pipeline step:
      - pull its versioned prompt contract from PromptManager (WHAT)
      - pull its model from MODEL_ROUTING
      - resolve auth via build_options() (HOW) -- the step never sees a
        credential directly, exactly as in the original per-step routing
        sample.
    """
    cfg = prompt_manager.get(step)
    model = MODEL_ROUTING[step]

    options = build_options(
        environment=ENVIRONMENT,
        model=model,
        max_turns=1,
        system_prompt=cfg.system_prompt,
    )

    start = time.time()
    text = ""
    async for message in query(prompt=user_content, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    text += block.text
    elapsed = time.time() - start

    print(f"[{step:9s}] prompt_version={cfg.version}  model={model:28s} time={elapsed:5.2f}s")

    # Enforce the FORMAT pillar in code -- not just in the prompt text.
    validated = prompt_manager.validate_output(step, cfg, text)
    return validated


async def run_pipeline(ticket_text: str) -> dict:
    category = await call_step(
        "classify",
        f"Classify this support ticket:\n\n{ticket_text}",
    )

    extracted = await call_step(
        "extract",
        f"Extract structured facts from this ticket:\n\n{ticket_text}",
    )

    draft_reply = await call_step(
        "respond",
        f"Category: {category}\nExtracted context: {json.dumps(extracted)}\n"
        f"Original ticket: {ticket_text}",
    )

    return {
        "category": category,
        "extracted": extracted,
        "draft_reply": draft_reply,
    }


async def main() -> None:
    sample_ticket = (
        "Hi, I was charged twice for my subscription this month and "
        "I need this fixed before my card is charged again next week."
    )

    print("=" * 72)
    print("PROMPT-AS-CONFIG PIPELINE RUN")
    print("=" * 72)

    for step in ("classify", "extract", "respond"):
        print(prompt_manager.get(step).describe())
        print("-" * 72)

    try:
        result = await run_pipeline(sample_ticket)
    except (AuthResolutionError, OutputContractError) as e:
        print(f"Pipeline halted -- contract violation or auth failure: {e}")
        return

    print("=" * 72)
    print("FINAL OUTPUT")
    print("=" * 72)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
