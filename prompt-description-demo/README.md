# Prompt-as-Config Demo — Description Applied to Prompt Design

Companion project for the blog post "Description in Prompt Design: Why 'It
Works in the Demo' Isn't Enough."

## What this demonstrates

Three things a demo-quality prompt setup usually skips:

1. **Scope, format, and constraints are structured config fields**, not
   just prose inside a system prompt — see `prompts/*.yaml`.
2. **The format contract is enforced in code**, not just requested in
   text — see `PromptManager.validate_output()` in `pipeline/prompt_manager.py`.
3. **A constraint can be tightened with a config edit alone** — no code
   change, no redeploy — see `pipeline/demo_incremental_change.py`.

Authentication is handled entirely separately, via
[`claude-auth-accelerator`](https://github.com/sandeeppachauri/Accelerators/tree/main/claude-auth-accelerator)'s
`build_options()`. Nothing in `prompt_manager.py` or the prompt configs
knows or cares how credentials are resolved — that separation is itself
an application of the constraints pillar: a prompt change can never
accidentally touch auth, and vice versa.

## Structure

```
prompts/
  classify.yaml     # scope / format / constraints for the classify step
  extract.yaml       # ...for the extract step
  respond.yaml        # ...for the respond step (used in the live demo)
pipeline/
  prompt_manager.py            # loads + validates prompt config; hot-reloads on every call
  run_pipeline.py               # full 3-step pipeline: PromptManager (what) + auth-accelerator (how)
  demo_incremental_change.py    # shows a constraint added via YAML edit alone
```

## Running it

```bash
pip install claude-agent-sdk pyyaml
pip install -e git+https://github.com/sandeeppachauri/Accelerators.git#subdirectory=claude-auth-accelerator

export ANTHROPIC_API_KEY=sk-ant-api...     # or: claude login   (local/dev)

cd pipeline
python run_pipeline.py                 # full pipeline, real model calls
python demo_incremental_change.py      # constraint-tightening demo, no model calls needed
```

`demo_incremental_change.py` only reads/writes `prompts/respond.yaml` and
re-loads it through `PromptManager` — it does not call the Claude API, so
it runs with no credentials configured.
