"""No test assert reads straight out of an environment mapping (#1025).

On failure, pytest's assertion rewriting prints the intermediate values of an
assert. `assert os.environ.get(KEY) == value` therefore prints the whole process
environment, which can carry a developer's or an agent's tokens. Read the one
key into a local first and assert on the local.

This guard is a lint for the common shapes, not a proof: an alias such as
`e = os.environ` followed by `assert e[...]` is not traced.
"""

from __future__ import annotations

import ast
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
_ENV_NAMES = {"env", "environ", "environment"}
# Captured mappings that hold an environment: `x["env"]`, and a captured
# subprocess call's keyword arguments, `x["kwargs"]`.
_ENV_KEYS = {"env", "kwargs"}


def _is_env(node: ast.AST) -> bool:
    if isinstance(node, ast.Attribute) and node.attr == "environ":
        return True
    if isinstance(node, ast.Name):
        return node.id in _ENV_NAMES or node.id.endswith("_env") or node.id.startswith("env_")
    if (
        isinstance(node, ast.Subscript)
        and isinstance(node.slice, ast.Constant)
        and node.slice.value in _ENV_KEYS
    ):
        return True
    # A copy such as `dict(os.environ)`.
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "dict"
        and any(_is_env(arg) for arg in node.args)
    )


def _reads_environment(test: ast.expr) -> bool:
    for node in ast.walk(test):
        if isinstance(node, ast.Subscript) and _is_env(node.value):
            return True
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and _is_env(node.func.value)
        ):
            return True
        if isinstance(node, ast.Compare):
            operands = [node.left, *node.comparators]
            for op, left, right in zip(node.ops, operands[:-1], operands[1:], strict=True):
                if isinstance(op, (ast.In, ast.NotIn)) and _is_env(right):
                    return True
                if isinstance(op, (ast.Eq, ast.NotEq)) and (_is_env(left) or _is_env(right)):
                    return True
    return False


def environment_asserts(source: str, filename: str = "<test>") -> list[int]:
    """Line numbers of asserts that index, call into, compare or search an environment."""
    tree = ast.parse(source, filename=filename)
    return [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Assert) and _reads_environment(node.test)
    ]


FLAGGED = [
    "assert os.environ.get('K') == 'v'",
    "assert os.environ['K'] == 'v'",
    "assert env['K'] == 'v'",
    "assert seen['kwargs']['env']['K'] == 'v'",
    "assert 'K' not in captured_env",
    'assert "shell" not in seen["kwargs"]',
    'assert kwargs["env"] == x',
    'assert x != kwargs["env"]',
    "assert captured_env == {}",
    'assert dict(os.environ)["X"] == "y"',
]
NOT_FLAGGED = [
    "value = os.environ.get('K')",
    "assert value == 'v'",
    "assert env is not None",
    'assert token == "x"',
    'assert kwarg_names == ["env"]',
    'assert "shell" not in kwarg_names',
]


def test_guard_flags_every_dumping_shape() -> None:
    for line in FLAGGED:
        assert environment_asserts(line) == [1], line


def test_guard_leaves_local_reads_alone() -> None:
    for line in NOT_FLAGGED:
        assert environment_asserts(line) == [], line


def test_no_test_asserts_directly_on_an_environment() -> None:
    offenders = [
        f"{path.relative_to(TESTS_DIR)}:{line}"
        for path in sorted(TESTS_DIR.rglob("*.py"))
        for line in environment_asserts(path.read_text(encoding="utf-8"), str(path))
    ]

    assert offenders == [], (
        "Read the environment value into a local before asserting on it, so a "
        "failure prints only that value: " + ", ".join(offenders)
    )
