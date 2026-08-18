"""
prompt_manager.py

Externalizes prompts as versioned, structured config -- the Description
competency applied as an engineering discipline rather than a prompt-writing
tip. Each prompt file declares its SCOPE, FORMAT, and CONSTRAINTS as
first-class fields, not just prose baked into a system_prompt string.

Why this exists:
  A prompt that lives only as a string embedded in application code can only
  change when that code is redeployed. That means the same failure modes as
  a hardcoded integration endpoint or a hardcoded XSLT transform: every
  tightening of a rule, every fix to a drifting format, becomes a deployment
  event. This module treats prompts the way an integration architect treats
  endpoint config or transformation maps -- externalized, versioned, and
  reloadable without touching the running process.

What it does NOT do:
  It does not resolve authentication. Credential resolution is handled
  entirely by claude-auth-accelerator's build_options() in the pipeline
  layer. PromptManager only ever returns prompt config -- it has no
  knowledge of API keys, OAuth sessions, or environment. That separation is
  itself an application of the CONSTRAINTS pillar: a change to a prompt's
  wording can never accidentally touch how the pipeline authenticates.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class PromptValidationError(Exception):
    """Raised when a prompt config file is missing a required Description field."""


class OutputContractError(Exception):
    """Raised when a model's actual output fails to satisfy the prompt's format contract."""


@dataclass(frozen=True)
class PromptConfig:
    step: str
    version: int
    scope: dict[str, Any]
    format: dict[str, Any]
    constraints: list[str]
    system_prompt: str

    def describe(self) -> str:
        """Human-readable summary -- useful for logging which contract was
        actually in force for a given run."""
        lines = [
            f"[{self.step} v{self.version}]",
            f"  in_bounds:     {self.scope.get('in_bounds')}",
            f"  out_of_bounds: {self.scope.get('out_of_bounds')}",
            f"  format:        {self.format}",
            f"  constraints:   {len(self.constraints)} rule(s)",
        ]
        return "\n".join(lines)


class PromptManager:
    """
    Loads prompt configs from disk on every call to get(). This is the
    "hot reload" mechanism: because the source of truth is a file (or, in
    a production deployment, a config table / object store key) rather
    than an in-process constant, an edit to the YAML takes effect on the
    very next request -- no redeploy, no restart.

    A production version of this would swap the file read for a cached
    read-through against a config service (e.g. an OCI Object Storage
    bucket, a DB table, or a feature-flag service) with a short TTL, but
    the contract PromptManager exposes to callers stays identical.
    """

    REQUIRED_FIELDS = {"step", "version", "scope", "format", "constraints", "system_prompt"}

    def __init__(self, prompts_dir: Path = PROMPTS_DIR):
        self.prompts_dir = prompts_dir

    def get(self, step: str) -> PromptConfig:
        path = self.prompts_dir / f"{step}.yaml"
        if not path.exists():
            raise PromptValidationError(f"No prompt config found for step '{step}' at {path}")

        with open(path, "r") as f:
            raw = yaml.safe_load(f)

        missing = self.REQUIRED_FIELDS - raw.keys()
        if missing:
            raise PromptValidationError(
                f"Prompt config for '{step}' is missing required Description "
                f"fields: {sorted(missing)}. A prompt without scope/format/"
                f"constraints is exactly the under-described prompt that "
                f"breaks in production."
            )

        return PromptConfig(
            step=raw["step"],
            version=raw["version"],
            scope=raw["scope"],
            format=raw["format"],
            constraints=raw["constraints"],
            system_prompt=raw["system_prompt"],
        )

    def validate_output(self, step: str, cfg: PromptConfig, output: str) -> Any:
        """
        Enforces the FORMAT pillar in code, not just in prompt text.
        A model can ignore an instruction; it cannot ignore a contract
        checked by the calling application before the output is trusted
        downstream. Raises OutputContractError on violation.
        """
        fmt = cfg.format

        if fmt["type"] == "enum":
            value = output.strip()
            if fmt.get("case") == "lower":
                value = value.lower()
            allowed = fmt["allowed_values"]
            if value not in allowed:
                raise OutputContractError(
                    f"[{step} v{cfg.version}] output '{output!r}' is not one of "
                    f"the allowed_values {allowed}"
                )
            return value

        if fmt["type"] == "json":
            try:
                parsed = json.loads(output.strip())
            except json.JSONDecodeError as e:
                raise OutputContractError(
                    f"[{step} v{cfg.version}] output is not valid JSON: {e}"
                ) from e

            expected_keys = set(fmt["schema"].keys())
            actual_keys = set(parsed.keys())
            if actual_keys != expected_keys:
                raise OutputContractError(
                    f"[{step} v{cfg.version}] JSON keys {sorted(actual_keys)} "
                    f"do not match contract {sorted(expected_keys)}"
                )

            urgency_spec = fmt["schema"].get("urgency", "")
            if urgency_spec.startswith("enum["):
                allowed = [v.strip() for v in urgency_spec[5:-1].split(",")]
                if parsed.get("urgency") not in allowed:
                    raise OutputContractError(
                        f"[{step} v{cfg.version}] urgency '{parsed.get('urgency')}' "
                        f"not in {allowed}"
                    )
            return parsed

        if fmt["type"] == "text":
            word_count = len(output.split())
            max_words = fmt.get("max_words")
            if max_words and word_count > max_words:
                raise OutputContractError(
                    f"[{step} v{cfg.version}] output is {word_count} words, "
                    f"exceeds max_words={max_words}"
                )
            return output.strip()

        raise OutputContractError(f"Unknown format type '{fmt['type']}' in contract")
