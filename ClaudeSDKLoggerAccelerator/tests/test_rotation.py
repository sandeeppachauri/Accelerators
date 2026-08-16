import glob
import os

import pytest

from sdk_logger_accelerator.config import LoggerConfig, RotationConfig
from sdk_logger_accelerator import rotation


@pytest.fixture(autouse=True)
def _reset_logger():
    rotation.reset_logger()
    yield
    rotation.reset_logger()


def test_size_rotation_creates_backup_files(tmp_path):
    config = LoggerConfig(
        log_dir=str(tmp_path),
        filename_pattern="trace.log",
        rotation=RotationConfig(strategy="size", max_bytes=200, backup_count=3),
    )
    logger = rotation.build_logger(config)
    for i in range(200):
        logger.info("x" * 20 + f" {i}")

    files = glob.glob(os.path.join(tmp_path, "trace.log*"))
    assert len(files) > 1


def test_build_logger_is_cached(tmp_path):
    config = LoggerConfig(log_dir=str(tmp_path))
    first = rotation.build_logger(config)
    second = rotation.build_logger(config)
    assert first is second


def test_unknown_strategy_raises(tmp_path):
    config = LoggerConfig(
        log_dir=str(tmp_path),
        rotation=RotationConfig(strategy="bogus"),
    )
    with pytest.raises(ValueError):
        rotation.build_logger(config)
