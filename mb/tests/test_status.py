"""``mb status`` daily briefing."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import date, datetime
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from mb import status as status_mod
from mb.cli import app
from mb.init import run as init_run

runner = CliRunner()


def _without_github_or_claude(name: str) -> str:
    if name in {"gh", "claude"}:
        return ""
    return shutil.which(name) or ""


def test_status_json_degrades_without_github(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    (repo / "decisions" / "2026-05-01-pricing.md").write_text(
        "---\ndate: 2026-05-01\nstatus: accepted\n---\n\n# Pricing\n",
        encoding="utf-8",
    )
    (repo / "research" / "2026-05-01-market.md").write_text(
        "---\ndate: 2026-05-01\nsource: desk\n---\n\n# Market\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["status", str(repo), "--json"])

    assert result.exit_code == 0
    report = json.loads(result.stdout)
    assert report["repo"]["looks_like_mainbranch_repo"] is True
    assert report["runtime"]["skill_wiring"]["ok"] is True
    assert report["github"]["authenticated"] is False
    assert report["brain"]["counts"]["decisions"] == 1
    assert report["brain"]["recent_research"][0]["title"] == "Market"
    assert "readiness" in report


def test_status_human_output_mentions_core_sections(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")

    result = runner.invoke(app, ["status", str(repo)])

    assert result.exit_code == 0
    assert "mb status" in result.stdout
    assert "Repo" in result.stdout
    assert "Runtime" in result.stdout
    assert "GitHub" in result.stdout
    assert "Next" in result.stdout


def test_status_detects_non_business_repo(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    report = status_mod.run(path=str(tmp_path))

    assert report["repo"]["looks_like_mainbranch_repo"] is False
    assert report["readiness"]["level"] == "not_ready"
    assert any("mb init" in action for action in report["readiness"]["next_actions"])


def test_status_low_level_helpers_handle_edge_cases(tmp_path: Path, monkeypatch) -> None:
    assert status_mod._repo_full_name("git@github.com:noontide-co/mainbranch.git") == (
        "noontide-co/mainbranch"
    )
    assert status_mod._repo_full_name("https://github.com/noontide-co/mainbranch.git") == (
        "noontide-co/mainbranch"
    )
    assert status_mod._repo_full_name("https://github.com/noontide-co/some.io.git") == (
        "noontide-co/some.io"
    )
    assert status_mod._repo_full_name("") == ""

    missing = tmp_path / "missing.md"
    plain = tmp_path / "plain.md"
    plain.write_text("# Plain\n", encoding="utf-8")
    unclosed = tmp_path / "unclosed.md"
    unclosed.write_text("---\nstatus: proposed\n", encoding="utf-8")
    bad_yaml = tmp_path / "bad.md"
    bad_yaml.write_text("---\n:\n---\n", encoding="utf-8")

    assert status_mod._read_frontmatter(missing) == {}
    assert status_mod._read_frontmatter(plain) == {}
    assert status_mod._read_frontmatter(unclosed) == {}
    assert status_mod._read_frontmatter(bad_yaml) == {}

    assert status_mod._parse_date(datetime(2026, 5, 2, 8, 30), plain) == date(2026, 5, 2)
    assert status_mod._parse_date(date(2026, 5, 2), plain) == date(2026, 5, 2)
    assert status_mod._parse_date("not-a-date", tmp_path / "2026-05-01-note.md") == date(2026, 5, 1)
    assert status_mod._parse_date("not-a-date", tmp_path / "note.md") is None

    external = tmp_path / "external.md"
    external.write_text("no heading\n", encoding="utf-8")
    summary = status_mod._file_summary(tmp_path / "repo", external)
    assert summary["path"] == str(external)
    assert summary["title"] == "external"

    def raise_missing(*args: object, **kwargs: object) -> object:
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", raise_missing)
    assert status_mod._run_command(["missing-bin"])["returncode"] == 127

    def raise_timeout(*args: object, **kwargs: object) -> object:
        raise subprocess.TimeoutExpired(cmd="slow", timeout=1)

    monkeypatch.setattr(subprocess, "run", raise_timeout)
    assert status_mod._run_command(["slow"])["returncode"] == 124

    def raise_subprocess(*args: object, **kwargs: object) -> object:
        raise subprocess.SubprocessError("boom")

    monkeypatch.setattr(subprocess, "run", raise_subprocess)
    assert status_mod._run_command(["boom"])["stderr"] == "boom"


def test_status_git_activity_parser_and_failure(tmp_path: Path, monkeypatch) -> None:
    def fake_run_command(
        args: list[str], cwd: Path | None = None, timeout: float = 3.0
    ) -> dict[str, Any]:
        assert args[1] == "log"
        return {
            "ok": True,
            "stdout": (
                "abc123\t2026-05-02\tUpdate offer\n"
                "core/offer.md\n"
                "research/2026-05-01-market.md\n\n"
                "def456\t2026-05-01\tAdd decision\n"
                "decisions/2026-05-01-pricing.md\n"
            ),
            "stderr": "",
        }

    monkeypatch.setattr(status_mod, "_run_command", fake_run_command)
    activity = status_mod._git_recent_activity(tmp_path, {"inside_work_tree": True})

    assert activity["available"] is True
    assert activity["items"][0]["commit"] == "abc123"
    assert activity["items"][0]["files"] == [
        "core/offer.md",
        "research/2026-05-01-market.md",
    ]
    assert activity["items"][1]["subject"] == "Add decision"
    assert (
        status_mod._git_recent_activity(tmp_path, {"inside_work_tree": False, "error": "no git"})[
            "error"
        ]
        == "no git"
    )

    monkeypatch.setattr(
        status_mod,
        "_run_command",
        lambda args, cwd=None, timeout=3.0: {"ok": False, "stdout": "", "stderr": "bad log"},
    )
    assert (
        status_mod._git_recent_activity(tmp_path, {"inside_work_tree": True})["error"] == "bad log"
    )


def test_status_brain_marks_stale_decisions(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    decisions = repo / "decisions"
    decisions.mkdir(parents=True)
    old_date = date.today().replace(year=date.today().year - 1)
    (decisions / f"{old_date.isoformat()}-old.md").write_text(
        f"---\ndate: {old_date.isoformat()}\nstatus: proposed\n---\n\n# Old proposal\n",
        encoding="utf-8",
    )
    (repo / "research").mkdir()
    (repo / "research" / "2026-05-01-market.md").write_text("# Market\n", encoding="utf-8")

    brain = status_mod._brain(repo)

    assert brain["recent_decisions"][0]["title"] == "Old proposal"
    assert brain["stale_decisions"][0]["age_days"] > status_mod.STALE_DECISION_DAYS
    assert brain["recent_research"][0]["title"] == "Market"


def test_status_github_authenticated_branches(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", lambda name: "/usr/bin/gh" if name == "gh" else "")
    monkeypatch.setattr(
        status_mod,
        "_run_command",
        lambda args, cwd=None, timeout=3.0: {"ok": True, "stdout": "", "stderr": ""},
    )

    def fake_gh_json(args: list[str], repo: Path) -> tuple[bool, Any, str]:
        if args[1:3] == ["issue", "list"]:
            return True, [{"number": 173, "title": "Status", "url": "u"}], ""
        if args[1:3] == ["pr", "list"] and "--search" in args:
            return False, None, "search failed"
        return (
            True,
            [{"number": 192, "title": "Briefing", "body": "## Scope\n- Shipped status"}],
            "",
        )

    monkeypatch.setattr(status_mod, "_gh_json", fake_gh_json)
    github = status_mod._github(
        tmp_path,
        {"remote": "https://github.com/noontide-co/mainbranch.git"},
    )

    assert github["authenticated"] is True
    assert github["repo"] == "noontide-co/mainbranch"
    assert github["assigned_issues"][0]["number"] == 173
    assert github["recent_merged_prs"][0]["what_shipped"] == "Shipped status"
    assert github["errors"] == ["review requests: search failed"]

    assert (
        status_mod._summarize_pr({"title": "Fallback title", "body": "# Heading"})["what_shipped"]
        == "Fallback title"
    )

    monkeypatch.setattr(
        status_mod,
        "_run_command",
        lambda args, cwd=None, timeout=3.0: {"ok": False, "stdout": "", "stderr": "no auth"},
    )
    assert status_mod._github(tmp_path, {"remote": ""})["authenticated"] is False


def test_status_renderer_prints_optional_sections(capsys) -> None:
    report: dict[str, Any] = {
        "repo": {"path": "/tmp/biz", "looks_like_mainbranch_repo": True},
        "install": {"detail": "mb 0.1.2 (wheel mode)"},
        "runtime": {
            "claude_code": {"found": True},
            "skill_wiring": {"ok": True},
        },
        "git": {"inside_work_tree": False, "dirty": False, "error": "not a git work tree"},
        "brain": {
            "counts": {
                "core": 1,
                "reference/core": 1,
                "research": 1,
                "decisions": 1,
                "campaigns": 1,
                "log": 1,
                "documents": 1,
            },
            "recent_decisions": [
                {"date": "2026-05-01", "updated_at": "", "title": "Pricing", "status": "accepted"}
            ],
            "stale_decisions": [
                {"path": "decisions/old.md", "age_days": 30},
            ],
            "recent_research": [
                {"date": "2026-05-01", "updated_at": "", "title": "Market"},
            ],
        },
        "git_activity": {
            "items": [
                {
                    "date": "2026-05-02",
                    "commit": "abc123",
                    "subject": "Update brain",
                    "files": ["core/offer.md", "research/a.md", "decisions/b.md"],
                }
            ]
        },
        "github": {
            "available": True,
            "authenticated": True,
            "assigned_issues": [{"number": 173, "title": "Status"}],
            "review_requests": [],
            "recent_merged_prs": [{"number": 192, "what_shipped": "Daily briefing"}],
            "errors": ["merged PRs: degraded"],
        },
        "readiness": {"level": "ready", "score": 100, "next_actions": ["Run `claude`."]},
    }

    status_mod.render_human(report)

    output = capsys.readouterr().out
    assert "Recent decisions" in output
    assert "Stale proposed/running decisions" in output
    assert "Recent research" in output
    assert "Recent git activity" in output
    assert "issue #173" in output
    assert "shipped #192" in output
