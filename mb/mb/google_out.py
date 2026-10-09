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
- the checkout sets ``core.ignorecase`` to false and a folder name is spelled
  differently from the one on disk (a disk that does not tell case apart);
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
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mb.connect import _inside_git_checkout
from mb.google_reads import ReadRefusal, terminal_safe

OUT_MODE = 0o600
GIT_TIMEOUT_SECONDS = 5
OUT_HINT = (
    "write it outside the repo, or under a folder git ignores, such as .mb/private/pulls/ "
    "(git must ignore both the file and its temporary file .<name>.mb-out.tmp)"
)

_GIT_ENV_DROP = {"GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"}
_GIT_ENV_INHERITED = ("GIT_DIR", "GIT_WORK_TREE")


@dataclass(frozen=True)
class OutTarget:
    """A checked destination: the real parent folder and the file name."""

    path: Path
    force: bool


def _git(
    args: list[str], cwd: Path, *, inherit_env: bool = False
) -> subprocess.CompletedProcess[bytes] | None:
    env = {k: v for k, v in os.environ.items() if inherit_env or k not in _GIT_ENV_DROP}
    if inherit_env:
        # The caller's shell reads a relative value against its own folder, not `cwd` here.
        try:
            shell_folder = os.getcwd()
        except OSError:
            return None
        for var in _GIT_ENV_INHERITED:
            if env.get(var) and not os.path.isabs(env[var]):
                env[var] = os.path.join(shell_folder, env[var])
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
    """Allow a path outside any checkout, or one git reports ignored; refuse the rest.

    The path is judged with the repository variables dropped (what a plain ``git``
    in that folder sees). When the caller exported ``GIT_DIR`` or ``GIT_WORK_TREE``,
    it is judged again with them, and both answers must allow it. An empty value
    counts as exported, as it does for git, which refuses to run with it.
    """

    _judge_git(parent, name, shown, inherit_env=False)
    if any(var in os.environ for var in _GIT_ENV_INHERITED):
        _judge_git(parent, name, shown, inherit_env=True)


def _judge_git(parent: Path, name: str, shown: str, *, inherit_env: bool) -> None:
    def run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[bytes] | None:
        # Without the inherited variables, call `_git` exactly as it always was.
        return _git(args, cwd, inherit_env=True) if inherit_env else _git(args, cwd)

    unknown = _git_env_unusable if inherit_env else _git_unknown
    # Refusals that come from the exported repository say so; without it the text is unchanged.
    which = _ENV_CHECKOUT if inherit_env else ""
    # With only GIT_DIR exported, git's work tree is the shell's own folder.
    start = _shell_folder() if inherit_env else parent
    top = run(["rev-parse", "--show-toplevel"], start) if start is not None else None
    if top is not None and top.returncode == 0:
        root = Path(top.stdout.decode("utf-8", "replace").strip() or ".")
        try:
            base = root.resolve()
            relative = parent.resolve().relative_to(base) / name
        except (OSError, RuntimeError, ValueError):
            if not inherit_env:
                raise _git_unplaced(shown) from None
            try:
                found = _identity_ancestor(parent, root, strict=True)
            except OSError:
                # Never count a folder as outside the work tree when it could not be compared.
                raise _work_tree_unexamined(shown) from None
            if found is None:
                # The exported work tree does not hold this folder: it says nothing about it.
                return
            if _spelled_as_on_disk(parent, Path(parent.anchor)) is not True:
                raise _git_unplaced(shown, which) from None
            # GIT_WORK_TREE names the same folder in another spelling (case, firmlink).
            base = found
            relative = parent.relative_to(found) / name
        if ".git" in relative.parts:
            raise unknown(shown)
        verdict = run(["check-ignore", "-q", "--", relative.as_posix()], root)
        if verdict is None or verdict.returncode not in {0, 1}:
            raise unknown(shown)
        if verdict.returncode == 1:
            raise ReadRefusal(
                "out_path_in_repo",
                f"--out {shown} is inside a git checkout{which} and git does not ignore it, so "
                f"the data could be committed; nothing was read or written. {OUT_HINT}.",
            )
        # The report is first written to a fixed temporary name beside the target, so
        # git must ignore that exact path too (a negation can re-include it).
        temp = relative.parent / temp_name(name)
        temp_verdict = run(["check-ignore", "-q", "--", temp.as_posix()], root)
        if temp_verdict is None or temp_verdict.returncode not in {0, 1}:
            raise unknown(shown)
        if temp_verdict.returncode == 1:
            raise _temp_refusal(shown, temp_name(name), which)
        _check_spelling(base, relative, root, shown, which, run)
        return
    if inherit_env:
        # The exported variables name a repository git cannot use from here.
        raise _git_env_unusable(shown)
    if _inside_git_checkout(parent):
        # A checkout is there but git would not say anything about it.
        raise _git_unknown(shown)


def _shell_folder() -> Path | None:
    try:
        return Path(os.getcwd())
    except OSError:
        return None


def _identity_ancestor(path: Path, target: Path, *, strict: bool = False) -> Path | None:
    """The folder among ``path`` and its parents that is the same file as ``target``.

    With ``strict``, an ``OSError`` while comparing is raised instead of skipped.
    """

    for candidate in (path, *path.parents):
        try:
            if os.path.samefile(candidate, target):
                return candidate
        except OSError:
            if strict:
                raise
    return None


def _spelled_as_on_disk(path: Path, base: Path) -> bool | None:
    """Whether every name in ``path`` below ``base`` is spelled as the disk lists it.

    ``None`` when a folder could not be listed. On a disk that tells case apart a
    name that exists is always listed as given.
    """

    folder = base
    for part in path.relative_to(base).parts:
        try:
            if part not in os.listdir(folder):
                return False
        except OSError:
            return None
        folder = folder / part
    return True


def _check_spelling(
    base: Path,
    relative: Path,
    root: Path,
    shown: str,
    which: str,
    run: Any,
) -> None:
    """Refuse a folder spelled unlike the disk when git matches ignore rules by exact case.

    ``base`` is the work tree as found on disk and ``relative`` the path git judged.
    With ``core.ignorecase`` false, git matched the rules against the spelling given,
    but the file lands in the folder the disk has, which those rules may not cover.
    """

    folders = relative.parent
    target = base / relative
    names = folders / relative.name if os.path.lexists(target) else folders
    spelled = _spelled_as_on_disk(base / names, base)
    if spelled is True:
        return
    setting = run(["config", "--bool", "core.ignorecase"], root)
    if setting is not None and setting.returncode == 0 and setting.stdout.strip() == b"true":
        return
    if spelled is None:
        raise _git_unplaced(shown, which)
    raise ReadRefusal(
        "out_path_git_unknown",
        f"--out {shown}: this checkout{which} sets core.ignorecase to false, but the disk does "
        "not tell folder names apart by case and the path is spelled differently from the "
        "folder on disk, so git's ignore rules may not cover where the file would land; "
        "nothing was read or written. Spell the folders as they are on disk, or set "
        "core.ignorecase to true (what git init sets on this disk).",
    )


_ENV_CHECKOUT = " (the one GIT_DIR or GIT_WORK_TREE in this shell names)"


def _temp_refusal(shown: str, temp: str, which: str = "") -> ReadRefusal:
    return ReadRefusal(
        "out_temp_not_ignored",
        f"--out {shown}: inside a git checkout{which} git must ignore both the file and its "
        f"temporary file {temp}, which holds the whole report while it is written; a rule for "
        "the file name alone, or a negation that re-includes the temporary file, would let it be "
        f"committed; nothing was read or written. {OUT_HINT}.",
    )


def _git_unknown(shown: str) -> ReadRefusal:
    return ReadRefusal(
        "out_path_git_unknown",
        f"--out {shown} is inside a git checkout and git could not say whether it is "
        f"ignored; nothing was read or written. {OUT_HINT}.",
    )


def _git_env_unusable(shown: str) -> ReadRefusal:
    # Same rule as `_git_unknown`; the cause is the caller's GIT_DIR / GIT_WORK_TREE.
    return ReadRefusal(
        "out_path_git_unknown",
        f"--out {shown}: GIT_DIR or GIT_WORK_TREE is set in this shell, but git could not use "
        "that repository from here, so mb cannot check that git ignores the file; nothing was "
        "read or written. Unset them (or fix them) and run again.",
    )


def _work_tree_unexamined(shown: str) -> ReadRefusal:
    # Same rule as `_git_unknown`: the exported work tree could not be compared with the folder.
    return ReadRefusal(
        "out_path_git_unknown",
        f"--out {shown}: GIT_DIR or GIT_WORK_TREE is set in this shell, but mb could not "
        "examine that work tree to tell whether the file would be inside it, so it cannot "
        "check that git ignores the file; nothing was read or written. Unset them (or fix "
        "them) and run again.",
    )


def _git_unplaced(shown: str, which: str = "") -> ReadRefusal:
    # Same rule as `_git_unknown`: the folder is refused, but the cause is on mb's side
    # (for example `BIZ/` for `Biz/` on a case-insensitive disk), not git's.
    return ReadRefusal(
        "out_path_git_unknown",
        f"--out {shown} is inside a git checkout{which}, but mb could not place the path in that "
        "checkout (a differently spelled folder name, for example), so it cannot check "
        f"that git ignores it; nothing was read or written. {OUT_HINT}.",
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
    """``raw`` as printed in a refusal: ``~/...`` when it is an absolute path under home."""

    return terminal_safe(_home_relative(raw), 120) or "PATH"


def _home_relative(raw: str) -> str:
    if not raw or "\x00" in raw:
        return raw
    try:
        given = Path(raw).expanduser()
        if not given.is_absolute():
            return raw
        home = Path.home()
        # The spelling given first, then where it really is (a link, a case variant).
        for path in (given, given.resolve()):
            found = _identity_ancestor(path, home)
            if found is not None:
                return "~/" + path.relative_to(found).as_posix()
    except (OSError, RuntimeError, ValueError):
        pass
    return raw


class OutWriteError(OSError):
    """The file could not be written; the read itself had already succeeded.

    ``existing_temp`` names a temporary file that was already there (an earlier
    or concurrent run); it was left untouched. ``leftover_temp`` names this run's
    own temporary file when removing it failed, so the file is still there.
    """

    def __init__(self, message: str, existing_temp: str = "", leftover_temp: str = "") -> None:
        super().__init__(message)
        self.existing_temp = existing_temp
        self.leftover_temp = leftover_temp


def write_out(target: OutTarget, text: str) -> str:
    """Create the file with mode 0600, atomically. Without ``--force`` it never replaces one.

    The report goes through ``.<name>.mb-out.tmp`` in the same folder, created
    exclusively (an existing one is never reused or removed), after
    ``check_out`` saw that git ignores that exact path. Returns that temporary
    file's name when the file was written but the temporary copy could not be
    removed, otherwise ``""``.
    """

    tmp = target.path.with_name(temp_name(target.path.name))
    created = False
    failure: OutWriteError | None = None
    leftover = ""
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
        failure = OutWriteError(str(exc))
    finally:
        if created:
            try:
                os.unlink(tmp)
            except OSError:
                if failure is not None:
                    failure.leftover_temp = tmp.name
                else:
                    leftover = tmp.name
    if failure is not None:
        raise failure
    return leftover


SCHEMA_OUT = "mb.google.out"


def display_path(path: Path) -> str:
    """The path as shown: ``~/...`` under the home folder, so no username is printed."""

    try:
        real = path.resolve()
        home = _identity_ancestor(real, Path.home())
        if home is not None:
            return "~/" + real.relative_to(home).as_posix()
    except (OSError, RuntimeError, ValueError):
        pass
    return str(path)


def leftover_warning(temp: str) -> str:
    return (
        f"the temporary file {temp} could not be removed and is still there, a second copy "
        "of the report beside the file; remove it yourself."
    )


def summary(
    command: str, target: OutTarget, result: dict[str, Any], leftover: str = ""
) -> dict[str, Any]:
    """What is printed after a write: the path and the size of the answer, never the data."""

    if "row_count" in result:
        count = result["row_count"]
    elif "sitemap_count" in result:
        count = result["sitemap_count"]
    else:
        count = 1 if result.get("inspection_result") else 0
    info: dict[str, Any] = {
        "ok": True,
        "out": display_path(target.path),
        "mode": "0600",
        "source_command": command,
        "row_count": count,
        "may_have_more": bool(result.get("may_have_more", False)),
        "safe_to_share": True,
    }
    if leftover:
        info["warnings"] = [leftover_warning(leftover)]
    return info


def render_summary(info: dict[str, Any]) -> list[str]:
    lines = [
        f"{info['source_command']}: wrote {terminal_safe(info['out'], 200)} (mode {info['mode']})",
        f"rows: {info['row_count']}, may_have_more: {str(info['may_have_more']).lower()}",
    ]
    lines.extend(f"warning: {warning}" for warning in info.get("warnings", []))
    return lines
