"""``mb think <topic>`` — invocation hint for /think.

The actual /think skill runs inside Claude Code. This subcommand exists
so the umbrella feels complete from outside Claude Code: it points the
operator at the right thing.
"""

from __future__ import annotations

import os
import sys


def run(topic: str) -> None:
    """Print invocation hint for /think."""
    in_cc = bool(os.environ.get("CLAUDE_CODE_SESSION") or os.environ.get("CLAUDECODE"))
    msg = (
        f"To run /think on '{topic}':\n\n"
        "  1. cd into your business repo\n"
        "  2. Run: claude\n"
        "  3. In Claude Code, type:\n"
        f"       /think {topic}\n\n"
        "The /think skill ships with the engine; "
        "ensure your repo's .claude/settings.local.json points at the engine path."
    )
    if in_cc:
        msg = (
            f"Looks like you're in Claude Code already. Just type /think {topic} "
            "in the conversation."
        )
    print(msg, file=sys.stdout)
