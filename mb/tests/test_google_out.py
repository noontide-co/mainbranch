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


@pytest.mark.parametrize(
    ("gitignore", "where"),
    [
        ("report.json\n", "report.json"),
        ("*.json\n", "data.json"),
        ("exports/*.json\n", "exports/a.json"),
    ],
)
def test_a_file_name_ignore_alone_is_refused(
    gitignore: str,
    where: str,
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # The target's own name is ignored, but its temporary file would not be.
    root = _checkout_with(tmp_path / "pattern", gitignore)
    api = _signed(repo, client_file, google, monkeypatch)
    before = _porcelain(root)

    result = _out(repo, SC_ARGS, root / where)

    _refused(result, "out_folder_not_ignored")
    assert ".mb/private/" in result.stderr and ".mb/ " not in result.stderr
    assert api.calls == [] and not (root / where).exists()
    assert _porcelain(root) == before


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
