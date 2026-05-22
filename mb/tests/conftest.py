"""Pytest fixtures for mb tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from mb import __version__
from mb import codex as codex_mod


@pytest.fixture()
def tmp_repo(tmp_path: Path) -> Path:
    """Empty directory ready for ``mb init``."""
    return tmp_path / "biz"


@pytest.fixture(autouse=True)
def stable_runtime_mb_probe(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep Codex runtime readiness tests independent of the host PATH."""

    monkeypatch.setattr(
        codex_mod,
        "_login_shell_mb_diagnostics",
        lambda: {
            "checked": True,
            "ok": True,
            "state": "ok",
            "shell": "/bin/sh",
            "command": "command -v mb && mb --version",
            "path": "/usr/local/bin/mb",
            "version": __version__,
            "active_path": "/usr/local/bin/mb",
            "active_version": __version__,
            "path_mismatch": False,
            "version_mismatch": False,
            "mismatch": False,
            "error": "",
            "summary": "Login-shell runtime resolves the current mb command.",
            "repair": "",
            "safe_to_share": True,
        },
    )
