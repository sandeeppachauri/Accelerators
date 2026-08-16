import json
import os

import pytest

from sdk_logger_accelerator import config as config_module
from sdk_logger_accelerator import rotation
from sdk_logger_accelerator.config import LoggerConfig
from sdk_logger_accelerator.exceptions import LoggerWriteError
from sdk_logger_accelerator.hooks import log_event, post_tool_use_hook, pre_tool_use_hook
from sdk_logger_accelerator.schema import Scope


@pytest.fixture(autouse=True)
def _reset_state():
    config_module.reset_config()
    rotation.reset_logger()
    yield
    config_module.reset_config()
    rotation.reset_logger()


def _read_lines(log_dir, filename="trace.log"):
    path = os.path.join(log_dir, filename)
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


@pytest.mark.asyncio
async def test_pre_and_post_tool_use_hook_pair_by_tool_use_id(tmp_path):
    config_module.configure(LoggerConfig(log_dir=str(tmp_path)))

    await pre_tool_use_hook({"tool_name": "Read", "tool_input": {"path": "a.py"}}, "call-1")
    await post_tool_use_hook({"tool_name": "Read", "tool_response": "ok"}, "call-1")

    lines = _read_lines(tmp_path)
    assert len(lines) == 2
    assert lines[0]["scope"] == "TOOL_CALL"
    assert lines[1]["tool_result"] == "ok"
    assert lines[1]["latency_ms"] is not None


@pytest.mark.asyncio
async def test_log_event_covers_every_scope(tmp_path):
    config_module.configure(LoggerConfig(log_dir=str(tmp_path)))

    for scope in Scope:
        await log_event(scope, session_id="s1", turn_index=1, payload={"scope": scope.value})

    lines = _read_lines(tmp_path)
    assert {line["scope"] for line in lines} == {s.value for s in Scope}


@pytest.mark.asyncio
async def test_disabled_scope_is_not_written(tmp_path):
    config_module.configure(
        LoggerConfig(log_dir=str(tmp_path), enabled_scopes=frozenset({Scope.ERROR}))
    )

    await log_event(Scope.DEBUG, session_id="s1")
    await log_event(Scope.ERROR, session_id="s1")

    lines = _read_lines(tmp_path)
    assert len(lines) == 1
    assert lines[0]["scope"] == "ERROR"


@pytest.mark.asyncio
async def test_write_failure_propagates(tmp_path):
    blocked_path = tmp_path / "blocked"
    blocked_path.write_text("not a directory")
    config_module.configure(LoggerConfig(log_dir=str(blocked_path)))

    with pytest.raises(LoggerWriteError):
        await log_event(Scope.ERROR, session_id="s1")
