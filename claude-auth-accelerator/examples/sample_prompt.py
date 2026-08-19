"""Sample prompts for each auth mode: OAuth session, raw Messages API, OS-mounted session.

Precedence note: resolve_auth() always tries ANTHROPIC_API_KEY -> ambient OAuth ->
OS-mounted session, first match wins. These examples call the specific provider
each mode needs so the demo runs even if a higher-precedence credential is present.
"""
from __future__ import annotations
import anyio
from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, TextBlock, query
from auth_accelerator.exceptions import AuthResolutionError
from auth_accelerator.providers import OAuthSessionAuth, OsSessionAuth


async def run_oauth_session_example() -> None:
    """Mode 1: ambient `claude` CLI OAuth session (local/dev only, via SDK)."""
    credential = OAuthSessionAuth(environment="local").resolve()
    if credential is None:
        print("[oauth_session] skipped: run `claude login` first")
        return
    print(f"[oauth_session] using {credential.detail}")
    options = ClaudeAgentOptions(model="claude-sonnet-4-6", max_turns=10, env=credential.env)
    async for message in query(prompt="Say hello in exactly 5 words.", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)


def run_messages_api_example() -> None:
    """Mode 2: raw Messages API with a console API key (no SDK subprocess)."""
    from auth_accelerator import build_api_credential
    import anthropic

    try:
        api_key = build_api_credential(environment="local")
    except AuthResolutionError as exc:
        print(f"[messages_api] skipped: {exc}")
        return
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=32,
        messages=[{"role": "user", "content": "Say hello in exactly 5 words."}],
    )
    print(response.content[0].text)


async def run_os_session_example() -> None:
    """Mode 3: OS-mounted session for containerized deployments (via SDK)."""
    credential = OsSessionAuth().resolve()
    if credential is None:
        print("[os_session] skipped: no session mounted at /home/agent/.claude")
        return
    print(f"[os_session] using {credential.detail}")
    options = ClaudeAgentOptions(model="claude-sonnet-4-6", max_turns=10, env=credential.env)
    async for message in query(prompt="Say hello in exactly 5 words.", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)


async def main() -> None:
    await run_oauth_session_example()
    run_messages_api_example()
    await run_os_session_example()


if __name__ == "__main__":
    anyio.run(main)
