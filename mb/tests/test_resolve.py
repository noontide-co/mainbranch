"""``mb resolve`` layered lookup."""

from __future__ import annotations

from pathlib import Path

from mb import engine as engine_mod
from mb.engine import engine_root
from mb.resolve import bundled_skills, run, skill_path


def test_resolve_local_override(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    (repo / "core").mkdir(parents=True)
    (repo / "core" / "voice.md").write_text("# Voice\n")
    out = run(key="voice", repo=str(repo))
    assert out["resolved"] is True
    assert out["tier"] == "local"
    assert out["is_stub"] is False


def test_resolve_ignores_legacy_vip_path_overrides(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    (repo / ".vip").mkdir(parents=True)
    (repo / ".vip" / "config.yaml").write_text(
        "paths:\n  core: legacy-core\n",
        encoding="utf-8",
    )
    (repo / "legacy-core").mkdir()
    (repo / "legacy-core" / "voice.md").write_text("# Legacy voice\n", encoding="utf-8")

    out = run(key="voice", repo=str(repo))

    assert out["tier"] != "local"


def test_resolve_unknown_key_returns_unresolved_or_stub(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    repo.mkdir()
    out = run(key="nonexistent-9f3a", repo=str(repo))
    # Either unresolved or a stub. Both are valid; nothing crashes.
    assert "resolved" in out


def test_skill_path_uses_engine_root() -> None:
    root = engine_root()
    assert root is not None
    path = skill_path("mb-start")
    assert path is not None
    assert path == root / ".claude" / "skills" / "mb-start"
    assert "mb-think" in bundled_skills()


def test_install_mode_does_not_treat_empty_pipx_home_as_prefix(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "tmp.with.dot" / "site-packages" / "mb" / "_engine"
    monkeypatch.delenv("PIPX_HOME", raising=False)
    monkeypatch.setattr(engine_mod, "packaged_engine_root", lambda: root)
    monkeypatch.setattr(engine_mod, "source_engine_root", lambda: None)

    assert engine_mod.install_mode() == "wheel"


def _uv_engine_root(tools: Path) -> Path:
    return tools / "mainbranch" / "lib" / "python3.12" / "site-packages" / "mb" / "_engine"


def _isolate_uv_tool_roots(tmp_path: Path, monkeypatch) -> Path:
    """Point every uv tool root lookup at a fake tools dir under tmp_path."""
    tools = tmp_path / "uv" / "tools"
    monkeypatch.delenv("PIPX_HOME", raising=False)
    monkeypatch.delenv("UV_TOOL_DIR", raising=False)
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setattr(engine_mod.Path, "home", staticmethod(lambda: tmp_path / "home"))
    monkeypatch.setattr(engine_mod.sys, "executable", str(tmp_path / "elsewhere" / "python3"))
    monkeypatch.setattr(engine_mod, "source_engine_root", lambda: None)
    return tools


def test_install_mode_detects_uv_tool_install_from_uv_tool_dir(tmp_path: Path, monkeypatch) -> None:
    tools = _isolate_uv_tool_roots(tmp_path, monkeypatch)
    monkeypatch.setenv("UV_TOOL_DIR", str(tools))
    root = _uv_engine_root(tools)
    monkeypatch.setattr(engine_mod, "packaged_engine_root", lambda: root)

    assert engine_mod.install_mode() == "uv"


def test_install_mode_detects_uv_tool_install_from_xdg_data_home(
    tmp_path: Path, monkeypatch
) -> None:
    _isolate_uv_tool_roots(tmp_path, monkeypatch)
    data_home = tmp_path / "data"
    monkeypatch.setenv("XDG_DATA_HOME", str(data_home))
    root = _uv_engine_root(data_home / "uv" / "tools")
    monkeypatch.setattr(engine_mod, "packaged_engine_root", lambda: root)

    assert engine_mod.install_mode() == "uv"


def test_install_mode_detects_uv_tool_install_from_default_home_root(
    tmp_path: Path, monkeypatch
) -> None:
    _isolate_uv_tool_roots(tmp_path, monkeypatch)
    tools = tmp_path / "home" / ".local" / "share" / "uv" / "tools"
    root = _uv_engine_root(tools)
    monkeypatch.setattr(engine_mod, "packaged_engine_root", lambda: root)

    assert engine_mod.install_mode() == "uv"


def test_install_mode_detects_uv_tool_install_from_interpreter_path(
    tmp_path: Path, monkeypatch
) -> None:
    tools = _isolate_uv_tool_roots(tmp_path, monkeypatch)
    monkeypatch.setenv("UV_TOOL_DIR", str(tools))
    monkeypatch.setattr(
        engine_mod.sys,
        "executable",
        str(tools / "mainbranch" / "bin" / "python3"),
    )
    monkeypatch.setattr(engine_mod, "packaged_engine_root", lambda: tmp_path / "elsewhere" / "mb")

    assert engine_mod.install_mode() == "uv"


def test_install_mode_keeps_plain_wheel_outside_uv_tool_roots(tmp_path: Path, monkeypatch) -> None:
    tools = _isolate_uv_tool_roots(tmp_path, monkeypatch)
    monkeypatch.setenv("UV_TOOL_DIR", str(tools))
    root = tmp_path / "project" / ".venv" / "lib" / "site-packages" / "mb" / "_engine"
    monkeypatch.setattr(engine_mod, "packaged_engine_root", lambda: root)

    assert engine_mod.install_mode() == "wheel"


def test_install_mode_does_not_claim_uv_for_another_uv_tool(tmp_path: Path, monkeypatch) -> None:
    tools = _isolate_uv_tool_roots(tmp_path, monkeypatch)
    monkeypatch.setenv("UV_TOOL_DIR", str(tools))
    root = tools / "other-tool" / "lib" / "site-packages" / "mb" / "_engine"
    monkeypatch.setattr(engine_mod, "packaged_engine_root", lambda: root)

    assert engine_mod.install_mode() == "wheel"
