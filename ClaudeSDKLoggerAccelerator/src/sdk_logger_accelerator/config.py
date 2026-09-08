# src/sdk_logger_accelerator/config.py
from __future__ import annotations

from dataclasses import dataclass, field

from .exceptions import LoggerNotConfiguredError
from .schema import Scope

ALL_SCOPES = frozenset(Scope)


@dataclass
class RotationConfig:
    strategy: str = "size"  # "size" | "interval"
    max_bytes: int = 10 * 1024 * 1024
    backup_count: int = 5
    when: str = "midnight"  # only used for strategy == "interval"
    interval: int = 1


@dataclass
class LoggerConfig:
    log_dir: str
    filename_pattern: str = "trace.log"
    rotation: RotationConfig = field(default_factory=RotationConfig)
    enabled_scopes: frozenset[Scope] = field(default_factory=lambda: ALL_SCOPES)
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> LoggerConfig:
        rotation_data = data.get("rotation", {})
        rotation = RotationConfig(**rotation_data) if rotation_data else RotationConfig()
        scopes_data = data.get("enabled_scopes")
        enabled_scopes = (
            frozenset(Scope(s) for s in scopes_data) if scopes_data else ALL_SCOPES
        )
        return cls(
            log_dir=data["log_dir"],
            filename_pattern=data.get("filename_pattern", "trace.log"),
            rotation=rotation,
            enabled_scopes=enabled_scopes,
            enabled=data.get("enabled", True),
        )


_config: LoggerConfig | None = None


def configure(config: LoggerConfig | dict) -> None:
    """One-time setup per process. Call before any hook/log_event use."""
    global _config
    _config = config if isinstance(config, LoggerConfig) else LoggerConfig.from_dict(config)


def get_config() -> LoggerConfig:
    if _config is None:
        raise LoggerNotConfiguredError(
            "sdk_logger_accelerator.configure(...) must be called before use"
        )
    return _config


def reset_config() -> None:
    """Test-only helper to clear the module-level singleton."""
    global _config
    _config = None
