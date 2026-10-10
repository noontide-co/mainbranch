"""Tests for `--out PATH` on the `mb google` reads (#1004, PR8).

No network: the token and API endpoints are stub senders behind the existing
seams. The git checks use a real `git init` in a temp folder.
"""

# The fixtures are imported from test_google_connect, so test parameters
# share their names by design.
# ruff: noqa: F811, E501

from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
from pathlib import Path
from typing import Any

import pytest

from mb import google_out as go_out
from mb.cli import app
from mb.google_reads import terminal_safe
from tests.test_google_connect import (  # noqa: F401 (fixtures are used by name)
    client_file,
    google,
    google_env,
    loopback_only_network,
    repo,
    runner,
)
from tests.test_google_inspect import INSPECT_ARGS, _inspect_api
from tests.test_google_reads import (
    GA4_ARGS,
    SC_ARGS,
    SITEMAPS_ARGS,
    _assert_never_shown,
    _reads,
    _signed_in,
)

ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
READS = {
    "sc query": SC_ARGS,
    "sc sitemaps list": SITEMAPS_ARGS,
    "ga4 report": GA4_ARGS,
}
GIT_ID = ["-c", "user.name=Test", "-c", "user.email=test@example.com"]


def _git(cwd: Path, *args: str) -> None:
    env = {"HOME": str(cwd), "PATH": os.environ["PATH"], "GIT_CONFIG_NOSYSTEM": "1"}
    subprocess.run(["git", *GIT_ID, *args], cwd=cwd, env=env, check=True, capture_output=True)


TEMPLATE_GITIGNORE = (
    Path(__file__).resolve().parents[1] / "mb" / "_data" / "templates" / ".gitignore.tmpl"
)
PRIVATE_PULLS = ".mb/private/pulls"


def _checkout_with(root: Path, gitignore: str) -> Path:
    root.mkdir()
    _git(root, "init", "-q")
    (root / ".gitignore").write_text(gitignore, encoding="utf-8")
    (root / "tracked.json").write_text("{}", encoding="utf-8")
    for folder in ("docs", "exports", PRIVATE_PULLS, ".mb/pulls"):
        (root / folder).mkdir(parents=True)
    _git(root, "add", "-f", ".gitignore", "tracked.json")
    _git(root, "commit", "-q", "-m", "start")
    return root


@pytest.fixture()
def checkout(tmp_path: Path) -> Path:
    """A git checkout with the `.gitignore` that `mb init` writes (the real template)."""

    return _checkout_with(
        tmp_path / "checkout",
        TEMPLATE_GITIGNORE.read_text(encoding="utf-8") + "private/\n",
    )


@pytest.fixture()
def outdir(tmp_path: Path) -> Path:
    path = tmp_path / "pulls"
    path.mkdir()
    return path


def _out(repo: Path, args: list[str], out: Path | str, *extra: str) -> Any:
    return runner.invoke(app, [*args, "--repo", str(repo), "--out", str(out), *extra])


def _mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def _signed(repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch) -> Any:
    _signed_in(repo, client_file, google, monkeypatch)
    return _reads(monkeypatch)


# --- what is written -------------------------------------------------------------------


def test_out_writes_the_json_envelope_privately(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    outdir: Path,
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    plain = runner.invoke(app, [*SC_ARGS, "--repo", str(repo), "--json"])
    target = outdir / "queries.json"

    result = _out(repo, SC_ARGS, target)

    assert result.exit_code == 0, result.stderr
    assert len(api.calls) == 2
    assert target.read_text(encoding="utf-8").rstrip("\n") == plain.stdout.rstrip("\n")
    assert _mode(target) == 0o600
    assert result.stdout.splitlines() == [
        f"mb google sc query: wrote {target.resolve()} (mode 0600)",
        "rows: 3, may_have_more: false",
    ]
    assert list(outdir.iterdir()) == [target]
    # Nothing but the short summary reaches the terminal.
    assert '"rows"' not in result.stdout and "q0" not in result.stdout


@pytest.mark.parametrize(("name", "args"), list(READS.items()) + [("sc inspect", INSPECT_ARGS)])
def test_every_read_takes_out(
    name: str,
    args: list[str],
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    outdir: Path,
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    if name == "sc inspect":
        _inspect_api(monkeypatch)
    else:
        _reads(monkeypatch)
    target = outdir / "out.json"

    result = _out(repo, args, target)

    assert result.exit_code == 0, result.stderr
    document = json.loads(target.read_text(encoding="utf-8"))
    assert (
        document["result_schema"]["name"]
        == f"mb.google.{name.replace(' list', '').replace(' ', '.')}"
    )
    assert document["ok"] is True
    assert _mode(target) == 0o600
    # As printed: a long temp root is cut to the display cap.
    shown = terminal_safe(go_out.display_path(target), 200)
    assert f"wrote {shown}" in result.stdout


def test_summary_counts_rows_sitemaps_and_paging(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch, outdir: Path
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    _reads(monkeypatch)

    sc = _out(repo, [*SC_ARGS, "--row-limit", "3"], outdir / "a.json", "--json")
    sitemaps = _out(repo, SITEMAPS_ARGS, outdir / "b.json", "--json")
    ga4 = _out(repo, GA4_ARGS, outdir / "c.json", "--json")

    first = json.loads(sc.stdout)
    assert first["result_schema"]["name"] == "mb.google.out"
    assert (first["row_count"], first["may_have_more"], first["mode"]) == (3, True, "0600")
    assert first["out"] == str((outdir / "a.json").resolve())
    assert "rows" not in first
    assert json.loads(sitemaps.stdout)["row_count"] == 0
    assert json.loads(ga4.stdout)["row_count"] == 2


def test_nothing_secret_reaches_the_file_or_the_summary(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch, outdir: Path
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    target = outdir / "queries.json"

    result = _out(repo, SC_ARGS, target)

    assert result.exit_code == 0
    _assert_never_shown(target.read_text(encoding="utf-8"))
    _assert_never_shown(result.stdout + result.stderr)
    # The file is exactly what --json prints: no token, secret or grant is added.
    assert set(json.loads(target.read_text(encoding="utf-8"))) >= {"ok", "rows", "site"}


def test_a_failed_read_writes_nothing(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch, outdir: Path
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    _reads(monkeypatch, sc=(403, {"error": {"code": 403, "errors": [{"reason": "forbidden"}]}}))

    result = _out(repo, SC_ARGS, outdir / "x.json")

    assert result.exit_code == 1
    assert "search_console_no_access" in result.stderr
    assert list(outdir.iterdir()) == []


def test_not_connected_writes_nothing(repo: Path, outdir: Path) -> None:
    result = _out(repo, SC_ARGS, outdir / "x.json")

    assert result.exit_code == 1 and "not_connected" in result.stderr
    assert list(outdir.iterdir()) == []


def test_write_failure_leaves_nothing_behind(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    outdir: Path,
) -> None:
    _signed(repo, client_file, google, monkeypatch)

    def refuse(*_: Any, **__: Any) -> None:
        raise OSError("disk says no (synthetic)")

    monkeypatch.setattr(os, "link", refuse)

    result = _out(repo, SC_ARGS, outdir / "x.json")

    assert result.exit_code == 1 and "out_write_failed" in result.stderr
    assert "synthetic" not in result.stderr
    assert list(outdir.iterdir()) == []


# --- the refusal matrix ----------------------------------------------------------------


def _refused(result: Any, rule: str) -> None:
    assert result.exit_code == 2, result.stdout + result.stderr
    assert f"({rule})" in result.stderr
    assert "nothing was read" in result.stderr


def test_a_tracked_file_is_refused_even_with_force(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    checkout: Path,
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    before = (checkout / "tracked.json").read_bytes()

    for extra in ((), ("--force",)):
        result = _out(repo, SC_ARGS, checkout / "tracked.json", *extra)
        _refused(result, "out_path_in_repo")

    assert api.calls == []
    assert (checkout / "tracked.json").read_bytes() == before


def test_an_untracked_path_that_git_does_not_ignore_is_refused(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    checkout: Path,
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)

    for path in (checkout / "pull.json", checkout / "docs" / "pull.json"):
        _refused(_out(repo, SC_ARGS, path), "out_path_in_repo")
        assert not path.exists()

    assert api.calls == []
    assert sorted(p.name for p in checkout.iterdir() if p.is_file()) == [
        ".gitignore",
        "tracked.json",
    ]


def test_the_business_repo_itself_is_refused(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _git(repo, "init", "-q")
    api = _signed(repo, client_file, google, monkeypatch)

    _refused(_out(repo, SC_ARGS, repo / "pull.json"), "out_path_in_repo")
    # `.mb/` itself is not ignored by git, so nothing is allowed there.
    (repo / ".mb").mkdir(exist_ok=True)
    _refused(_out(repo, SC_ARGS, repo / ".mb" / "pull.json"), "out_path_in_repo")

    assert api.calls == []


@pytest.mark.parametrize("where", [f"{PRIVATE_PULLS}/pull.json", ".mb/private/pull.json"])
def test_an_ignored_path_in_a_checkout_is_allowed(
    where: str,
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    checkout: Path,
) -> None:
    _signed(repo, client_file, google, monkeypatch)

    result = _out(repo, SC_ARGS, checkout / where)

    assert result.exit_code == 0, result.stderr
    assert _mode(checkout / where) == 0o600
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=checkout, capture_output=True, text=True, check=True
    )
    assert status.stdout == ""


def test_a_path_outside_any_checkout_is_allowed(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch, outdir: Path
) -> None:
    _signed(repo, client_file, google, monkeypatch)

    assert _out(repo, SC_ARGS, outdir / "ok.json").exit_code == 0


def test_a_relative_path_is_relative_to_the_shell_folder(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    outdir: Path,
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    monkeypatch.chdir(outdir)

    assert _out(repo, SC_ARGS, "rel.json").exit_code == 0
    assert (outdir / "rel.json").is_file()


def test_an_existing_file_needs_force_and_stays_private(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    outdir: Path,
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    target = outdir / "old.json"
    target.write_text("old", encoding="utf-8")
    target.chmod(0o644)

    _refused(_out(repo, SC_ARGS, target), "out_path_exists")
    assert target.read_text(encoding="utf-8") == "old" and api.calls == []

    result = _out(repo, SC_ARGS, target, "--force")

    assert result.exit_code == 0, result.stderr
    assert json.loads(target.read_text(encoding="utf-8"))["ok"] is True
    assert _mode(target) == 0o600
    assert [p.name for p in outdir.iterdir()] == ["old.json"]


def test_a_missing_folder_is_refused_and_not_created(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch, outdir: Path
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)

    _refused(_out(repo, SC_ARGS, outdir / "nope" / "x.json"), "out_parent_missing")

    assert not (outdir / "nope").exists() and api.calls == []


def test_a_link_is_refused(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch, outdir: Path
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    real = outdir / "real.json"
    real.write_text("keep", encoding="utf-8")
    (outdir / "alias.json").symlink_to(real)
    (outdir / "dangling.json").symlink_to(outdir / "missing.json")

    for name in ("alias.json", "dangling.json"):
        for extra in ((), ("--force",)):
            _refused(_out(repo, SC_ARGS, outdir / name, *extra), "out_path_link")

    assert real.read_text(encoding="utf-8") == "keep"
    assert not (outdir / "missing.json").exists() and api.calls == []


def test_a_folder_link_into_a_checkout_is_judged_where_it_leads(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    checkout: Path,
    outdir: Path,
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    (outdir / "into-docs").symlink_to(checkout / "docs")
    (outdir / "into-private").symlink_to(checkout / PRIVATE_PULLS)

    _refused(_out(repo, SC_ARGS, outdir / "into-docs" / "x.json"), "out_path_in_repo")
    assert api.calls == []
    assert _out(repo, SC_ARGS, outdir / "into-private" / "x.json").exit_code == 0
    assert (checkout / PRIVATE_PULLS / "x.json").is_file()


def test_a_folder_is_not_a_file(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch, outdir: Path
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    (outdir / "dir").mkdir()

    for extra in ((), ("--force",)):
        _refused(_out(repo, SC_ARGS, outdir / "dir", *extra), "out_path_not_file")


def test_when_git_cannot_answer_inside_a_checkout_the_path_is_refused(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    checkout: Path,
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    real = go_out._git

    def broken(args: list[str], cwd: Path) -> Any:
        return None

    monkeypatch.setattr(go_out, "_git", broken)
    _refused(_out(repo, SC_ARGS, checkout / PRIVATE_PULLS / "x.json"), "out_path_git_unknown")

    def failing(args: list[str], cwd: Path) -> Any:
        done = real(args, cwd)
        assert done is not None
        if args[0] == "check-ignore":
            return subprocess.CompletedProcess(args, 128, b"", b"fatal")
        return done

    monkeypatch.setattr(go_out, "_git", failing)
    _refused(_out(repo, SC_ARGS, checkout / PRIVATE_PULLS / "x.json"), "out_path_git_unknown")

    assert api.calls == [] and not (checkout / PRIVATE_PULLS / "x.json").exists()


def test_git_missing_inside_a_checkout_is_refused_and_outside_is_allowed(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    checkout: Path,
    outdir: Path,
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    monkeypatch.setenv("PATH", "")  # no git to run

    _refused(_out(repo, SC_ARGS, checkout / PRIVATE_PULLS / "x.json"), "out_path_git_unknown")
    assert _out(repo, SC_ARGS, outdir / "ok.json").exit_code == 0


def test_git_index_unavailable_refuses_before_read(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    checkout: Path,
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    real = go_out._git

    def unavailable(args: list[str], cwd: Path) -> Any:
        if args[0] == "ls-files":
            return subprocess.CompletedProcess(args, 128, b"", b"fatal")
        return real(args, cwd)

    monkeypatch.setattr(go_out, "_git", unavailable)
    target = checkout / PRIVATE_PULLS / "x.json"

    _refused(_out(repo, SC_ARGS, target), "out_path_git_unknown")
    assert api.calls == [] and not target.exists()


def test_force_without_out_is_refused(repo: Path) -> None:
    result = runner.invoke(app, [*SC_ARGS, "--repo", str(repo), "--force"])

    _refused(result, "out_force_without_out")


@pytest.mark.parametrize(("raw", "rule"), [("", "out_path_invalid"), (".", "out_path_not_file")])
def test_an_empty_path_or_a_folder_is_refused(repo: Path, raw: str, rule: str) -> None:
    result = _out(repo, SC_ARGS, raw)

    assert result.exit_code == 2 and f"({rule})" in result.stderr


def test_a_refusal_is_json_with_json(repo: Path, outdir: Path) -> None:
    result = _out(repo, SC_ARGS, outdir / "nope" / "x.json", "--json")

    payload = json.loads(result.stdout)
    assert result.exit_code == 2
    assert payload["rule"] == "out_parent_missing" and payload["ok"] is False


def test_the_path_is_shown_without_terminal_escapes(repo: Path, outdir: Path) -> None:
    result = _out(repo, SC_ARGS, outdir / "no\x1b[31mpe" / "x.json")

    assert "\x1b" not in result.stderr and result.exit_code == 2


# --- the temporary file must not be committable either -----------------------------------


def _porcelain(root: Path) -> str:
    return subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def _dry_add(root: Path) -> str:
    return subprocess.run(
        ["git", "add", "-A", "--dry-run"], cwd=root, capture_output=True, text=True, check=True
    ).stdout


def test_during_a_write_git_never_sees_a_file_in_the_folder(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    checkout: Path,
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    seen: list[tuple[list[str], str, str]] = []
    real = os.fsync

    def spy(fd: int) -> None:
        folder = checkout / PRIVATE_PULLS
        seen.append(
            (sorted(p.name for p in folder.iterdir()), _porcelain(checkout), _dry_add(checkout))
        )
        real(fd)

    monkeypatch.setattr(os, "fsync", spy)

    result = _out(repo, SC_ARGS, checkout / PRIVATE_PULLS / "q.json")

    assert result.exit_code == 0, result.stderr
    names, porcelain, dry = seen[0]
    assert len(names) == 1 and names[0].endswith(".tmp")  # the temp file existed
    assert porcelain == "" and dry == ""
    assert _porcelain(checkout) == "" and _dry_add(checkout) == ""


def test_a_killed_write_leaves_nothing_git_could_commit(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    checkout: Path,
) -> None:
    _signed(repo, client_file, google, monkeypatch)

    def killed(fd: int) -> None:
        # A SIGKILL runs no cleanup: stand in by leaving the temp file behind.
        monkeypatch.setattr(os, "unlink", lambda *_a, **_k: None)
        raise OSError("killed (synthetic)")

    monkeypatch.setattr(os, "fsync", killed)
    _out(repo, SC_ARGS, checkout / PRIVATE_PULLS / "q.json")

    left = [p.name for p in (checkout / PRIVATE_PULLS).iterdir()]
    assert len(left) == 1 and left[0].endswith(".tmp")
    assert _porcelain(checkout) == "" and _dry_add(checkout) == ""


def test_the_recommended_place_works_in_a_fresh_mb_init_repo(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from mb import init as init_mod

    business = tmp_path / "fresh"
    assert (
        runner.invoke(
            app,
            [
                "init",
                str(business),
                "--name",
                "Example Co",
                "--owner-name",
                "Pat Example",
                "--owner-github",
                "pat-example",
            ],
        ).exit_code
        == 0
    )
    assert init_mod  # the real `mb init` wrote the repo's .gitignore
    _signed(repo, client_file, google, monkeypatch)
    (business / ".mb" / "private" / "pulls").mkdir(parents=True)
    (business / ".mb" / "pulls").mkdir(parents=True)

    ok = _out(repo, SC_ARGS, business / ".mb" / "private" / "pulls" / "q.json")
    refused = _out(repo, SC_ARGS, business / ".mb" / "pulls" / "q.json")

    assert ok.exit_code == 0, ok.stderr
    assert (business / ".mb" / "private" / "pulls" / "q.json").is_file()
    _refused(refused, "out_path_in_repo")
    assert ".mb/private/pulls/" in refused.stderr
    assert _porcelain(business).count("q.json") == 0


# --- the fixed matrix: ignore shapes that decide whether the temporary file is safe ------

TEMPLATE = TEMPLATE_GITIGNORE.read_text(encoding="utf-8")
ALLOW, REFUSE = "allow", "refuse"
# id -> (.gitignore, extra files {path: text}, info/exclude, global excludes, target, verdict)
SHAPES: dict[str, tuple[str, dict[str, str], str, str, str, str]] = {
    "01 dir/": ("dir/\n", {}, "", "", "dir/a.json", ALLOW),
    "02 dir": ("dir\n", {}, "", "", "dir/a.json", ALLOW),
    "03 dir/*": ("dir/*\n", {}, "", "", "dir/a.json", ALLOW),
    "04 dir/**": ("dir/**\n", {}, "", "", "dir/a.json", ALLOW),
    "05 dir/*/": ("dir/*/\n", {}, "", "", "dir/x/a.json", ALLOW),
    "06 **/pulls/": ("**/pulls/\n", {}, "", "", "sub/pulls/a.json", ALLOW),
    "07 dir/* !dir/*.tmp": ("dir/*\n!dir/*.tmp\n", {}, "", "", "dir/a.json", REFUSE),
    "08 dir/* !dir/.*": ("dir/*\n!dir/.*\n", {}, "", "", "dir/a.json", REFUSE),
    "09 dir/** !dir/**/.*.tmp": ("dir/**\n!dir/**/.*.tmp\n", {}, "", "", "dir/a.json", REFUSE),
    "10 dir/* !.*.tmp": ("dir/*\n!.*.tmp\n", {}, "", "", "dir/a.json", REFUSE),
    "11 dir/ !.*.tmp": ("dir/\n!.*.tmp\n", {}, "", "", "dir/a.json", ALLOW),
    "12 nested * !.*.tmp": ("", {"dir/.gitignore": "*\n!.*.tmp\n"}, "", "", "dir/a.json", REFUSE),
    "13 nested pulls/* !pulls/.*": (
        "",
        {"sub/.gitignore": "pulls/*\n!pulls/.*\n"},
        "",
        "",
        "sub/pulls/a.json",
        REFUSE,
    ),
    "14 nested *": ("", {"dir/.gitignore": "*\n"}, "", "", "dir/a.json", ALLOW),
    "15 report.json": ("report.json\n", {}, "", "", "report.json", REFUSE),
    "16 *.json": ("*.json\n", {}, "", "", "a.json", REFUSE),
    "17 exports/*.json": ("exports/*.json\n", {}, "", "", "exports/a.json", REFUSE),
    "18 info/exclude": ("", {}, "dir/*\n!dir/*.tmp\n", "", "dir/a.json", REFUSE),
    "19 global excludes": ("", {}, "", "dir/*\n!dir/*.tmp\n", "dir/a.json", REFUSE),
    "20 template": (TEMPLATE, {}, "", "", ".mb/private/pulls/a.json", ALLOW),
    "21 template !tmp": (
        TEMPLATE + "!.mb/private/pulls/*.tmp\n",
        {},
        "",
        "",
        ".mb/private/pulls/a.json",
        ALLOW,
    ),
    "22 template .mb/pulls": (TEMPLATE, {}, "", "", ".mb/pulls/a.json", REFUSE),
}


def _shape_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, shape: str) -> tuple[Path, str]:
    gitignore, extra, info, global_excludes, target, _ = SHAPES[shape]
    home = tmp_path / "home"
    home.mkdir()
    if global_excludes:
        (home / "excludes").write_text(global_excludes, encoding="utf-8")
        (home / ".gitconfig").write_text(
            f"[core]\n\texcludesFile = {home / 'excludes'}\n", encoding="utf-8"
        )
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    root = tmp_path / "matrix"
    root.mkdir()
    _git(root, "init", "-q")
    (root / ".gitignore").write_text(gitignore, encoding="utf-8")
    for name, text in extra.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text, encoding="utf-8")
    if info:
        (root / ".git" / "info").mkdir(exist_ok=True)
        (root / ".git" / "info" / "exclude").write_text(info, encoding="utf-8")
    (root / target).parent.mkdir(parents=True, exist_ok=True)
    _git(root, "add", "-f", "-A")
    _git(root, "commit", "-q", "-m", "start", "--allow-empty")
    return root, target


@pytest.mark.parametrize("shape", list(SHAPES))
def test_the_ignore_shape_matrix(
    shape: str,
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root, target = _shape_repo(tmp_path, monkeypatch, shape)
    verdict = SHAPES[shape][5]
    api = _signed(repo, client_file, google, monkeypatch)
    calls_before = len(api.calls)
    seen: list[tuple[str, str]] = []
    real_fsync = os.fsync

    def spy(fd: int) -> None:
        seen.append((_porcelain(root), _dry_add(root)))
        real_fsync(fd)

    monkeypatch.setattr(os, "fsync", spy)
    result = _out(repo, SC_ARGS, root / target)

    if verdict == REFUSE:
        assert result.exit_code == 2, result.stdout + result.stderr
        assert "(out_path_in_repo)" in result.stderr or "(out_temp_not_ignored)" in result.stderr
        assert "nothing was read" in result.stderr
        assert len(api.calls) == calls_before, "a refused path must not read from Google"
        assert not (root / target).exists()
        assert list(root.rglob("*mb-out.tmp")) == []
        return

    assert result.exit_code == 0, result.stderr
    # (i) during the write, the temporary file existed and git saw nothing
    assert seen and seen[0] == ("", "")
    assert (_porcelain(root), _dry_add(root)) == ("", "")
    # (ii) after a run killed mid-write, the temporary file is left and git sees nothing
    (root / target).unlink()

    def killed(fd: int) -> None:
        monkeypatch.setattr(os, "unlink", lambda *_a, **_k: None)
        raise OSError("killed (synthetic)")

    monkeypatch.setattr(os, "fsync", killed)
    _out(repo, SC_ARGS, root / target)
    left = list(root.rglob("*mb-out.tmp"))
    assert len(left) == 1 and left[0].name == f".{Path(target).name}.mb-out.tmp"
    assert (_porcelain(root), _dry_add(root)) == ("", "")


def test_an_existing_temporary_file_is_named_and_left_alone(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch, outdir: Path
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    temp = outdir / ".a.json.mb-out.tmp"
    temp.write_text("an earlier run", encoding="utf-8")

    result = _out(repo, SC_ARGS, outdir / "a.json")

    assert result.exit_code == 1
    assert "(out_write_failed)" in result.stderr and ".a.json.mb-out.tmp" in result.stderr
    assert temp.read_text(encoding="utf-8") == "an earlier run"
    assert not (outdir / "a.json").exists()


# --- follow-ups from the #1077 reviews (#1080) -------------------------------------------


def _failing_link(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(*_: Any, **__: Any) -> None:
        raise OSError("disk says no (synthetic)")

    monkeypatch.setattr(os, "link", refuse)


def test_a_write_failure_with_json_puts_the_envelope_on_stdout(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    outdir: Path,
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    _failing_link(monkeypatch)

    result = _out(repo, SC_ARGS, outdir / "x.json", "--json")

    assert result.exit_code == 1
    envelope = json.loads(result.stdout)
    assert envelope["ok"] is False and envelope["rule"] == "out_write_failed"
    assert envelope["exit_code"] == 1 and envelope["state"] == "out_write_failed"
    assert envelope["errors"][0]["code"] == "out_write_failed"
    assert envelope["safe_to_share"] is True
    assert "(out_write_failed)" in result.stderr
    assert "synthetic" not in result.stdout + result.stderr
    assert str(outdir) not in result.stdout
    assert list(outdir.iterdir()) == []


def test_a_clean_write_failure_still_says_nothing_was_left_behind(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    outdir: Path,
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    _failing_link(monkeypatch)

    result = _out(repo, SC_ARGS, outdir / "x.json")

    assert "nothing was left behind" in result.stderr


def test_a_failed_cleanup_names_the_leftover_file(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    outdir: Path,
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    _failing_link(monkeypatch)
    real_unlink = os.unlink

    def stuck(path: Any, *args: Any, **kwargs: Any) -> None:
        if str(path).endswith(".mb-out.tmp"):
            raise OSError("cannot remove (synthetic)")
        real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(os, "unlink", stuck)

    for extra in ((), ("--json",)):
        result = _out(repo, SC_ARGS, outdir / "x.json", *extra)

        assert result.exit_code == 1 and "(out_write_failed)" in result.stderr
        assert "nothing was left behind" not in result.stderr
        assert ".x.json.mb-out.tmp" in result.stderr and "remove" in result.stderr
        assert "synthetic" not in result.stdout + result.stderr
        assert str(outdir) not in result.stderr
        if extra:
            assert ".x.json.mb-out.tmp" in json.loads(result.stdout)["summary"]
        real_unlink(outdir / ".x.json.mb-out.tmp")


def _separate_git_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str = "work") -> Path:
    """A work tree with no `.git` on disk, whose repo is named by GIT_DIR/GIT_WORK_TREE."""

    work = tmp_path / name
    gitdir = tmp_path / "sep.git"
    for folder in ("open", "ignored", "elsewhere"):
        (work / folder).mkdir(parents=True)
    (tmp_path / "elsewhere").mkdir()
    env = {"HOME": str(tmp_path), "PATH": os.environ["PATH"], "GIT_DIR": str(gitdir)}
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, env=env, check=True, capture_output=True)
    (gitdir / "info").mkdir(exist_ok=True)
    (gitdir / "info" / "exclude").write_text("ignored/\n", encoding="utf-8")
    monkeypatch.setenv("GIT_DIR", str(gitdir))
    monkeypatch.setenv("GIT_WORK_TREE", str(work))
    return work


def test_an_inherited_git_dir_is_judged_too(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from mb.google_reads import ReadRefusal

    work = _separate_git_dir(tmp_path, monkeypatch)

    with pytest.raises(ReadRefusal) as refused:
        go_out.check_out(str(work / "open" / "x.json"))
    assert refused.value.rule == "out_path_in_repo"
    with pytest.raises(ReadRefusal) as refused_force:
        go_out.check_out(str(work / "open" / "x.json"), force=True)
    assert refused_force.value.rule == "out_path_in_repo"
    # Both judgments ignore this one, and this one is outside the inherited work tree.
    assert go_out.check_out(str(work / "ignored" / "x.json")).path.name == "x.json"
    assert go_out.check_out(str(tmp_path / "elsewhere" / "x.json")).path.name == "x.json"


def test_an_inherited_git_dir_refusal_reads_nothing(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    work = _separate_git_dir(tmp_path, monkeypatch)

    result = _out(repo, SC_ARGS, work / "open" / "x.json")

    _refused(result, "out_path_in_repo")
    assert api.calls == [] and not (work / "open" / "x.json").exists()


def test_a_path_mb_cannot_place_in_the_checkout_says_so(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from mb.google_reads import ReadRefusal

    (tmp_path / "Biz").mkdir()

    def elsewhere(args: list[str], cwd: Path) -> Any:
        # git names a checkout the folder cannot be mapped into (a case-variant spelling).
        return subprocess.CompletedProcess(args, 0, b"/no/such/checkout\n", b"")

    monkeypatch.setattr(go_out, "_git", elsewhere)

    with pytest.raises(ReadRefusal) as refused:
        go_out.check_out(str(tmp_path / "Biz" / "x.json"))

    assert refused.value.rule == "out_path_git_unknown"
    text = str(refused.value)
    assert "could not place" in text and "could not say" not in text
    assert "nothing was read or written" in text


def test_the_hint_states_the_path_exact_rule(checkout: Path) -> None:
    from mb.google_reads import ReadRefusal

    assert "as a whole" not in go_out.OUT_HINT
    assert ".mb-out.tmp" in go_out.OUT_HINT and ".mb/private/pulls/" in go_out.OUT_HINT
    with pytest.raises(ReadRefusal) as refused:
        go_out.check_out(str(checkout / "docs" / "x.json"))
    assert refused.value.rule == "out_path_in_repo"
    assert "as a whole" not in str(refused.value) and ".mb-out.tmp" in str(refused.value)


def test_a_path_under_home_is_shown_with_a_tilde(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    home = tmp_path / "homefolder"
    (home / "pulls").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))

    human = _out(repo, SC_ARGS, home / "pulls" / "q.json")
    as_json = _out(repo, SC_ARGS, home / "pulls" / "q2.json", "--json")

    assert human.exit_code == 0 and as_json.exit_code == 0
    assert human.stdout.splitlines()[0] == "mb google sc query: wrote ~/pulls/q.json (mode 0600)"
    info = json.loads(as_json.stdout)
    assert info["out"] == "~/pulls/q2.json"
    for text in (human.stdout, as_json.stdout):
        assert str(home) not in text and home.name not in text
    assert (home / "pulls" / "q.json").is_file() and (home / "pulls" / "q2.json").is_file()


def _case_insensitive(folder: Path) -> bool:
    probe = folder / "CaseProbe"
    probe.mkdir()
    try:
        return (folder / "caseprobe").exists()
    finally:
        probe.rmdir()


def test_a_case_variant_of_the_exported_work_tree_is_refused(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    if not _case_insensitive(tmp_path):
        pytest.skip("this disk tells apart folder names that differ only in case")
    api = _signed(repo, client_file, google, monkeypatch)
    work = _separate_git_dir(tmp_path, monkeypatch, name="Biz")

    _refused(_out(repo, SC_ARGS, work / "open" / "x.json"), "out_path_in_repo")
    result = _out(repo, SC_ARGS, tmp_path / "BIZ" / "open" / "x.json")

    _refused(result, "out_path_git_unknown")
    assert api.calls == [] and not (work / "open" / "x.json").exists()


def _unusable_text(result: Any) -> None:
    _refused(result, "out_path_git_unknown")
    assert "GIT_DIR" in result.stderr and "GIT_WORK_TREE" in result.stderr
    assert "inside a git checkout" not in result.stderr and "nothing was read" in result.stderr


@pytest.mark.parametrize("shape", ["missing_git_dir", "only_work_tree", "relative_git_dir"])
def test_an_unusable_inherited_git_env_says_so(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    outdir: Path,
    shape: str,
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    elsewhere = tmp_path / "shellfolder"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    if shape == "missing_git_dir":
        monkeypatch.setenv("GIT_DIR", str(tmp_path / "nope"))
    elif shape == "only_work_tree":
        monkeypatch.setenv("GIT_WORK_TREE", str(tmp_path))
    else:
        monkeypatch.setenv("GIT_DIR", ".git")

    _unusable_text(_out(repo, SC_ARGS, outdir / "q.json"))

    assert api.calls == [] and list(outdir.iterdir()) == []


def test_a_hook_style_relative_git_dir_judges_from_the_repo_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, checkout: Path, outdir: Path
) -> None:
    from mb.google_reads import ReadRefusal

    monkeypatch.chdir(checkout)
    monkeypatch.setenv("GIT_DIR", ".git")

    assert go_out.check_out(str(checkout / PRIVATE_PULLS / "x.json")).path.name == "x.json"
    assert go_out.check_out(str(outdir / "x.json")).path.name == "x.json"
    with pytest.raises(ReadRefusal) as refused:
        go_out.check_out(str(checkout / "docs" / "x.json"))
    assert refused.value.rule == "out_path_in_repo"


def test_a_case_variant_home_is_still_shown_with_a_tilde(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    if not _case_insensitive(tmp_path):
        pytest.skip("this disk tells apart folder names that differ only in case")
    _signed(repo, client_file, google, monkeypatch)
    (tmp_path / "Homefolder" / "pulls").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(tmp_path / "Homefolder"))

    result = _out(repo, SC_ARGS, tmp_path / "HOMEFOLDER" / "pulls" / "q.json", "--json")

    assert result.exit_code == 0
    assert json.loads(result.stdout)["out"] == "~/pulls/q.json"
    assert "omefolder" not in result.stdout.lower()


# --- help ------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "command",
    [["sc", "query"], ["sc", "sitemaps", "list"], ["sc", "inspect"], ["ga4", "report"]],
)
def test_help_shows_out_and_force(command: list[str]) -> None:
    result = runner.invoke(app, ["google", *command, "--help"], terminal_width=200)

    text = ANSI.sub("", result.stdout)
    assert result.exit_code == 0
    assert "--out" in text and "--force" in text and "0600" in text


def test_the_module_uses_no_grant_or_token_names() -> None:
    # `--out` only handles the already-shaped result; it never touches a credential.
    source = Path(go_out.__file__).read_text(encoding="utf-8")
    assert not re.search(r"access_token|refresh_token|client_secret|oauth_grant|read_token", source)


# --- follow-ups from the #1081 reviews (#1080) -------------------------------------------


def test_a_refusal_under_home_shows_a_tilde(
    repo: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    home = tmp_path / "homefolder"
    (home / "pulls").mkdir(parents=True)
    (home / "pulls" / "link.json").symlink_to(home / "pulls" / "gone.json")
    monkeypatch.setenv("HOME", str(home))

    _checkout_with(home / "checkout", TEMPLATE_GITIGNORE.read_text(encoding="utf-8"))

    # (shell folder, --out as typed, shown, rule); relative paths that lead under home too.
    for cwd, out, shown, rule in (
        (tmp_path, str(home / "nope" / "x.json"), "~/nope/x.json", "out_parent_missing"),
        (tmp_path, str(home / "pulls" / "link.json"), "~/pulls/link.json", "out_path_link"),
        (tmp_path, "homefolder/nope/x.json", "~/nope/x.json", "out_parent_missing"),
        (home / "pulls", "../../homefolder/nope/x.json", "~/nope/x.json", "out_parent_missing"),
        (tmp_path, "homefolder/checkout/docs/x.json", "~/checkout/docs/x.json", "out_path_in_repo"),
        (home, "nope/x.json", "~/nope/x.json", "out_parent_missing"),
    ):
        monkeypatch.chdir(cwd)
        human = _out(repo, SC_ARGS, out)
        as_json = _out(repo, SC_ARGS, out, "--json")

        _refused(human, rule)
        assert f"--out {shown}" in human.stderr
        payload = json.loads(as_json.stdout)
        assert payload["safe_to_share"] is True and shown in payload["summary"]
        for text in (human.stdout + human.stderr, as_json.stdout + as_json.stderr):
            assert str(home) not in text and home.name not in text

    # A relative path that does not lead under home is shown as typed.
    monkeypatch.chdir(tmp_path)
    assert "--out elsewhere/x.json:" in _out(repo, SC_ARGS, "elsewhere/x.json").stderr


def test_home_is_found_by_spelling_when_identity_cannot_be_compared(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    home = tmp_path / "homefolder"
    (home / "pulls").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))

    def unreadable(*_: Any) -> bool:
        raise PermissionError("cannot look (synthetic)")

    monkeypatch.setattr(os.path, "samefile", unreadable)

    refused = _out(repo, SC_ARGS, home / "nope" / "x.json", "--json")
    written = _out(repo, SC_ARGS, home.resolve() / "pulls" / "q.json", "--json")

    assert "~/nope/x.json" in json.loads(refused.stdout)["summary"]
    assert written.exit_code == 0 and json.loads(written.stdout)["out"] == "~/pulls/q.json"
    for text in (refused.stdout + refused.stderr, written.stdout + written.stderr):
        assert home.name not in text


def _env_text(text: str) -> None:
    assert "GIT_DIR or GIT_WORK_TREE in this shell" in text
    assert "nothing was read or written" in text


def test_a_work_tree_mb_cannot_examine_is_refused_not_counted_as_outside(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from mb.google_reads import ReadRefusal

    _separate_git_dir(tmp_path, monkeypatch)
    outside = tmp_path / "elsewhere" / "x.json"
    assert go_out.check_out(str(outside)).path.name == "x.json"

    def unreadable(*_: Any) -> bool:
        raise PermissionError("cannot look (synthetic)")

    with monkeypatch.context() as patched:
        patched.setattr(os.path, "samefile", unreadable)
        with pytest.raises(ReadRefusal) as refused:
            go_out.check_out(str(outside))
    assert refused.value.rule == "out_path_git_unknown"
    assert "could not examine that work tree" in str(refused.value)
    assert "synthetic" not in str(refused.value)

    # A work tree that is not there cannot be examined either.
    monkeypatch.setenv("GIT_WORK_TREE", str(tmp_path / "missing"))
    with pytest.raises(ReadRefusal) as missing:
        go_out.check_out(str(outside))
    assert missing.value.rule == "out_path_git_unknown"
    assert "GIT_DIR or GIT_WORK_TREE" in str(missing.value)


def test_refusals_from_the_exported_repository_say_so(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, checkout: Path
) -> None:
    from mb.google_reads import ReadRefusal

    work = _separate_git_dir(tmp_path, monkeypatch)
    exclude = tmp_path / "sep.git" / "info" / "exclude"
    exclude.write_text("ignored/\nreport.json\n", encoding="utf-8")

    for path, rule in (
        (work / "open" / "x.json", "out_path_in_repo"),
        (work / "report.json", "out_temp_not_ignored"),
    ):
        with pytest.raises(ReadRefusal) as refused:
            go_out.check_out(str(path))
        assert refused.value.rule == rule
        _env_text(str(refused.value))
    if _case_insensitive(tmp_path):
        with pytest.raises(ReadRefusal) as unplaced:
            go_out.check_out(str(tmp_path / "WORK" / "open" / "x.json"))
        assert unplaced.value.rule == "out_path_git_unknown"
        assert "could not place" in str(unplaced.value)
        _env_text(str(unplaced.value))

    # Without the variables the text is as before.
    monkeypatch.delenv("GIT_DIR")
    monkeypatch.delenv("GIT_WORK_TREE")
    with pytest.raises(ReadRefusal) as plain:
        go_out.check_out(str(checkout / "docs" / "x.json"))
    assert " is inside a git checkout and git does not ignore it, so the data" in str(plain.value)
    assert "GIT_DIR" not in str(plain.value)


def _ignored_by_git(tmp_path: Path, work: Path, file: Path) -> bool:
    env = {
        "HOME": str(tmp_path),
        "PATH": os.environ["PATH"],
        "GIT_DIR": str(tmp_path / "sep.git"),
        "GIT_WORK_TREE": str(work),
    }
    done = subprocess.run(
        ["git", "status", "--porcelain", "--ignored", "-uall"],
        cwd=work,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    relative = file.relative_to(work).as_posix()
    return f"!! {relative}" in done.stdout.splitlines()


@pytest.mark.parametrize("spelling", ["case", "firmlink"])
def test_a_work_tree_exported_in_another_spelling_allows_its_ignored_folders(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, spelling: str
) -> None:
    from mb.google_reads import ReadRefusal

    work = _separate_git_dir(tmp_path, monkeypatch, name="Biz")
    if spelling == "case":
        if not _case_insensitive(tmp_path):
            pytest.skip("this disk tells apart folder names that differ only in case")
        exported = str(tmp_path / "BIZ")
    else:
        data = Path("/System/Volumes/Data")
        real = work.resolve()
        if not data.is_dir() or not (data / str(real).lstrip("/")).is_dir():
            pytest.skip("no firmlinked data volume on this machine")
        exported = str(data) + str(real)
    monkeypatch.setenv("GIT_WORK_TREE", exported)

    target = go_out.check_out(str(work / "ignored" / "x.json"))
    target.path.write_text("{}", encoding="utf-8")
    assert _ignored_by_git(tmp_path, work, work / "ignored" / "x.json")
    with pytest.raises(ReadRefusal) as refused:
        go_out.check_out(str(work / "open" / "x.json"))
    assert refused.value.rule == "out_path_in_repo"
    assert go_out.check_out(str(tmp_path / "elsewhere" / "x.json")).path.name == "x.json"


def _checkout_ignoring_open(tmp_path: Path, ignorecase: str) -> Path:
    root = tmp_path / "cased"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "core.ignorecase", ignorecase)
    (root / "open").mkdir()
    (root / ".git" / "info" / "exclude").write_text("OPEN/\n", encoding="utf-8")
    return root


@pytest.mark.parametrize("env", [False, True])
def test_a_folder_spelled_unlike_the_disk_is_refused_with_ignorecase_false(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    env: bool,
) -> None:
    if not _case_insensitive(tmp_path):
        pytest.skip("this disk tells apart folder names that differ only in case")
    api = _signed(repo, client_file, google, monkeypatch)
    root = _checkout_ignoring_open(tmp_path, "false")
    if env:
        monkeypatch.chdir(root)
        monkeypatch.setenv("GIT_DIR", ".git")

    result = _out(repo, SC_ARGS, root / "OPEN" / "x.json")

    _refused(result, "out_path_git_unknown")
    assert "Spell the path exactly as it is on disk" in result.stderr
    assert api.calls == [] and list((root / "open").iterdir()) == []


@pytest.mark.parametrize("ignorecase", ["false", "true", "unset", "broken"])
def test_a_spelling_unlike_the_disk_is_refused_regardless_of_git_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, ignorecase: str
) -> None:
    # Runs on any disk: the disk is made to report another spelling.
    from mb.google_reads import ReadRefusal

    root = _checkout_ignoring_open(tmp_path, "false" if ignorecase == "broken" else ignorecase)
    if ignorecase == "unset":
        _git(root, "config", "--unset", "core.ignorecase")
    (root / "OPEN").mkdir(exist_ok=True)
    monkeypatch.setattr(go_out, "_spelled_as_on_disk", lambda *_: False)
    if ignorecase == "broken":
        real = go_out._git

        def no_config(args: list[str], cwd: Path, **kwargs: Any) -> Any:
            if args[0] == "config":
                return subprocess.CompletedProcess(args, 128, b"", b"fatal")
            return real(args, cwd, **kwargs)

        monkeypatch.setattr(go_out, "_git", no_config)

    with pytest.raises(ReadRefusal) as refused:
        go_out.check_out(str(root / "OPEN" / "x.json"))
    assert refused.value.rule == "out_path_git_unknown"
    assert "Spell the path exactly as it is on disk" in str(refused.value)
    assert "core.ignorecase" not in str(refused.value)


@pytest.mark.parametrize("folder", ["private", "PRIVATE"])
def test_case_variant_out_cannot_replace_a_tracked_file_on_case_insensitive_disk(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    folder: str,
) -> None:
    if not _case_insensitive(tmp_path):
        pytest.skip("this disk tells apart names that differ only in case")
    api = _signed(repo, client_file, google, monkeypatch)
    root = _checkout_with(tmp_path / "case-tracked", "private/\n")
    _git(root, "config", "core.ignorecase", "true")
    (root / "private").mkdir()
    tracked = root / "private" / "Report.json"
    original = b"personal original\n"
    tracked.write_bytes(original)
    _git(root, "add", "-f", "private/Report.json")
    _git(root, "commit", "-q", "-m", "tracked report")

    result = _out(repo, SC_ARGS, root / folder / "report.json", "--force")

    _refused(result, "out_path_git_unknown")
    assert api.calls == [] and tracked.read_bytes() == original
    assert not list((root / "private").glob(".*.mb-out.tmp"))
    diff = subprocess.run(["git", "diff", "--exit-code"], cwd=root, capture_output=True)
    assert diff.returncode == 0 and diff.stdout == b""


@pytest.mark.parametrize("folder", ["private", "PRIVATE"])
@pytest.mark.parametrize("force", [False, True])
def test_case_variant_out_refuses_an_index_only_tracked_file(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    folder: str,
    force: bool,
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    root = _checkout_with(tmp_path / "case-index-only", "private/\n")
    _git(root, "config", "core.ignorecase", "true")
    (root / "private").mkdir()
    tracked = root / "private" / "Report.json"
    tracked.write_bytes(b"personal original\n")
    _git(root, "add", "-f", "private/Report.json")
    _git(root, "commit", "-q", "-m", "tracked report")
    tracked.unlink()
    if folder == "PRIVATE" and not _case_insensitive(tmp_path):
        (root / "PRIVATE").mkdir()

    args = ("--force",) if force else ()
    result = _out(repo, SC_ARGS, root / folder / "report.json", *args)

    _refused(result, "out_path_git_unknown")
    assert "Spell the path exactly as it is on disk" in result.stderr
    assert api.calls == [] and not tracked.exists()
    assert not list((root / folder).glob(".*.mb-out.tmp"))
    status = subprocess.run(["git", "status", "--short"], cwd=root, capture_output=True, check=True)
    assert status.stdout == b" D private/Report.json\n"


def test_case_variant_out_refuses_an_index_only_tracked_file_with_missing_folders(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    root = _checkout_with(tmp_path / "missing-index-folders", "private/\n")
    _git(root, "config", "core.ignorecase", "true")
    tracked = root / "private" / "deep" / "Report.json"
    tracked.parent.mkdir(parents=True)
    tracked.write_bytes(b"personal original\n")
    _git(root, "add", "-f", "private/deep/Report.json")
    _git(root, "commit", "-q", "-m", "tracked report")
    tracked.unlink()
    tracked.parent.rmdir()
    tracked.parent.parent.rmdir()

    result = _out(repo, SC_ARGS, root / "PRIVATE" / "DEEP" / "report.json", "--force")
    exact = _out(repo, SC_ARGS, tracked, "--force")

    _refused(result, "out_path_git_unknown")
    _refused(exact, "out_parent_missing")
    assert api.calls == [] and not (root / "private").exists()
    status = subprocess.run(["git", "status", "--short"], cwd=root, capture_output=True, check=True)
    assert status.stdout == b" D private/deep/Report.json\n"


def test_unicode_variant_out_refuses_an_index_only_tracked_file(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    root = _checkout_with(tmp_path / "unicode-index-only", "private/\n")
    _git(root, "config", "core.ignorecase", "true")
    _git(root, "config", "core.precomposeunicode", "false")
    (root / "private").mkdir()
    tracked = root / "private" / "Cafe\u0301.json"
    tracked.write_bytes(b"personal original\n")
    _git(root, "add", "-f", "private/Cafe\u0301.json")
    _git(root, "commit", "-q", "-m", "tracked report")
    tracked.unlink()

    result = _out(repo, SC_ARGS, root / "private" / "Caf\u00e9.json", "--force")

    # Without `core.precomposeunicode` the two forms are not known to be one file.
    _refused(result, "out_path_git_unknown")
    assert api.calls == [] and not tracked.exists()
    assert not list((root / "private").glob(".*.mb-out.tmp"))
    status = subprocess.run(
        ["git", "status", "--short", "-z"], cwd=root, capture_output=True, check=True
    )
    assert status.stdout == " D private/Cafe\u0301.json\0".encode()


def test_exact_spelling_of_an_index_only_tracked_file_keeps_its_refusal(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    root = _checkout_with(tmp_path / "exact-index-only", "private/\n")
    (root / "private").mkdir()
    tracked = root / "private" / "Report.json"
    tracked.write_bytes(b"personal original\n")
    _git(root, "add", "-f", "private/Report.json")
    _git(root, "commit", "-q", "-m", "tracked report")
    tracked.unlink()

    result = _out(repo, SC_ARGS, tracked, "--force")

    _refused(result, "out_path_in_repo")
    assert api.calls == [] and not tracked.exists()


def test_case_variant_out_cannot_replace_an_untracked_file(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    root = _checkout_with(tmp_path / "case-untracked", "private/\n")
    _git(root, "config", "core.ignorecase", "true")
    (root / "private").mkdir()
    existing = root / "private" / "Report.json"
    original = b"untracked original\n"
    existing.write_bytes(original)

    result = _out(repo, SC_ARGS, root / "private" / "report.json", "--force")

    _refused(result, "out_path_git_unknown")
    assert api.calls == [] and existing.read_bytes() == original
    assert not list((root / "private").glob(".*.mb-out.tmp"))


@pytest.mark.parametrize("var", ["GIT_DIR", "GIT_WORK_TREE"])
def test_an_empty_git_variable_counts_as_set_as_it_does_for_git(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    outdir: Path,
    var: str,
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    shell = tmp_path / "shellfolder"
    shell.mkdir()
    monkeypatch.chdir(shell)
    monkeypatch.setenv(var, "")
    git_env = {"HOME": str(tmp_path), "PATH": os.environ["PATH"], var: ""}
    plain = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], cwd=shell, env=git_env, capture_output=True
    )
    assert plain.returncode != 0  # git itself will not run with it

    _unusable_text(_out(repo, SC_ARGS, outdir / "q.json"))

    assert api.calls == [] and list(outdir.iterdir()) == []


def test_a_temp_left_after_a_successful_write_is_named(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    outdir: Path,
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    real_unlink = os.unlink

    def stuck(path: Any, *args: Any, **kwargs: Any) -> None:
        if str(path).endswith(".mb-out.tmp"):
            raise OSError("cannot remove (synthetic)")
        real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(os, "unlink", stuck)

    human = _out(repo, SC_ARGS, outdir / "x.json")
    assert human.exit_code == 0 and (outdir / "x.json").is_file()
    assert "warning:" in human.stdout and ".x.json.mb-out.tmp" in human.stdout
    assert "remove it yourself" in human.stdout
    real_unlink(outdir / ".x.json.mb-out.tmp")

    as_json = _out(repo, SC_ARGS, outdir / "y.json", "--json")
    assert as_json.exit_code == 0
    info = json.loads(as_json.stdout)
    assert info["ok"] is True and info["safe_to_share"] is True
    assert len(info["warnings"]) == 1 and ".y.json.mb-out.tmp" in info["warnings"][0]
    assert "synthetic" not in human.stdout + human.stderr + as_json.stdout
    assert (outdir / ".y.json.mb-out.tmp").is_file()


def _stuck_unlink(monkeypatch: pytest.MonkeyPatch, error: type[OSError]) -> None:
    real_unlink = os.unlink

    def stuck(path: Any, *args: Any, **kwargs: Any) -> None:
        if str(path).endswith(".mb-out.tmp"):
            if error is FileNotFoundError:
                real_unlink(path, *args, **kwargs)  # someone else removed it first
            raise error("cannot remove (synthetic)")
        real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(os, "unlink", stuck)


def test_a_leftover_temp_name_is_printed_without_terminal_escapes(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    outdir: Path,
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    _stuck_unlink(monkeypatch, PermissionError)
    name = "x\x1b[31m.json"

    written = _out(repo, SC_ARGS, outdir / name)
    as_json = _out(repo, SC_ARGS, outdir / ("y" + name), "--json")
    _failing_link(monkeypatch)
    failed = _out(repo, SC_ARGS, outdir / ("z" + name))

    assert written.exit_code == 0 and "warning:" in written.stdout
    assert as_json.exit_code == 0
    assert failed.exit_code == 1 and "remove it yourself" in failed.stderr
    for text in (written.stdout, failed.stderr, json.loads(as_json.stdout)["warnings"][0]):
        assert "\x1b" not in text and ".mb-out.tmp" in text


def test_a_temp_already_gone_is_not_reported_as_left_behind(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    outdir: Path,
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    _stuck_unlink(monkeypatch, FileNotFoundError)

    written = _out(repo, SC_ARGS, outdir / "x.json", "--json")
    _failing_link(monkeypatch)
    failed = _out(repo, SC_ARGS, outdir / "y.json")

    assert written.exit_code == 0 and json.loads(written.stdout)["warnings"] == []
    assert failed.exit_code == 1 and "nothing was left behind" in failed.stderr
    assert "still there" not in written.stdout + failed.stderr
    assert sorted(p.name for p in outdir.iterdir()) == ["x.json"]


# --- the home folder's name never printed: a fixed corpus (#1080) -------------------------


def test_the_last_guard_hides_any_part_named_like_home(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home = tmp_path / "Homefolder"
    home.mkdir()
    (tmp_path / "homelink").symlink_to(home)
    monkeypatch.setenv("HOME", str(tmp_path / "homelink"))

    guard = go_out.hide_home_name
    assert guard("~/pulls/x.json", "x.json") == "~/pulls/x.json"
    assert guard("elsewhere/x.json", "x.json") == "elsewhere/x.json"
    # The link's name, its target's name, in any case and through terminal escapes.
    assert guard("/T/homelink/nope/x.json", "x.json") == "…/x.json"
    assert guard("/T/HOMEFOLDER/x.json", "x.json") == "…/x.json"
    assert guard("~/nope/../../homefolder/x.json", "x.json") == "~/…/x.json"
    assert guard("homefo\x1b[1mlder/x.json", "x.json") == "…/x.json"
    assert guard("/T/homefolder", "homefolder") == "…"
    # A part that only contains it is hidden too; one without it is not.
    assert guard("/T/homefolder2/x.json", "x.json") == "…/x.json"
    assert guard("~/pulls/my-homefolder.json", "my-homefolder.json") == "~/…"
    assert guard("/T/home-folder/x.json", "x.json") == "/T/home-folder/x.json"


def test_the_last_guard_for_a_short_home_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home = tmp_path / "Sam"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))

    guard = go_out.hide_home_name
    # Standing alone (a letter touches neither side): hidden, in any case.
    for hidden in ("sam", ".sam", "SAM.json", "sam-report.json", "sam2.json", "sam_x.json"):
        assert guard(f"~/pulls/{hidden}", hidden) == "~/…", hidden
    assert guard("/T/sam/x.json", "x.json") == "…/x.json"
    # Inside a longer word: shown.
    for shown in ("samples.json", "mysam.json", "wisam", "usam.json"):
        assert guard(f"~/pulls/{shown}", shown) == f"~/pulls/{shown}", shown
    # The fixed frame of a temporary name is not the name.
    assert go_out.show_temp(".samples.json.mb-out.tmp") == ".samples.json.mb-out.tmp"
    assert go_out.show_temp(".sam.json.mb-out.tmp") == ".….mb-out.tmp"
    assert go_out.show_temp(".x.mb-out.tmp") == ".x.mb-out.tmp"


# Ways to name the home folder: (shell folder, prefix) with `H` home as given, `R` its
# real path, `T` the temp root; `HOMEFOLDER` spellings run only on a case-insensitive disk.
CORPUS_PREFIXES = {
    "abs": ("T", "{H}/"),
    "abs-real": ("T", "{R}/"),
    "abs-upper": ("T", "{T}/HOMEFOLDER/"),
    "abs-link": ("T", "{T}/homelink/"),
    "abs-firmlink": ("T", "/System/Volumes/Data{R}/"),
    "abs-double-slash": ("T", "{H}//"),
    "tilde": ("T", "~/"),
    "rel-from-parent": ("T", "homefolder/"),
    "rel-upper-from-parent": ("T", "HOMEFOLDER/"),
    "rel-link-from-parent": ("T", "homelink/"),
    "rel-trailing-slashes": ("T", "homefolder//"),
    "rel-inside": ("H", ""),
    "rel-dot-inside": ("H", "./"),
    "rel-up-from-pulls": ("H/pulls", "../"),
    "rel-up-up-from-pulls": ("H/pulls", "../../homefolder/"),
    "rel-three-up-from-pulls": ("H/pulls", "../../../{Tname}/homefolder/"),
    "rel-from-root": ("/", "{Rrel}/"),
    "cwd-link": ("T/homelink", ""),
    "cwd-upper": ("T/HOMEFOLDER", ""),
    "dotdot-existing-abs": ("T", "{H}/pulls/../"),
    "dotdot-existing-rel": ("H", "pulls/../"),
    "dotdot-missing-abs": ("T", "{H}/nope/../"),
    "dotdot-missing-back-abs": ("T", "{H}/nope/../../homefolder/"),
    "dotdot-missing-rel": ("H", "nope/../../homefolder/"),
    "dotdot-missing-two-rel": ("H", "nope/nope2/../../../homefolder/"),
    "dotdot-missing-from-parent": ("T", "homefolder/nope/../../homefolder/"),
}
# What the path names below home: (suffix, expected exit code).
CORPUS_TARGETS = {
    "missing-parent": ("nope/x.json", 2),
    "link": ("pulls/link.json", 2),
    "in-checkout": ("checkout/docs/x.json", 2),
    "exists": ("pulls/exists.json", 2),
    "folder": ("pulls", 2),
    "git-folder": ("checkout/.git/x.json", 2),
    "tracked": ("checkout/tracked.json", 2),
    "allowed": ("pulls/new-{n}.json", 0),
}
CORPUS_HOMES = ["as-is", "trailing-slash", "link", "upper", "real"]


@pytest.mark.parametrize("home_kind", CORPUS_HOMES)
@pytest.mark.parametrize("prefix", list(CORPUS_PREFIXES))
def test_the_home_folder_name_is_never_printed(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    home_kind: str,
    prefix: str,
) -> None:
    upper_case = "upper" in prefix or home_kind == "upper"
    if upper_case and not _case_insensitive(tmp_path):
        pytest.skip("this disk tells apart folder names that differ only in case")
    _signed(repo, client_file, google, monkeypatch)
    home = tmp_path / "homefolder"
    (home / "pulls").mkdir(parents=True)
    (home / "pulls" / "exists.json").write_text("{}", encoding="utf-8")
    (home / "pulls" / "link.json").symlink_to(home / "pulls" / "gone.json")
    _checkout_with(home / "checkout", TEMPLATE_GITIGNORE.read_text(encoding="utf-8"))
    (tmp_path / "homelink").symlink_to(home)
    real = home.resolve()
    if prefix == "abs-firmlink" and not Path(f"/System/Volumes/Data{real}").is_dir():
        pytest.skip("no firmlinked data volume on this machine")
    monkeypatch.setenv(
        "HOME",
        {
            "as-is": str(home),
            "trailing-slash": f"{home}/",
            "link": str(tmp_path / "homelink"),
            "upper": str(tmp_path / "HOMEFOLDER"),
            "real": str(real),
        }[home_kind],
    )
    cwd, spelled = CORPUS_PREFIXES[prefix]
    folders = {"T": tmp_path, "H": home, "/": Path("/")}
    head, _, rest = cwd.partition("/")
    monkeypatch.chdir(folders[head] / rest if head in folders else Path(cwd))
    spelled = spelled.format(
        H=home, R=real, T=tmp_path, Tname=tmp_path.name, Rrel=str(real).lstrip("/")
    )

    for target, (suffix, code) in CORPUS_TARGETS.items():
        for n, extra in enumerate(((), ("--json",))):
            out = spelled + suffix.format(n=n)
            result = _out(repo, SC_ARGS, out, *extra)
            text = (result.stdout + result.stderr).lower()

            # A `..` through a missing folder leaves no folder to write in.
            expected = 2 if prefix.startswith("dotdot-missing") else code
            assert result.exit_code == expected, (target, out, result.stdout + result.stderr)
            assert "homefolder" not in text and "homelink" not in text, (target, out, text)
            if extra:
                assert json.loads(result.stdout)["safe_to_share"] is True


# Cells only the last guard can pass, through the CLI: (shell folder, --out, exit, shown).
GUARD_CELLS = {
    # A folder elsewhere named like home (a backup volume's copy, say).
    "elsewhere-named-like-home": ("T", "other/homefolder/x.json", 0, "…/x.json"),
    "elsewhere-named-like-home-missing": ("T", "other/gone/homefolder/x.json", 2, "…/x.json"),
    # The home-named part ends at character 119, where the display is cut.
    "cut-at-the-display-width": ("T", "q" * 105 + "/../homefolder/../away/x.json", 2, "…/x.json"),
}


@pytest.mark.parametrize("cell", list(GUARD_CELLS))
def test_the_guard_is_reached_through_the_cli(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    cell: str,
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    home = tmp_path / "homefolder"
    home.mkdir()
    (tmp_path / "other" / "homefolder").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(tmp_path)
    _, out, code, shown = GUARD_CELLS[cell]
    if cell == "cut-at-the-display-width":
        assert out.index("homefolder") + len("homefolder") == 119

    for n, extra in enumerate(((), ("--json",))):
        result = _out(repo, SC_ARGS, out.replace("x.json", f"x{n}.json"), *extra)
        text = result.stdout + result.stderr

        assert result.exit_code == code, text
        assert "homefolder" not in text.lower(), text
        expected = shown.replace("x.json", f"x{n}.json")
        if extra:
            payload = json.loads(result.stdout)
            assert payload["safe_to_share"] is True
            assert expected in (payload.get("out") or payload["summary"])
        else:
            assert expected in text


def test_a_dotdot_after_a_link_is_not_shown_as_a_path_under_home(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    home = tmp_path / "homefolder"
    home.mkdir()
    (tmp_path / "away" / "deep").mkdir(parents=True)
    (tmp_path / "away" / "x.json").write_text("{}", encoding="utf-8")
    (home / "linkout").symlink_to(tmp_path / "away" / "deep")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(home)

    # `linkout/..` is `away/`, not home: the file that exists is away/x.json.
    for extra in ((), ("--json",)):
        result = _out(repo, SC_ARGS, "linkout/../x.json", *extra)

        _refused(result, "out_path_exists")
        assert "~/x.json" not in result.stdout + result.stderr
        assert "--out linkout/../x.json already exists" in result.stderr
    assert not (home / "x.json").exists()


# --- a home-named file in the temp name, `~user`, existing_temp (#1080) ------------------

# File names that name the home folder, or only contain its name (`H` in another case).
TEMP_NAMES = [
    "homefolder",
    ".homefolder",
    "homefolder.json",
    "HomeFolder",
    "pull-homefolder-1.json",
]
# Every message that names the temporary file.
TEMP_MESSAGES = [
    "temp-not-ignored",
    "leftover-after-write",
    "existing-temp",
    "leftover-after-failure",
]


@pytest.mark.parametrize("home_spelling", ["as-is", "upper"])
@pytest.mark.parametrize("message", TEMP_MESSAGES)
@pytest.mark.parametrize("name", TEMP_NAMES)
def test_a_home_named_file_is_never_printed_through_its_temp(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    home_spelling: str,
    message: str,
    name: str,
) -> None:
    if home_spelling == "upper" and not _case_insensitive(tmp_path):
        pytest.skip("this disk tells apart folder names that differ only in case")
    api = _signed(repo, client_file, google, monkeypatch)
    real_unlink = os.unlink
    home = tmp_path / "homefolder"
    home.mkdir()
    monkeypatch.setenv(
        "HOME", str(tmp_path / ("HOMEFOLDER" if home_spelling == "upper" else "homefolder"))
    )
    if message == "temp-not-ignored":
        # The file is ignored, its temporary file re-included.
        folder = _checkout_with(home / "checkout", "pulls/*\n!pulls/.*.tmp\n") / "pulls"
    else:
        folder = home / "pulls"
    folder.mkdir()
    if message.startswith("leftover"):
        _stuck_unlink(monkeypatch, PermissionError)
    if message in {"existing-temp", "leftover-after-failure"}:
        _failing_link(monkeypatch)
    expected = {"temp-not-ignored": 2, "leftover-after-write": 0}.get(message, 1)
    target = folder / name
    temp = folder / go_out.temp_name(name)

    for extra in ((), ("--json",)):
        if message == "existing-temp":
            temp.write_text("an earlier run", encoding="utf-8")
        result = _out(repo, SC_ARGS, target, *extra)
        text = result.stdout + result.stderr

        assert result.exit_code == expected, text
        assert "homefolder" not in text.lower(), text
        if extra:
            payload = json.loads(result.stdout)
            assert payload["safe_to_share"] is True
            text = json.dumps(payload, ensure_ascii=False) + result.stderr
            assert "homefolder" not in text.lower(), text
        assert ".….mb-out.tmp" in text, text
        assert temp.exists() is (message != "temp-not-ignored")
        for left in (temp, target):
            if left.exists():
                real_unlink(left)
    if message == "temp-not-ignored":
        assert api.calls == []


def test_an_existing_temp_is_named_without_terminal_escapes(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch, outdir: Path
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    _failing_link(monkeypatch)

    for n, extra in enumerate(((), ("--json",))):
        name = f"x{n}\x1b[31m.json"
        (outdir / go_out.temp_name(name)).write_text("an earlier run", encoding="utf-8")
        result = _out(repo, SC_ARGS, outdir / name, *extra)

        assert result.exit_code == 1 and "(out_write_failed)" in result.stderr
        assert "is already there" in result.stderr
        assert "\x1b" not in result.stdout + result.stderr
        assert f".x{n}.json.mb-out.tmp" in result.stderr
        if extra:
            assert "\x1b" not in json.loads(result.stdout)["summary"]


def _users(monkeypatch: pytest.MonkeyPatch, known: dict[str, Path]) -> None:
    """`~name` knows only the users given here, whatever this computer has."""

    import pwd

    real = pwd.getpwnam

    def getpwnam(name: str) -> Any:
        if name in known:
            entry = list(real("root"))
            entry[5] = str(known[name])
            return pwd.struct_passwd(entry)
        raise KeyError(name)

    monkeypatch.setattr(pwd, "getpwnam", getpwnam)


def test_an_unknown_user_is_refused_cleanly(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    _users(monkeypatch, {})

    human = _out(repo, SC_ARGS, "~unknownuser/x.json")
    as_json = _out(repo, SC_ARGS, "~unknownuser/x.json", "--json")

    for result in (human, as_json):
        _refused(result, "out_user_unknown")
        assert "unexpected error" not in result.stdout + result.stderr
        assert "~unknownuser names a user this computer does not know" in result.stderr
        assert "nothing was read or written" in result.stderr
    payload = json.loads(as_json.stdout)
    assert payload["rule"] == "out_user_unknown" and payload["safe_to_share"] is True
    assert "~unknownuser/x.json" in payload["summary"]
    assert api.calls == []


def test_another_users_home_is_shown_as_typed(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    other = tmp_path / "alexhome"
    (other / "pulls").mkdir(parents=True)
    _users(monkeypatch, {"alex": other})

    written = _out(repo, SC_ARGS, "~alex/pulls/x.json")
    as_json = _out(repo, SC_ARGS, "~alex/pulls/y.json", "--json")
    refused = _out(repo, SC_ARGS, "~alex/nope/x.json", "--json")

    assert written.exit_code == 0 and (other / "pulls" / "x.json").is_file()
    assert "wrote ~alex/pulls/x.json (mode 0600)" in written.stdout
    assert as_json.exit_code == 0 and json.loads(as_json.stdout)["out"] == "~alex/pulls/y.json"
    _refused(refused, "out_parent_missing")
    assert "--out ~alex/nope/x.json" in refused.stderr
    for result in (written, as_json, refused):
        assert "alexhome" not in result.stdout + result.stderr


# --- follow-ups from the #1107 and #1115 reviews (#1080) --------------------------------


def test_your_own_user_name_is_shown_like_a_tilde(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    home = tmp_path / "alexhome"
    (home / "pulls").mkdir(parents=True)
    (tmp_path / "samehome").symlink_to(home)
    monkeypatch.setenv("HOME", str(home))
    # `alex` is you; `kim` is another user name for the same folder; `eve` is someone else.
    other = tmp_path / "evehome"
    (other / "pulls").mkdir(parents=True)
    _users(monkeypatch, {"alex": home, "kim": tmp_path / "samehome", "eve": other})

    for user in ("alex", "kim"):
        written = _out(repo, SC_ARGS, f"~{user}/pulls/x.json")
        as_json = _out(repo, SC_ARGS, f"~{user}/pulls/y.json", "--json")
        refused = _out(repo, SC_ARGS, f"~{user}/nope/x.json", "--json")
        exists = _out(repo, SC_ARGS, f"~{user}/pulls/x.json")

        assert "wrote ~/pulls/x.json (mode 0600)" in written.stdout
        assert as_json.exit_code == 0 and json.loads(as_json.stdout)["out"] == "~/pulls/y.json"
        _refused(refused, "out_parent_missing")
        assert "--out ~/nope/x.json" in json.loads(refused.stdout)["summary"]
        _refused(exists, "out_path_exists")
        assert "--out ~/pulls/x.json already exists" in exists.stderr
        for result in (written, as_json, refused, exists):
            assert "…" not in result.stdout + result.stderr
            assert "alexhome" not in result.stdout + result.stderr
        for name in ("x.json", "y.json"):
            (home / "pulls" / name).unlink()
    # Another user's home is still never shown as a path.
    elsewhere = _out(repo, SC_ARGS, "~eve/pulls/x.json")
    assert "wrote ~eve/pulls/x.json (mode 0600)" in elsewhere.stdout
    assert "evehome" not in elsewhere.stdout + elsewhere.stderr


def test_a_home_folder_that_cannot_be_found_is_refused_clearly(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import pwd

    api = _signed(repo, client_file, google, monkeypatch)
    monkeypatch.delenv("HOME", raising=False)

    def no_entry(_: int) -> Any:
        raise KeyError("no passwd entry")

    monkeypatch.setattr(pwd, "getpwuid", no_entry)
    here = tmp_path / "here"
    here.mkdir()
    monkeypatch.chdir(here)

    human = _out(repo, SC_ARGS, "~/x.json")
    as_json = _out(repo, SC_ARGS, "~/x.json", "--json")
    bare = _out(repo, SC_ARGS, "~")

    for result in (human, as_json, bare):
        _refused(result, "out_home_not_found")
        text = result.stdout + result.stderr
        assert "unexpected error" not in text and "does not know" not in text
        assert "the home folder cannot be found" in result.stderr
    payload = json.loads(as_json.stdout)
    assert payload["rule"] == "out_home_not_found" and payload["exit_code"] == 2
    assert payload["safe_to_share"] is True and "--out ~/x.json" in payload["summary"]
    assert api.calls == [] and not list(here.iterdir())


def test_a_user_name_is_still_unknown_when_home_is_missing(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    _users(monkeypatch, {})

    result = _out(repo, SC_ARGS, "~nobody/x.json")

    _refused(result, "out_user_unknown")
    assert api.calls == []


def _nfd_tracked(tmp_path: Path) -> Path:
    """A checkout whose index holds ``Café.json`` in NFC while the disk lists it in NFD."""

    root = _checkout_with(tmp_path / "form-only", "private/\n")
    _git(root, "config", "core.precomposeunicode", "true")
    (root / "private").mkdir()
    tracked = root / "private" / "Cafe\u0301.json"
    tracked.write_bytes(b"personal original\n")
    _git(root, "add", "-f", "private/Cafe\u0301.json")
    _git(root, "commit", "-q", "-m", "tracked report")
    listed = subprocess.run(
        ["git", "ls-files", "-z", "private"], cwd=root, capture_output=True, check=True
    ).stdout
    if listed != "private/Caf\u00e9.json\0".encode() or "Cafe\u0301.json" not in os.listdir(
        root / "private"
    ):
        pytest.skip("this git and disk do not store the index name in NFC while listing NFD")
    return root


@pytest.mark.parametrize("force", [False, True])
def test_a_tracked_file_in_another_unicode_form_is_the_tracked_path_refusal(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    force: bool,
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    root = _nfd_tracked(tmp_path)
    name = "Cafe\u0301.json"
    extra = ("--force",) if force else ()

    for more in ((), ("--json",)):
        result = _out(repo, SC_ARGS, root / "private" / name, *extra, *more)

        _refused(result, "out_path_in_repo")
        assert "git does not ignore it" in result.stderr
        assert "spelled differently" not in result.stdout + result.stderr
    assert api.calls == []
    assert (root / "private" / "Cafe\u0301.json").read_bytes() == b"personal original\n"
    assert not list((root / "private").glob(".*.mb-out.tmp"))
    status = subprocess.run(
        ["git", "status", "--short"], cwd=root, capture_output=True, check=True
    ).stdout
    assert status == b""


def test_a_form_difference_with_a_missing_folder_is_the_tracked_path_refusal(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    root = _nfd_tracked(tmp_path)
    shutil.rmtree(root / "private")

    result = _out(repo, SC_ARGS, root / "private" / "Cafe\u0301.json")

    _refused(result, "out_path_in_repo")
    assert api.calls == [] and not (root / "private").exists()


def test_the_index_spelling_against_the_disk_spelling_keeps_its_advice(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # The name as git stores it (NFC) is not how the disk lists the file (NFD): the
    # advice "spell it exactly as on disk" is the one that helps.
    api = _signed(repo, client_file, google, monkeypatch)
    root = _nfd_tracked(tmp_path)

    result = _out(repo, SC_ARGS, root / "private" / "Caf\u00e9.json")

    _refused(result, "out_path_git_unknown")
    assert api.calls == []


def test_a_form_and_case_difference_stays_the_spelling_refusal(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    root = _nfd_tracked(tmp_path)

    result = _out(repo, SC_ARGS, root / "private" / "CAFE\u0301.json")

    _refused(result, "out_path_git_unknown")
    assert api.calls == []


# --- short home names: hidden only where they stand alone (#1080) ------------------------
#
# The rule: a home name of five letters or more is hidden wherever a path part contains
# it (as before). A name of four or fewer is hidden only where no letter touches it, so
# `sam.json`, `.sam`, `sam-report.json`, `sam2.json` and `sam_x.json` are hidden but
# `samples.json` and `mysam.json` still show. Why this is still safe: the guard exists so
# the home name is not printed as a name, and a part with a letter against it reads as a
# longer word; every #1097/#1107 case is either a long name (still hidden by containment)
# or a name standing alone (still hidden). The fixed `.mb-out.tmp` frame is not checked.
# Known residual: names are compared folded, so a camelCase part (`reportForSam.json`)
# prints `Sam`, which a letter touches on one side; it is display-only.

# Test ids stay neutral on purpose: pytest puts them into the temp folder's name.
SHORT_HOMES = {"h3": "sam", "h4": "alex", "h8": "homefolder"}
# (file name template, hidden for a short home, hidden for a long home); `{h}` home name.
SHORT_NAMES = {
    "exact": ("{h}", True, True),
    "dot": (".{h}", True, True),
    "json": ("{h}.json", True, True),
    "report": ("{h}-report.json", True, True),
    "case": ("{U}.json", True, True),
    "digit": ("{h}2.json", True, True),
    "tail": ("{h}ples.json", False, True),
    "head": ("my{h}.json", False, True),
}
SHORT_MESSAGES = {
    "summary": 0,
    "exists": 2,
    "temp-not-ignored": 2,
    "leftover-after-write": 0,
    "existing-temp": 1,
    "leftover-after-failure": 1,
}


def _standalone(name: str, text: str) -> bool:
    """Whether ``name`` stands in ``text`` with no letter against it."""

    return re.search(rf"(?<![^\W\d_]){re.escape(name)}(?![^\W\d_])", text.lower()) is not None


# The upper-case spelling of the home folder runs for three file names only.
SHORT_CASES = [
    (home_id, kind, message, spelling)
    for spelling in ("as-is", "upper")
    for message in SHORT_MESSAGES
    for kind in SHORT_NAMES
    for home_id in SHORT_HOMES
    if spelling == "as-is" or kind in {"exact", "report", "tail"}
]


@pytest.mark.parametrize(("home_id", "kind", "message", "home_spelling"), SHORT_CASES)
def test_a_short_home_name_is_hidden_only_where_it_stands_alone(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    home_id: str,
    kind: str,
    message: str,
    home_spelling: str,
) -> None:
    if home_spelling == "upper" and not _case_insensitive(tmp_path):
        pytest.skip("this disk tells apart folder names that differ only in case")
    api = _signed(repo, client_file, google, monkeypatch)
    real_unlink = os.unlink
    home_name = SHORT_HOMES[home_id]
    template, hidden_short, hidden_long = SHORT_NAMES[kind]
    name = template.format(h=home_name, U=home_name.upper())
    hidden = hidden_short if len(home_name) <= 4 else hidden_long
    home = tmp_path / home_name
    home.mkdir()
    monkeypatch.setenv(
        "HOME", str(tmp_path / (home_name.upper() if home_spelling == "upper" else home_name))
    )
    if message == "temp-not-ignored":
        folder = _checkout_with(home / "checkout", "pulls/*\n!pulls/.*.tmp\n") / "pulls"
        base = "~/checkout/pulls/"
    else:
        folder = home / "pulls"
        base = "~/pulls/"
    folder.mkdir()
    if message.startswith("leftover"):
        _stuck_unlink(monkeypatch, PermissionError)
    if message in {"existing-temp", "leftover-after-failure"}:
        _failing_link(monkeypatch)
    target = folder / name
    temp = folder / go_out.temp_name(name)
    where = base + name if not hidden else "~/…"
    temp_shown = go_out.temp_name(name) if not hidden else ".….mb-out.tmp"
    expected_text = {
        "summary": f"wrote {where} (mode 0600)",
        "exists": f"--out {where} already exists",
        "temp-not-ignored": f"--out {where}: inside a git checkout git must ignore both the file "
        f"and its temporary file {temp_shown}",
        "leftover-after-write": f"the temporary file {temp_shown} could not be removed",
        "existing-temp": f"{temp_shown} is already there",
        "leftover-after-failure": f"the temporary file {temp_shown} could not be removed",
    }[message]

    for extra in ((), ("--json",)):
        if message == "exists":
            target.write_text("{}", encoding="utf-8")
        if message == "existing-temp":
            temp.write_text("an earlier run", encoding="utf-8")
        result = _out(repo, SC_ARGS, target, *extra)
        text = result.stdout + result.stderr
        assert result.exit_code == SHORT_MESSAGES[message], text
        if extra:
            payload = json.loads(result.stdout)
            assert payload["safe_to_share"] is True
            text = json.dumps(payload, ensure_ascii=False) + result.stderr
            if message in {"summary", "leftover-after-write"}:
                assert payload["out"] == where, text
        folded = text.lower()
        # Exactly what is hidden: the expected text is there, no full home path is,
        # and the home name never stands alone.
        expected = expected_text if not extra or message not in {"summary"} else where
        assert expected in text, (expected, text)
        assert str(home).lower() not in folded and str(home.resolve()).lower() not in folded
        assert not _standalone(home_name, text), text
        if hidden:
            assert name.lower() not in folded or kind in {"exact", "dot"}, text
            if len(home_name) > 4:
                assert home_name not in folded, text
        else:
            assert name in text, text
        for left in (temp, target):
            if left.exists():
                real_unlink(left)
    if message == "temp-not-ignored":
        assert api.calls == []


@pytest.mark.parametrize("cut", ["refusal-120", "summary-200"])
def test_a_cut_cannot_leave_a_short_home_name_standing_alone(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    cut: str,
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    home = tmp_path / "sam"
    (home / "pulls").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))
    # `samples.json` is shown whole, but the display cut lands right after `sam`.
    width = 120 if cut == "refusal-120" else 200
    prefix = "~/pulls/"
    padding = "x" * (width - 1 - len(prefix) - len("sam") - 1)
    name = f"{padding}-samples.json"
    assert (prefix + name)[: width - 1].endswith("-sam")
    if cut == "refusal-120":
        (home / "pulls" / name).write_text("{}", encoding="utf-8")

    result = _out(repo, SC_ARGS, home / "pulls" / name)
    text = result.stdout + result.stderr

    assert result.exit_code == (2 if cut == "refusal-120" else 0), text
    assert "sam…" not in text and not _standalone("sam", text), text
    # The part is guarded again after the cut: the folder is shown as `~/…/`, then the name.
    assert "~/…/" + padding[:50] in text, text


# --- follow-ups from the #1130 review (#1080) -------------------------------------------


@pytest.mark.parametrize(
    ("platform", "wording"),
    [
        ("darwin", "out_path_in_repo"),
        ("linux", "out_path_git_unknown"),
        ("win32", "out_path_git_unknown"),
    ],
)
def test_the_unicode_form_wording_applies_only_where_git_precomposes(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    platform: str,
    wording: str,
) -> None:
    api = _signed(repo, client_file, google, monkeypatch)
    root = _nfd_tracked(tmp_path)
    monkeypatch.setattr("sys.platform", platform)

    for more in ((), ("--json",)):
        result = _out(repo, SC_ARGS, root / "private" / "Café.json", "--force", *more)

        _refused(result, wording)
    assert api.calls == []
    assert (root / "private" / "Café.json").read_bytes() == b"personal original\n"
    assert not list((root / "private").glob(".*.mb-out.tmp"))


@pytest.mark.parametrize("home_name", ["Sam", "homefolder"])
@pytest.mark.parametrize("shown_length", [118, 119, 120, 121, 125, 126, 127, 130, 200])
def test_a_reguarded_path_stays_within_its_limit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, home_name: str, shown_length: int
) -> None:
    home = tmp_path / home_name
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    lower = home_name.lower()
    # Where the display cut lands right after the home name (`...-sam…`), so the cut is
    # judged again; the old result then ran 2 characters over (`…/` plus a 120-character name).
    for tail in ("ples.json", "-1.json"):
        name = "x" * (shown_length - len(tail) - len(lower) - 1) + "-" + lower + tail
        raw = f"/T/{lower}/{name}"

        shown = go_out._shown(raw)

        assert len(shown) <= 120, (len(shown), shown)
        assert not go_out._holds_home_name(shown), shown
        info = {
            "out": go_out.hide_home_name(raw, name),
            "mode": "0600",
            "source_command": "c",
            "row_count": 0,
        }
        info["may_have_more"] = False
        wrote = go_out.render_summary(info)[0].split(" wrote ", 1)[1].rsplit(" (mode", 1)[0]
        assert len(wrote) <= 200 and not go_out._holds_home_name(wrote), wrote


@pytest.mark.parametrize("prefix_source", ["~/pulls/x/sam", "/T/sam/x"])
@pytest.mark.parametrize("limit", [4, 5, 6, 10, 120])
def test_the_last_guard_keeps_its_result_within_a_limit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, prefix_source: str, limit: int
) -> None:
    home = tmp_path / "sam"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    name = "abcdefghijklmnopqrstuvwxyz" * 6
    guarded = go_out.hide_home_name(f"{prefix_source}/{name}", name, limit)

    assert len(guarded) <= limit, guarded
    # A cut that leaves the name standing alone is hidden, not shown.
    assert go_out.hide_home_name("/T/sam/x", "samples.json", 6) == "…"


def test_another_users_home_reached_through_dotdot_is_shown_as_typed(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _signed(repo, client_file, google, monkeypatch)
    mine = tmp_path / "myhome"
    mine.mkdir()
    monkeypatch.setenv("HOME", str(mine))
    (tmp_path / "samfolder").mkdir()
    (tmp_path / "bobhome" / "pulls").mkdir(parents=True)
    _users(monkeypatch, {"sam": tmp_path / "samfolder", "me": mine})
    typed = "~sam/../bobhome/pulls/a.json"

    written = _out(repo, SC_ARGS, typed)
    as_json = _out(repo, SC_ARGS, "~sam/../bobhome/pulls/b.json", "--json")

    assert written.exit_code == 0 and (tmp_path / "bobhome" / "pulls" / "a.json").is_file()
    assert f"wrote {typed} (mode 0600)" in written.stdout
    assert json.loads(as_json.stdout)["out"] == "~sam/../bobhome/pulls/b.json"
    for result in (written, as_json):
        assert str(tmp_path) not in result.stdout + result.stderr
    # Back into your own home it is still `~/...`.
    own = _out(repo, SC_ARGS, "~sam/../myhome/x.json", "--json")
    assert own.exit_code == 0 and json.loads(own.stdout)["out"] == "~/x.json"
    # Your own user name leaving your home does the same.
    out = _out(repo, SC_ARGS, "~me/../bobhome/pulls/c.json", "--json")
    assert out.exit_code == 0, out.stderr
    assert json.loads(out.stdout)["out"] == "~me/../bobhome/pulls/c.json"
    # A folder outside every home is shown as typed too.
    (tmp_path / "plain").mkdir()
    plain = _out(repo, SC_ARGS, "~sam/../plain/d.json", "--json")
    assert plain.exit_code == 0
    assert json.loads(plain.stdout)["out"] == "~sam/../plain/d.json"
