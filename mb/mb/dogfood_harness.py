"""Claude Code runtime dogfood harness for release/contributor smoke tests.

This module backs the repo-level script. It is intentionally not exposed as an
``mb`` command because optional Claude print-mode smoke invokes a runtime.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from mb import release_simulation

InstallMode = Literal["editable", "wheel", "pypi"]

DEFAULT_BUSINESS_NAME = "Dogfood Studio"
DEFAULT_FIXTURE_SLUG = "dogfood-studio"
DEFAULT_CLAUDE_BUDGET = "0.25"

SAFE_FIXTURE_FILES: dict[str, str] = {
    "core/offer.md": """# Offer

Dogfood Studio helps solo founders keep offer, audience, voice, and launch
context in files they own so AI sessions stop starting from zero.

Primary offer: a two-week operating-memory setup sprint.
Promise: leave with a working business repo, daily decision flow, and one
shipped growth asset.
""",
    "core/audience.md": """# Audience

Solo founders and small service operators who already use AI for marketing and
operations but keep losing context across chats, SaaS tools, and docs.

They are capable but busy. They want exact next steps, not abstract systems
thinking.
""",
    "core/voice.md": """# Voice

Direct, specific, calm, and practical. Avoid hype. Explain tradeoffs in plain
English. Prefer business-owner language before tool internals.
""",
    "research/2026-05-07-ai-context-reset.md": """---
date: 2026-05-07
topic: AI context reset pain
source: sanitized dogfood fixture
---

# AI Context Reset Pain

Common complaint: every new AI chat requires the founder to re-explain the
offer, audience, proof, and current priority. The opportunity is to turn the
business repo into the durable briefing layer.
""",
}


@dataclass
class CommandResult:
    """Captured process result plus artifact paths."""

    label: str
    command: list[str]
    cwd: Path
    returncode: int
    stdout: str
    stderr: str
    stdout_path: Path
    stderr_path: Path
    metadata_path: Path

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def summary(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "returncode": self.returncode,
            "stdout": str(self.stdout_path),
            "stderr": str(self.stderr_path),
        }


@dataclass
class HarnessState:
    """Mutable state for one harness run."""

    engine_repo: Path
    root: Path
    evidence_dir: Path
    fixture_repo: Path
    mb_path: Path
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    commands: list[CommandResult] = field(default_factory=list)
    parsed_json: dict[str, Any] = field(default_factory=dict)
    engine_status_before: str = ""
    engine_status_after: str = ""
    fixture_status_after: str = ""
    fixture_diff_after: str = ""
    claude: dict[str, Any] = field(default_factory=dict)

    def fail(self, message: str) -> None:
        self.failures.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def repo_root_from_module() -> Path:
    """Return the source checkout root when this module is imported from the repo."""
    return Path(__file__).resolve().parents[2]


def safe_label(label: str) -> str:
    """Convert a command label into an artifact-safe stem."""
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in label).strip("-")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(text: str, *, label: str) -> tuple[dict[str, Any] | None, str]:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"{label} emitted invalid JSON: {exc}"
    if not isinstance(parsed, dict):
        return None, f"{label} emitted JSON {type(parsed).__name__}, expected object"
    return parsed, ""


def run_command(
    state: HarnessState,
    label: str,
    command: Sequence[str],
    *,
    cwd: Path,
    input_text: str | None = None,
    env: dict[str, str] | None = None,
    timeout: int = 180,
) -> CommandResult:
    """Run a command and write stdout/stderr/metadata artifacts."""
    artifact_stem = safe_label(label)
    stdout_path = state.evidence_dir / "commands" / f"{artifact_stem}.stdout"
    stderr_path = state.evidence_dir / "commands" / f"{artifact_stem}.stderr"
    metadata_path = state.evidence_dir / "commands" / f"{artifact_stem}.json"
    stdout_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        completed = subprocess.run(
            list(command),
            cwd=str(cwd),
            input=input_text,
            text=True,
            capture_output=True,
            env=env,
            timeout=timeout,
            check=False,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        returncode = completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        stderr = f"{stderr}\nCommand timed out after {timeout}s".strip() + "\n"
        returncode = 124

    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    metadata = {
        "label": label,
        "command": list(command),
        "cwd": str(cwd),
        "returncode": returncode,
        "stdout": str(stdout_path),
        "stderr": str(stderr_path),
    }
    write_json(metadata_path, metadata)
    result = CommandResult(
        label=label,
        command=list(command),
        cwd=cwd,
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        metadata_path=metadata_path,
    )
    state.commands.append(result)
    return result


def ensure_ok(state: HarnessState, result: CommandResult, detail: str | None = None) -> None:
    if result.ok:
        return
    suffix = f": {detail}" if detail else ""
    state.fail(f"{result.label} exited {result.returncode}{suffix}")


def parse_command_json(
    state: HarnessState, key: str, result: CommandResult
) -> dict[str, Any] | None:
    payload, error = read_json(result.stdout, label=result.label)
    if error:
        state.fail(error)
        return None
    assert payload is not None
    state.parsed_json[key] = payload
    json_path = state.evidence_dir / "json" / f"{safe_label(key)}.json"
    write_json(json_path, payload)
    return payload


def git_text(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(repo),
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.stdout if completed.returncode == 0 else completed.stderr


def make_venv(root: Path) -> Path:
    venv = root / "venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
    return venv / ("Scripts" if os.name == "nt" else "bin")


def install_mb(
    *,
    mode: InstallMode,
    root: Path,
    engine_repo: Path,
    wheel: Path | None,
    pypi_version: str,
) -> Path:
    """Install the package under test into a temp venv and return the mb executable."""
    bin_dir = make_venv(root)
    pip = bin_dir / "pip"
    mb = bin_dir / ("mb.exe" if os.name == "nt" else "mb")
    if mode == "editable":
        target = engine_repo / "mb"
        subprocess.run([str(pip), "install", "-e", str(target)], check=True)
    elif mode == "wheel":
        if wheel is None:
            raise ValueError("--wheel is required with --install-mode wheel")
        subprocess.run([str(pip), "install", str(wheel)], check=True)
    else:
        package = "mainbranch" if not pypi_version else f"mainbranch=={pypi_version}"
        subprocess.run([str(pip), "install", package], check=True)
    return mb


def write_fixture_context(repo: Path) -> None:
    for relative_path, body in SAFE_FIXTURE_FILES.items():
        path = repo / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    for folder in ("decisions", "pushes", "log", "documents"):
        (repo / folder).mkdir(exist_ok=True)


def setup_fixture(state: HarnessState) -> None:
    onboard = run_command(
        state,
        "mb-onboard",
        [
            str(state.mb_path),
            "onboard",
            "--yes",
            "--name",
            DEFAULT_BUSINESS_NAME,
            "--path",
            str(state.fixture_repo),
            "--json",
        ],
        cwd=state.root,
        timeout=240,
    )
    ensure_ok(state, onboard)
    onboard_json = parse_command_json(state, "onboard", onboard)
    if onboard_json and not onboard_json.get("ok", False):
        state.fail("mb onboard reported ok=false")

    for key, value in {
        "user.name": "Main Branch Dogfood",
        "user.email": "dogfood@example.com",
    }.items():
        config = run_command(
            state,
            f"git-config-{key}",
            ["git", "config", key, value],
            cwd=state.fixture_repo,
        )
        ensure_ok(state, config)

    write_fixture_context(state.fixture_repo)
    git_add = run_command(state, "fixture-git-add", ["git", "add", "."], cwd=state.fixture_repo)
    ensure_ok(state, git_add)
    commit = run_command(
        state,
        "fixture-initial-commit",
        ["git", "commit", "-m", "[added] dogfood fixture context"],
        cwd=state.fixture_repo,
    )
    ensure_ok(state, commit, "fixture checkpoint commit should pass the Main Branch hook")

    skill = state.fixture_repo / ".claude" / "skills" / "mb-start" / "SKILL.md"
    if not skill.exists():
        state.fail("missing .claude/skills/mb-start/SKILL.md in fixture repo")


def run_cli_checks(state: HarnessState) -> None:
    doctor = run_command(
        state,
        "mb-doctor-json",
        [str(state.mb_path), "doctor", str(state.fixture_repo), "--json"],
        cwd=state.fixture_repo,
    )
    doctor_json = parse_command_json(state, "doctor", doctor)
    if not doctor.ok:
        state.warn("mb doctor returned nonzero; inspect doctor JSON for actionable repair")
    if doctor_json and not isinstance(doctor_json.get("checks", []), list):
        state.fail("mb doctor JSON did not include checks list")

    repair = run_command(
        state,
        "mb-doctor-repair-plan-json",
        [
            str(state.mb_path),
            "doctor",
            "repair",
            "--repo",
            str(state.fixture_repo),
            "--plan",
            "--json",
        ],
        cwd=state.fixture_repo,
    )
    repair_json = parse_command_json(state, "doctor_repair_plan", repair)
    if repair_json and repair_json.get("read_only") is not True:
        state.fail("mb doctor repair --plan did not report read_only=true")

    hook = run_command(
        state,
        "mb-checkpoint-hook-status-json",
        [
            str(state.mb_path),
            "checkpoint",
            "--repo",
            str(state.fixture_repo),
            "--hook-status",
            "--json",
        ],
        cwd=state.fixture_repo,
    )
    ensure_ok(state, hook)
    hook_json = parse_command_json(state, "checkpoint_hook_status", hook)
    if hook_json and not hook_json.get("ok", False):
        state.fail("checkpoint hook status reported ok=false")

    status = run_command(
        state,
        "mb-checkpoint-status-json",
        [str(state.mb_path), "checkpoint", "--repo", str(state.fixture_repo), "--status", "--json"],
        cwd=state.fixture_repo,
    )
    ensure_ok(state, status)
    parse_command_json(state, "checkpoint_status", status)

    validation = run_command(
        state,
        "mb-checkpoint-validate-json",
        [
            str(state.mb_path),
            "checkpoint",
            "--repo",
            str(state.fixture_repo),
            "--validate",
            "[drafted] dogfood transcript notes",
            "--json",
        ],
        cwd=state.fixture_repo,
    )
    ensure_ok(state, validation)
    validation_json = parse_command_json(state, "checkpoint_validate", validation)
    if validation_json and not validation_json.get("ok", False):
        state.fail("checkpoint message validation failed")

    validate = run_command(
        state,
        "mb-validate-cross-refs-json",
        [str(state.mb_path), "validate", str(state.fixture_repo), "--cross-refs", "--json"],
        cwd=state.fixture_repo,
    )
    ensure_ok(state, validate)
    validate_json = parse_command_json(state, "validate_cross_refs", validate)
    if validate_json and not validate_json.get("ok", False):
        state.fail("mb validate --cross-refs --json reported ok=false")

    status_json_result = run_command(
        state,
        "mb-status-json-peek",
        [str(state.mb_path), "status", str(state.fixture_repo), "--json", "--peek"],
        cwd=state.fixture_repo,
    )
    ensure_ok(state, status_json_result)
    status_json = parse_command_json(state, "status_peek", status_json_result)
    check_status_payload(state, status_json)

    start = run_command(
        state,
        "mb-start-json",
        [str(state.mb_path), "start", "--repo", str(state.fixture_repo), "--json"],
        cwd=state.fixture_repo,
    )
    start_json = parse_command_json(state, "start", start)
    if not start.ok:
        state.warn(
            "mb start --json returned nonzero; handoff may be blocked by local runtime setup"
        )
    check_start_payload(state, start_json)


def check_status_payload(state: HarnessState, payload: dict[str, Any] | None) -> None:
    if payload is None:
        return
    if payload.get("schema_version") != "1.0":
        state.fail("mb status JSON schema_version was not 1.0")
    runtime = payload.get("runtime")
    if not isinstance(runtime, dict):
        state.fail("mb status JSON missing runtime object")
        return
    wiring = runtime.get("skill_wiring")
    if not isinstance(wiring, dict) or wiring.get("ok") is not True:
        state.fail("mb status JSON reports unhealthy skill wiring")


def check_start_payload(state: HarnessState, payload: dict[str, Any] | None) -> None:
    if payload is None:
        return
    command = payload.get("command")
    if not isinstance(command, dict) or command.get("follow_up") != "/mb-start":
        state.fail("mb start JSON did not name /mb-start as follow_up")
    runtime = payload.get("runtime")
    wiring = runtime.get("skill_wiring") if isinstance(runtime, dict) else None
    if not isinstance(wiring, dict) or wiring.get("ok") is not True:
        state.fail("mb start JSON reports unhealthy skill wiring")
    if payload.get("handoff_ready") is not True:
        state.warn("mb start JSON did not report handoff_ready=true")


def claude_version() -> str:
    if shutil.which("claude") is None:
        return "missing"
    completed = subprocess.run(
        ["claude", "--version"],
        text=True,
        capture_output=True,
        check=False,
    )
    return (completed.stdout or completed.stderr).strip() or f"exit {completed.returncode}"


def extract_session_id(payload: dict[str, Any]) -> str:
    for key in ("session_id", "sessionId"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    result = payload.get("result")
    if isinstance(result, dict):
        return extract_session_id(result)
    return ""


def transcript_text_from_payload(payload: dict[str, Any]) -> str:
    chunks: list[str] = []
    for key in ("result", "response", "text", "content", "message"):
        value = payload.get(key)
        if isinstance(value, str):
            chunks.append(value)
        elif isinstance(value, dict):
            chunks.append(transcript_text_from_payload(value))
        elif isinstance(value, list):
            chunks.extend(_text_from_list(value))
    return "\n".join(chunk for chunk in chunks if chunk)


def _text_from_list(values: list[Any]) -> list[str]:
    chunks: list[str] = []
    for item in values:
        if isinstance(item, str):
            chunks.append(item)
        elif isinstance(item, dict):
            chunks.append(transcript_text_from_payload(item))
        elif isinstance(item, list):
            chunks.extend(_text_from_list(item))
    return chunks


def score_transcript(text: str) -> dict[str, Any]:
    return release_simulation.score_transcript(text)


def run_claude_print(state: HarnessState, *, max_budget_usd: str, simulation_tier: str) -> None:
    if shutil.which("claude") is None:
        state.warn("Claude Code executable not found; skipped optional print-mode smoke")
        state.claude = {
            "mode": "print_proxy",
            "ran": False,
            "reason": "claude executable not found",
            "proxy_notice": "Print-mode evidence is not the same as interactive TUI evidence.",
            "simulation_tier": simulation_tier,
        }
        return

    session_id = ""
    turns: list[dict[str, Any]] = []
    transcript_parts: list[str] = []
    simulations = release_simulation.simulations_for_tier(simulation_tier)
    for simulation in simulations:
        command = [
            "claude",
            "-p",
            "--output-format",
            "json",
            "--max-budget-usd",
            max_budget_usd,
        ]
        if session_id:
            command.extend(["--resume", session_id])
        command.append(simulation.prompt)
        result = run_command(
            state,
            f"claude-print-{simulation.label}",
            command,
            cwd=state.fixture_repo,
            timeout=600,
        )
        payload, error = read_json(result.stdout, label=result.label)
        turn: dict[str, Any] = {
            "label": simulation.label,
            "simulation_id": simulation.id,
            "title": simulation.title,
            "expected_behaviors": list(simulation.expected_behaviors),
            "returncode": result.returncode,
            "stdout": str(result.stdout_path),
            "stderr": str(result.stderr_path),
            "parsed_json": error == "",
        }
        if payload is not None:
            write_json(
                state.evidence_dir / "claude" / f"{safe_label(simulation.label)}.json",
                payload,
            )
            new_session_id = extract_session_id(payload)
            if new_session_id:
                session_id = new_session_id
            text = transcript_text_from_payload(payload)
            if text:
                transcript_parts.append(f"## {simulation.label}\n\n{text.strip()}\n")
        else:
            turn["error"] = error
        turns.append(turn)
        if result.returncode != 0:
            state.warn(
                f"Claude print-mode stopped at {simulation.label}; "
                "inspect stderr for auth/budget details"
            )
            break

    transcript_text = "\n".join(transcript_parts)
    transcript_path = state.evidence_dir / "claude" / "transcript-excerpts.md"
    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    transcript_path.write_text(transcript_text, encoding="utf-8")
    rubric = score_transcript(transcript_text)
    write_json(state.evidence_dir / "claude" / "rubric.json", rubric)

    skill_discovery = rubric.get("checks", {}).get("skill_discovery", {})
    observed_unknown_command = False
    if isinstance(skill_discovery, dict):
        observed_unknown_command = bool(skill_discovery.get("observed_unknown_command_failure"))
    if transcript_text and observed_unknown_command:
        state.fail("Claude print-mode transcript reported an unknown command")

    state.claude = {
        "mode": "print_proxy",
        "ran": True,
        "proxy_notice": "Print-mode evidence is not the same as interactive TUI evidence.",
        "simulation_tier": simulation_tier,
        "max_budget_usd": max_budget_usd,
        "session_id": session_id,
        "turns": turns,
        "simulations": [
            {
                "id": simulation.id,
                "label": simulation.label,
                "title": simulation.title,
                "expected_route": list(simulation.expected_route),
                "expected_behaviors": list(simulation.expected_behaviors),
                "must_observe": list(simulation.must_observe),
                "must_not": list(simulation.must_not),
            }
            for simulation in simulations
        ],
        "transcript_excerpts": str(transcript_path),
        "rubric": rubric,
    }


def collect_post_run_state(state: HarnessState) -> None:
    state.fixture_status_after = git_text(state.fixture_repo, "status", "--short")
    state.fixture_diff_after = git_text(state.fixture_repo, "diff", "--stat")
    state.engine_status_after = git_text(state.engine_repo, "status", "--short")
    (state.evidence_dir / "git").mkdir(parents=True, exist_ok=True)
    (state.evidence_dir / "git" / "fixture-status-after.txt").write_text(
        state.fixture_status_after,
        encoding="utf-8",
    )
    (state.evidence_dir / "git" / "fixture-diff-stat-after.txt").write_text(
        state.fixture_diff_after,
        encoding="utf-8",
    )
    (state.evidence_dir / "git" / "engine-status-before.txt").write_text(
        state.engine_status_before,
        encoding="utf-8",
    )
    (state.evidence_dir / "git" / "engine-status-after.txt").write_text(
        state.engine_status_after,
        encoding="utf-8",
    )
    if state.engine_status_after != state.engine_status_before:
        state.fail("engine repo git status changed during dogfood harness run")


def evidence_template(state: HarnessState, *, install_mode: str, mb_version: str) -> str:
    status_payload = state.parsed_json.get("status_peek", {})
    start_payload = state.parsed_json.get("start", {})
    hook_payload = state.parsed_json.get("checkpoint_hook_status", {})
    validate_payload = state.parsed_json.get("validate_cross_refs", {})
    claude = state.claude or {
        "ran": False,
        "reason": "not requested",
        "proxy_notice": "Print-mode evidence is not the same as interactive TUI evidence.",
    }
    rubric = claude.get("rubric") if isinstance(claude, dict) else None
    rubric_summary = "not run"
    if isinstance(rubric, dict):
        rubric_summary = f"{rubric.get('passed', 0)}/{rubric.get('total', 0)} heuristic checks"
    skill_present = (state.fixture_repo / ".claude" / "skills" / "mb-start" / "SKILL.md").exists()
    status_schema = status_payload.get("schema_version", "unknown")
    status_wiring = nested_get(status_payload, ("runtime", "skill_wiring", "ok"))
    start_follow_up = nested_get(start_payload, ("command", "follow_up"))
    start_handoff = start_payload.get("handoff_ready", "unknown")
    claude_ran = claude.get("ran", False) if isinstance(claude, dict) else False
    claude_notice = claude.get("proxy_notice", "") if isinstance(claude, dict) else ""
    claude_tier = (
        claude.get("simulation_tier", "not run") if isinstance(claude, dict) else "not run"
    )
    claude_session = bool(claude.get("session_id")) if isinstance(claude, dict) else False
    claude_transcript = "local artifact; see harness output and summary.json"
    if not (isinstance(claude, dict) and claude.get("transcript_excerpts")):
        claude_transcript = "not run"

    return f"""## Claude Code Runtime Dogfood Evidence

Date: {datetime.now(timezone.utc).date().isoformat()}
Main Branch ref or version: {mb_version}
Install mode: {install_mode}
Claude Code version: {claude_version()}
OS: {sys.platform}
Fixture repo path: disposable temp path, no private data
Evidence folder: local artifact; see harness output and summary.json

### CLI Fixture Setup

- `mb onboard --yes --json`: {result_status(state, "mb-onboard")}
- Fixture commit: {result_status(state, "fixture-initial-commit")}
- `.claude/skills/mb-start/SKILL.md` present: {skill_present}

### Read-Only Checks

- `mb doctor --json`: {result_status(state, "mb-doctor-json")}
- `mb doctor repair --plan --json`: {result_status(state, "mb-doctor-repair-plan-json")}
- `mb checkpoint --hook-status --json`: {hook_payload.get("ok", "unknown")}
- `mb validate --cross-refs --json`: {validate_payload.get("ok", "unknown")}
- `mb status --json --peek`: schema {status_schema}, skill wiring {status_wiring}
- `mb start --json`: follow-up {start_follow_up}, handoff ready {start_handoff}

### Claude Print-Mode Proxy

- Ran: {claude_ran}
- Simulation tier: {claude_tier}
- Proxy notice: {claude_notice}
- Session ID preserved: {claude_session}
- Rubric: {rubric_summary}
- Transcript excerpts: {claude_transcript}

### Repo Boundary Check

- Business repo changed files after run:

```text
{state.fixture_status_after.strip() or "(clean)"}
```

- Engine repo unexpected changes: {state.engine_status_after != state.engine_status_before}

### Failures / Follow-Up Issues

{bullet_list(state.failures) if state.failures else "- None recorded by the harness."}

### Warnings / Manual Follow-Up

{bullet_list(state.warnings) if state.warnings else "- None."}

Interactive Claude Code TUI smoke is still required for release-bearing runtime
claims. This harness labels `claude -p` evidence as proxy evidence only.
"""


def nested_get(payload: dict[str, Any], keys: tuple[str, ...]) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return "unknown"
        current = current.get(key)
    return current if current is not None else "unknown"


def result_status(state: HarnessState, label: str) -> str:
    for result in state.commands:
        if result.label == label:
            return "ok" if result.ok else f"exit {result.returncode}"
    return "not run"


def bullet_list(items: Sequence[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def write_summary(state: HarnessState, *, install_mode: str, mb_version: str) -> None:
    summary = {
        "ok": not state.failures,
        "failures": state.failures,
        "warnings": state.warnings,
        "root": str(state.root),
        "evidence_dir": str(state.evidence_dir),
        "fixture_repo": str(state.fixture_repo),
        "mb_path": str(state.mb_path),
        "commands": [command.summary() for command in state.commands],
        "claude": state.claude,
    }
    write_json(state.evidence_dir / "summary.json", summary)
    template = evidence_template(state, install_mode=install_mode, mb_version=mb_version)
    (state.evidence_dir / "evidence-template.md").write_text(template, encoding="utf-8")


def mb_version(state: HarnessState) -> str:
    result = run_command(
        state,
        "mb-version",
        [str(state.mb_path), "--version"],
        cwd=state.root,
    )
    return result.stdout.strip() or result.stderr.strip() or f"exit {result.returncode}"


def run_harness(args: argparse.Namespace) -> int:
    engine_repo = Path(args.engine_repo).resolve()
    created_temp_root = not bool(args.root)
    root = (
        Path(args.root).resolve()
        if args.root
        else Path(tempfile.mkdtemp(prefix="mainbranch-dogfood-"))
    )
    root.mkdir(parents=True, exist_ok=True)
    evidence_dir = Path(args.evidence_dir).resolve() if args.evidence_dir else root / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    fixture_repo = root / DEFAULT_FIXTURE_SLUG
    if fixture_repo.exists():
        raise ValueError(
            f"fixture repo already exists at {fixture_repo}; "
            "remove that directory or choose a fresh --root"
        )

    mb_path = install_mb(
        mode=args.install_mode,
        root=root,
        engine_repo=engine_repo,
        wheel=Path(args.wheel).resolve() if args.wheel else None,
        pypi_version=args.pypi_version,
    )

    state = HarnessState(
        engine_repo=engine_repo,
        root=root,
        evidence_dir=evidence_dir,
        fixture_repo=fixture_repo,
        mb_path=mb_path,
    )
    state.engine_status_before = git_text(engine_repo, "status", "--short")
    (evidence_dir / "git").mkdir(parents=True, exist_ok=True)
    (evidence_dir / "git" / "engine-status-before.txt").write_text(
        state.engine_status_before,
        encoding="utf-8",
    )

    version = mb_version(state)
    exit_code = 0
    try:
        setup_fixture(state)
        run_cli_checks(state)
        if args.run_claude_print:
            run_claude_print(
                state,
                max_budget_usd=args.max_budget_usd,
                simulation_tier=args.simulation_tier,
            )
    finally:
        collect_post_run_state(state)
        write_summary(state, install_mode=args.install_mode, mb_version=version)

    print(f"Evidence folder: {state.evidence_dir}")
    print(f"Evidence template: {state.evidence_dir / 'evidence-template.md'}")
    if state.failures:
        print("Failures:", file=sys.stderr)
        for failure in state.failures:
            print(f"  - {failure}", file=sys.stderr)
        exit_code = 1
    if state.warnings:
        print("Warnings:")
        for warning in state.warnings:
            print(f"  - {warning}")
    if args.cleanup and exit_code == 0:
        if created_temp_root:
            shutil.rmtree(root, ignore_errors=True)
            print(f"Cleaned up temp root: {root}")
        else:
            print(
                f"--cleanup only removes auto-created temp roots; explicit --root remains: {root}"
            )
    return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create a sanitized Main Branch business fixture, run deterministic "
            "Claude runtime dogfood checks, and write public-safe evidence."
        )
    )
    parser.add_argument(
        "--install-mode",
        choices=("editable", "wheel", "pypi"),
        default="editable",
        help="How to install the mb package under test into the temp venv.",
    )
    parser.add_argument(
        "--engine-repo",
        default=str(repo_root_from_module()),
        help="Main Branch engine checkout. Used for editable install and boundary checks.",
    )
    parser.add_argument("--wheel", default="", help="Wheel path for --install-mode wheel.")
    parser.add_argument("--pypi-version", default="", help="Version for --install-mode pypi.")
    parser.add_argument("--root", default="", help="Optional temp root to reuse or inspect.")
    parser.add_argument("--evidence-dir", default="", help="Optional evidence output directory.")
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help=(
            "Remove the auto-created temp root after a successful run. Explicit "
            "--root directories are never deleted."
        ),
    )
    parser.add_argument(
        "--run-claude-print",
        action="store_true",
        help="Run optional chained claude -p print-mode proxy smoke.",
    )
    parser.add_argument(
        "--simulation-tier",
        choices=("pr_smoke", "prerelease_candidate", "release_acceptance"),
        default="pr_smoke",
        help=(
            "Release simulation prompt tier for --run-claude-print. "
            "PR smoke is intentionally short; release tiers remain proxy evidence."
        ),
    )
    parser.add_argument(
        "--max-budget-usd",
        default=DEFAULT_CLAUDE_BUDGET,
        help="Budget cap passed to claude -p when --run-claude-print is enabled.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run_harness(args)
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"dogfood harness failed before evidence completion: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
