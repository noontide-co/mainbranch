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
import stat
import subprocess
from pathlib import Path
from typing import Any

import pytest

from mb import google_out as go_out
from mb.cli import app
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
    assert f"wrote {target.resolve()}" in result.stdout


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
def test_ignorecase_false_refuses_a_folder_spelled_unlike_the_disk(
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
    assert "core.ignorecase" in result.stderr and "spelled differently" in result.stderr
    assert api.calls == [] and list((root / "open").iterdir()) == []


@pytest.mark.parametrize(
    ("ignorecase", "seen"),
    [
        ("false", "sets core.ignorecase to false"),
        ("true", ""),
        ("unset", "does not set core.ignorecase (git then treats it as false)"),
        ("broken", "did not let mb read core.ignorecase"),
    ],
)
def test_a_spelling_unlike_the_disk_is_judged_by_core_ignorecase(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, ignorecase: str, seen: str
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

    if ignorecase == "true":
        assert go_out.check_out(str(root / "OPEN" / "x.json")).path.name == "x.json"
        return
    with pytest.raises(ReadRefusal) as refused:
        go_out.check_out(str(root / "OPEN" / "x.json"))
    assert refused.value.rule == "out_path_git_unknown"
    assert seen in str(refused.value) and "nothing was read or written" in str(refused.value)
    if ignorecase != "false":
        assert "sets core.ignorecase to false" not in str(refused.value)


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
