"""`--out PATH` for the `mb google` reads: a private file instead of terminal output (#1004).

A pulled report is business data. ``--out`` writes the same JSON that ``--json``
prints to a file only its owner can read, and prints a short summary. The path
is judged before anything is read from Google, so a refused path costs no
quota. A path is refused when:

- it is inside a git checkout and git does not report it ignored (a tracked
  file, or one a ``git add`` would pick up), including the business repo, or
  git does not ignore the temporary file written beside the target
  (``.<name>.mb-out.tmp``; a rule for the file name alone, or a negation that
  re-includes the temporary file, would not cover it);
- git cannot answer inside a checkout (fail closed);
- it already exists and ``--force`` was not given, or it exists and is not a
  plain file;
- its folder does not exist (no folder is created);
- the last part of it is a link.

Folders above the file may be links (macOS keeps ``/tmp`` and ``/var`` behind
one). The folder is resolved first and the checks run on where it really is, so
a link that leads into a repo is caught by the git check. ``--force`` replaces
an existing file but never lifts the git rules.

Nothing here reads credentials: the file holds what ``--json`` already prints.
"""

from __future__ import annotations

import os
import stat
import subprocess
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mb.connect import _inside_git_checkout
from mb.google_reads import ReadRefusal, terminal_safe

OUT_MODE = 0o600
GIT_TIMEOUT_SECONDS = 5
OUT_HINT = (
    "write it outside the repo, or in a folder git ignores as a whole, such as .mb/private/pulls/"
)

_GIT_ENV_DROP = {"GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"}


@dataclass(frozen=True)
class OutTarget:
    """A checked destination: the real parent folder and the file name."""

    path: Path
    force: bool


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[bytes] | None:
    env = {k: v for k, v in os.environ.items() if k not in _GIT_ENV_DROP}
    try:
        return subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            env=env,
            capture_output=True,
            timeout=GIT_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def _check_git(parent: Path, name: str, shown: str) -> None:
    """Allow a path outside any checkout, or one git reports ignored; refuse the rest."""

    top = _git(["rev-parse", "--show-toplevel"], parent)
    if top is not None and top.returncode == 0:
        root = Path(top.stdout.decode("utf-8", "replace").strip() or ".")
        try:
            relative = parent.resolve().relative_to(root.resolve()) / name
        except (OSError, RuntimeError, ValueError):
            raise _git_unknown(shown) from None
        if ".git" in relative.parts:
            raise _git_unknown(shown)
        verdict = _git(["check-ignore", "-q", "--", relative.as_posix()], root)
        if verdict is None or verdict.returncode not in {0, 1}:
            raise _git_unknown(shown)
        if verdict.returncode == 1:
            raise ReadRefusal(
                "out_path_in_repo",
                f"--out {shown} is inside a git checkout and git does not ignore it, so the "
                f"data could be committed; nothing was read or written. {OUT_HINT}.",
            )
        # The report is first written to a fixed temporary name beside the target, so
        # git must ignore that exact path too (a negation can re-include it).
        temp = relative.parent / temp_name(name)
        temp_verdict = _git(["check-ignore", "-q", "--", temp.as_posix()], root)
        if temp_verdict is None or temp_verdict.returncode not in {0, 1}:
            raise _git_unknown(shown)
        if temp_verdict.returncode == 1:
            raise _temp_refusal(shown, temp_name(name))
        return
    if _inside_git_checkout(parent):
        # A checkout is there but git would not say anything about it.
        raise _git_unknown(shown)


def _temp_refusal(shown: str, temp: str) -> ReadRefusal:
    return ReadRefusal(
        "out_temp_not_ignored",
        f"--out {shown}: inside a git checkout git must ignore both the file and its temporary "
        f"file {temp}, which holds the whole report while it is written; a rule for the file "
        "name alone, or a negation that re-includes the temporary file, would let it be "
        f"committed; nothing was read or written. {OUT_HINT}.",
    )


def _git_unknown(shown: str) -> ReadRefusal:
    return ReadRefusal(
        "out_path_git_unknown",
        f"--out {shown} is inside a git checkout and git could not say whether it is "
        f"ignored; nothing was read or written. {OUT_HINT}.",
    )


def temp_name(name: str) -> str:
    return f".{name}.mb-out.tmp"


def check_out(raw: str, *, force: bool = False) -> OutTarget:
    """Judge ``--out`` before any read. A relative PATH is relative to the shell's folder."""

    shown = _shown(raw)
    if not raw or "\x00" in raw:
        raise ReadRefusal("out_path_invalid", "--out needs a file path; nothing was read.")
    given = Path(raw).expanduser()
    if not given.is_absolute():
        given = Path.cwd() / given
    name = given.name
    if name in {"", ".", ".."}:
        raise ReadRefusal(
            "out_path_invalid", f"--out {shown} must name a file; nothing was read or written."
        )
    try:
        parent = given.parent.resolve(strict=True)
    except (OSError, RuntimeError):
        raise ReadRefusal(
            "out_parent_missing",
            f"--out {shown}: the folder does not exist; nothing was read or written. "
            "Create the folder first; mb does not create it.",
        ) from None
    if not parent.is_dir():
        raise ReadRefusal(
            "out_parent_missing",
            f"--out {shown}: the folder is not a folder; nothing was read or written.",
        )
    target = parent / name
    try:
        info = os.lstat(target)
    except FileNotFoundError:
        info = None
    except OSError:
        raise ReadRefusal(
            "out_path_invalid", f"--out {shown} could not be examined; nothing was read."
        ) from None
    if info is not None and stat.S_ISLNK(info.st_mode):
        raise ReadRefusal(
            "out_path_link",
            f"--out {shown} is a link; nothing was read or written. Name a plain file.",
        )
    if info is not None and not stat.S_ISREG(info.st_mode):
        raise ReadRefusal(
            "out_path_not_file",
            f"--out {shown} exists and is not a plain file; nothing was read or written.",
        )
    _check_git(parent, name, shown)
    if info is not None and not force:
        raise ReadRefusal(
            "out_path_exists",
            f"--out {shown} already exists; nothing was read or written. "
            "Pick another path, or add --force to replace it.",
        )
    return OutTarget(path=target, force=force)


def _shown(raw: str) -> str:
    return terminal_safe(raw, 120) or "PATH"


class OutWriteError(OSError):
    """The file could not be written; the read itself had already succeeded.

    ``existing_temp`` names a temporary file that was already there (an earlier
    or concurrent run); it was left untouched.
    """

    def __init__(self, message: str, existing_temp: str = "") -> None:
        super().__init__(message)
        self.existing_temp = existing_temp


def write_out(target: OutTarget, text: str) -> None:
    """Create the file with mode 0600, atomically. Without ``--force`` it never replaces one.

    The report goes through ``.<name>.mb-out.tmp`` in the same folder, created
    exclusively (an existing one is never reused or removed), after
    ``check_out`` saw that git ignores that exact path.
    """

    tmp = target.path.with_name(temp_name(target.path.name))
    created = False
    try:
        try:
            fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, OUT_MODE)
        except FileExistsError:
            raise OutWriteError("temporary file exists", tmp.name) from None
        created = True
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            os.fchmod(handle.fileno(), OUT_MODE)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        if target.force:
            os.replace(tmp, target.path)
            created = False
        else:
            os.link(tmp, target.path)
    except OutWriteError:
        raise
    except OSError as exc:
        raise OutWriteError(str(exc)) from None
    finally:
        if created:
            with suppress(OSError):
                os.unlink(tmp)


SCHEMA_OUT = "mb.google.out"


def summary(command: str, target: OutTarget, result: dict[str, Any]) -> dict[str, Any]:
    """What is printed after a write: the path and the size of the answer, never the data."""

    if "row_count" in result:
        count = result["row_count"]
    elif "sitemap_count" in result:
        count = result["sitemap_count"]
    else:
        count = 1 if result.get("inspection_result") else 0
    return {
        "ok": True,
        "out": str(target.path),
        "mode": "0600",
        "source_command": command,
        "row_count": count,
        "may_have_more": bool(result.get("may_have_more", False)),
        "safe_to_share": True,
    }


def render_summary(info: dict[str, Any]) -> list[str]:
    return [
        f"{info['source_command']}: wrote {terminal_safe(info['out'], 200)} (mode {info['mode']})",
        f"rows: {info['row_count']}, may_have_more: {str(info['may_have_more']).lower()}",
    ]
