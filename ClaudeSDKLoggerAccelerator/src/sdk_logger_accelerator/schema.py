# src/sdk_logger_accelerator/schema.py
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

SCHEMA_VERSION = "1.0"


class Scope(str, Enum):
    """Tags a trace record's kind; also used as the enabled_scopes filter."""

    TOOL_CALL = "TOOL_CALL"
    ASSISTANT_TEXT = "ASSISTANT_TEXT"
    USER_INPUT = "USER_INPUT"
    FULL_TURN = "FULL_TURN"
    ERROR = "ERROR"
    INFO = "INFO"
    WARNING = "WARNING"
    DEBUG = "DEBUG"


@dataclass
class TraceRecord:
    scope: Scope
    session_id: str
    turn_index: int
    timestamp: str
    tool_name: str | None = None
    tool_input: Any = None
    tool_result: Any = None
    error: str | None = None
    latency_ms: float | None = None
    model: str | None = None
    payload: Any = None
    user_message: str | None = None
    metadata: dict = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict:
        record = asdict(self)
        record["scope"] = self.scope.value
        return record
