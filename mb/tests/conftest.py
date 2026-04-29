"""Pytest fixtures for mb tests."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture()
def tmp_repo(tmp_path: Path) -> Path:
    """Empty directory ready for ``mb init``."""
    return tmp_path / "biz"
