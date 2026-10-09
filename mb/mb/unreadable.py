"""Name a file or folder Main Branch could not read, with its own fix (#1101, #1106, #1109).

`mb update` and `mb doctor` read files a person owns: `.gitignore`,
`.claude/settings.local.json`, `AGENTS.md`, the repo's `.claude` folder and the
global Codex folders. One that is not UTF-8, has no read permission, is a
folder where a file belongs, or is a link that loops raises from deep inside
the read. These helpers turn that into one sentence naming the path (relative
to the repo, or `~/...` under the home folder) and the step that fixes it.
"""

from __future__ import annotations

import ast
import errno
import os
from collections.abc import Iterable
from pathlib import Path

SYMLINK_LOOP_PREFIX = "Symlink loop from "
JSON_ERROR_CODE = "unreadable_file"


def _is_symlink_loop(exc: BaseException) -> bool:
    # pathlib raises a plain RuntimeError for a looping link on Python 3.10 to
    # 3.12. Its subclasses (NotImplementedError, RecursionError) and any other
    # RuntimeError are programming errors and must stay loud.
    return type(exc) is RuntimeError and str(exc).startswith(SYMLINK_LOOP_PREFIX)


def is_unreadable_error(exc: BaseException) -> bool:
    """True when `exc` means a file or folder could not be read."""
    return isinstance(exc, (OSError, UnicodeDecodeError)) or _is_symlink_loop(exc)


def _decoded_path(exc: BaseException) -> str:
    """The file a `Path.read_text` was decoding when it raised, if any."""
    found = ""
    tb = exc.__traceback__
    while tb is not None:
        frame = tb.tb_frame
        if frame.f_code.co_name == "read_text" and isinstance(frame.f_locals.get("self"), Path):
            found = str(frame.f_locals["self"])
        tb = tb.tb_next
    return found


def _raw_path(exc: BaseException) -> str:
    if isinstance(exc, OSError) and exc.filename:
        return os.fsdecode(exc.filename)
    if _is_symlink_loop(exc):
        # The path is a Python string literal, so a backslash or a quote in it
        # comes back as written (#1106 item 1).
        try:
            value = ast.literal_eval(str(exc)[len(SYMLINK_LOOP_PREFIX) :])
        except (ValueError, SyntaxError):
            return ""
        return value if isinstance(value, str) else ""
    if isinstance(exc, UnicodeDecodeError):
        # Only the file being decoded is named. Another file that does not
        # decode either may not be the one that failed, so none is guessed
        # (#1109 item 3).
        return _decoded_path(exc)
    return ""


def _within(raw: str, bases: Iterable[str]) -> str | None:
    for base in bases:
        if raw.startswith(base + os.sep):
            return base
    return None


def _loops(path: str) -> bool:
    """True when `path` is a link that never reaches a real file or folder."""
    if not os.path.islink(path):
        return False
    try:
        os.stat(path)
    except OSError as exc:
        return exc.errno == errno.ELOOP
    return False


def _closed(path: str) -> bool:
    """True when `path` is a folder this user cannot enter."""
    return os.path.isdir(path) and not os.access(path, os.X_OK)


def _first_blocked_folder(raw: str, base: str) -> str:
    """The first folder between `base` and `raw` that blocks the way to it.

    A folder that cannot be entered (#1106 item 3), or a link that loops: the
    link to remove is that one, not the path below it (#1109 item 1).
    """
    current = base
    for part in Path(os.path.relpath(raw, base)).parts[:-1]:
        current = os.path.join(current, part)
        if _loops(current) or _closed(current):
            return current
    return raw


def _locate(raw: str, repo: Path) -> tuple[str, str]:
    """`(named, shown)`: the path to name, and how to show it.

    Under the repo it is shown relative to it, under the home folder as
    `~/...`; anywhere else it stays absolute, since there is nothing shorter.
    """
    repo_bases = list(dict.fromkeys([str(repo), os.path.realpath(repo)]))
    base = _within(raw, repo_bases)
    if base is not None:
        raw = _first_blocked_folder(raw, base)
        return raw, os.path.relpath(raw, base).replace(os.sep, "/")
    home = str(Path.home())
    base = _within(raw, list(dict.fromkeys([home, os.path.realpath(home)])))
    if base is not None:
        raw = _first_blocked_folder(raw, base)
        return raw, "~/" + os.path.relpath(raw, base).replace(os.sep, "/")
    return raw, raw


def _is_loop(exc: BaseException, named: str) -> bool:
    if named and _loops(named):
        return True
    return _is_symlink_loop(exc) or (isinstance(exc, OSError) and exc.errno == errno.ELOOP)


def _reason(exc: BaseException, named: str) -> str:
    if isinstance(exc, UnicodeDecodeError):
        return "it is not UTF-8 text"
    if _is_loop(exc, named):
        return "it is a link that loops back on itself"
    if isinstance(exc, IsADirectoryError):
        return "it is a folder, not a file"
    if isinstance(exc, PermissionError):
        return "permission denied"
    if isinstance(exc, OSError) and exc.strerror:
        return exc.strerror.lower()
    return type(exc).__name__


def _fix(path: str, exc: BaseException, named: str) -> str:
    """The failing file's own fix (#1106 item 5)."""
    if not path:
        if isinstance(exc, UnicodeDecodeError):
            return "Save the files Main Branch reads in this repo as UTF-8 text"
        return "Check the files Main Branch reads in this repo"
    shown = f"`{path}`"
    if isinstance(exc, UnicodeDecodeError):
        return f"Save {shown} as UTF-8 text"
    if _is_loop(exc, named):
        return f"Remove the link {shown} or point it at a real file or folder"
    if isinstance(exc, IsADirectoryError):
        return f"Move the {shown} folder aside so a file can take its place"
    if isinstance(exc, PermissionError):
        if _closed(named) and os.access(named, os.R_OK):
            # Readable but not enterable (mode 600): read access is already
            # there; entering needs execute permission (#1109 item 5).
            return f"Let your user enter the {shown} folder (give it execute permission)"
        return f"Give your user read access to {shown}"
    return f"Check {shown}"


def describe(exc: BaseException, repo: Path) -> tuple[str, str, str]:
    """`(path, reason, fix)` for an unreadable-file error; `path` may be empty."""
    raw = _raw_path(exc)
    named, path = _locate(raw, repo) if raw else ("", "")
    return path, _reason(exc, named), _fix(path, exc, named)


def message(exc: BaseException, repo: Path) -> str:
    """One sentence for an `errors` entry: what could not be read and the fix."""
    path, reason, fix = describe(exc, repo)
    target = f"`{path}`" if path else "a file it needs"
    return f"Main Branch could not read {target} ({reason}). {fix}, then run the command again."
