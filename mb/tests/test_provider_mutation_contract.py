"""#656: the provider-mutation contract is documented, exampled, and routed."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")


def test_provider_mutation_contract_page_defines_the_five_steps() -> None:
    doc = _read("docs/provider-mutation-contract.md").lower()
    # The preview -> approve -> apply -> verify spine.
    assert "read-only discovery first" in doc
    assert "mutation plan" in doc
    assert "explicit operator approval" in doc
    assert "minimal scope" in doc
    assert "verify" in doc and "private-safe summary" in doc


def test_provider_mutation_contract_has_a_plan_apply_example() -> None:
    doc = _read("docs/provider-mutation-contract.md").lower()
    # Acceptance criterion: at least one concrete plan/apply example.
    assert "plan" in doc and "apply --approve" in doc
    assert "count: 42" in doc or "count:" in doc
    assert "risk:" in doc


def test_provider_mutation_contract_keeps_private_data_out() -> None:
    doc = _read("docs/provider-mutation-contract.md").lower()
    # The secrets/rows-out-of-git rule is explicit.
    assert "never enter a public or git artifact" in doc or "out of git" in doc
    assert "tokens" in doc and ("customer rows" in doc or "customer" in doc)
    # Reads and writes are separated.
    assert "read vs write" in doc or "read paths" in doc


def test_provider_mutation_contract_is_indexed_and_cross_linked() -> None:
    index = _read("docs/README.md")
    assert "provider-mutation-contract.md" in index
    # Sibling doctrine cross-links to it.
    assert "provider-mutation-contract.md" in _read("docs/delivery-truth.md")


def test_provider_mutation_contract_routed_on_codex_rail() -> None:
    template = " ".join(_read("mb/mb/_data/templates/AGENTS.md.tmpl").lower().split())
    assert "provider-mutation-contract.md" in template
    assert "read-only discovery first" in template
    assert "writing to an external provider" in template
