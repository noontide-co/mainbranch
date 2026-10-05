"""No test assert reads straight out of an environment mapping (#1025).

On failure, pytest's assertion rewriting prints the intermediate values of an
assert. `assert os.environ.get(KEY) == value` therefore prints the whole process
environment, which can carry a developer's or an agent's tokens. Read the one
key into a local first and assert on the local.
"""

from __future__ import annotations

import ast
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
_ENV_NAMES = {"env", "environ", "environment"}


def _is_env(node: ast.AST) -> bool:
    if isinstance(node, ast.Attribute) and node.attr == "environ":
        return True
    if isinstance(node, ast.Name):
        return node.id in _ENV_NAMES or node.id.endswith("_env") or node.id.startswith("env_")
    # A captured mapping such as `kwargs["env"]` or `call["env"]`.
    return (
        isinstance(node, ast.Subscript)
        and isinstance(node.slice, ast.Constant)
        and node.slice.value == "env"
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
        if (
            isinstance(node, ast.Compare)
            and any(isinstance(op, (ast.In, ast.NotIn)) for op in node.ops)
            and any(_is_env(comparator) for comparator in node.comparators)
        ):
            return True
    return False


def environment_asserts(source: str, filename: str = "<test>") -> list[int]:
    """Line numbers of asserts that index, call into or search an environment mapping."""
    tree = ast.parse(source, filename=filename)
    return [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Assert) and _reads_environment(node.test)
    ]


def test_guard_catches_the_dumping_patterns() -> None:
    source = "\n".join(
        [
            "assert os.environ.get('K') == 'v'",
            "assert os.environ['K'] == 'v'",
            "assert env['K'] == 'v'",
            "assert seen['kwargs']['env']['K'] == 'v'",
            "assert 'K' not in captured_env",
            "value = os.environ.get('K')",
            "assert value == 'v'",
            "assert env is not None",
        ]
    )

    assert environment_asserts(source) == [1, 2, 3, 4, 5]


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
