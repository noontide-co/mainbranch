"""``mb think <topic>`` — invocation hint for /mb-think.

The actual /mb-think skill runs inside Claude Code. This subcommand exists
so the umbrella feels complete from outside Claude Code: it points the
operator at the right thing.
"""

from __future__ import annotations

import os
import sys


def run(topic: str) -> None:
    """Print invocation hint for /mb-think."""
    in_cc = bool(os.environ.get("CLAUDE_CODE_SESSION") or os.environ.get("CLAUDECODE"))
    msg = (
        f"To run /mb-think on '{topic}':\n\n"
        "  1. cd into your business repo\n"
        "  2. Run: claude\n"
        "  3. In Claude Code, type:\n"
        f"       /mb-think {topic}\n\n"
        "The /mb-think skill ships with the engine; "
        "ensure your repo's .claude/settings.local.json points at the engine path."
    )
    if in_cc:
        msg = (
            f"Looks like you're in Claude Code already. Just type /mb-think {topic} "
            "in the conversation."
        )
    print(msg, file=sys.stdout)
