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
def isolated_state_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep every test's ``mb feedback`` writes out of the real user state dir.

    Connect boundary refusals log themselves, so any test that reaches one
    would otherwise append to the operator's own feedback file.
    """

    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "xdg-state"))
    monkeypatch.delenv("MB_FEEDBACK_LOG", raising=False)


@pytest.fixture(autouse=True)
def isolated_credential_backend(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep every test away from the operator's own credential store.

    `mb connect status` probes credential-backend health even with no
    provider connected, so without this a status-reading test would ask the
    real Keychain or Secret Service. Tests that need another backend set it.
    """

    monkeypatch.setenv("MB_CONNECT_SECRET_BACKEND", "local-file")
    monkeypatch.setenv("MAINBRANCH_HOME", str(tmp_path / "mainbranch-home"))


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
