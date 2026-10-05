"""`write_agents_md` never deletes what a person wrote (#1052).

The Codex AGENTS.md repair replaces only Main Branch's own guidance: the text
between the managed markers, or an older generated file recognised by the
template hash its metadata names. Transitional repo-local Codex paths lose only
the files `mb` wrote there.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mb import codex as codex_mod

NOTE = "## Our team rules\n\nShip on Fridays only after the owner says yes.\n"


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    target = tmp_path / "biz"
    target.mkdir()
    (target / "CLAUDE.md").write_text("# Acme\n", encoding="utf-8")
    return target


def _agents(repo: Path) -> str:
    return (repo / "AGENTS.md").read_text(encoding="utf-8")


def _old_generated(repo: Path, template: str | None = None) -> str:
    """AGENTS.md as `mb` wrote it before the managed markers: the whole file."""
    source = template if template is not None else codex_mod._read_template("AGENTS.md.tmpl")
    digest = codex_mod.guidance_template_hash(source)
    return codex_mod._render(
        source,
        {
            "BUSINESS_NAME": "Acme",
            "GH_USERNAME": "acme-owner",
            "CODEX_GUIDANCE_METADATA": codex_mod.guidance_metadata_comment(template_hash=digest),
        },
    )


def _current_block(repo: Path) -> str:
    rendered = codex_mod.render_agents_md(repo, name="Acme", gh_username="acme-owner")
    return codex_mod._managed_agents_block(rendered)


# --- Case A: an older generated file with a person's additions ---------------


def test_case_a_old_generated_file_keeps_the_persons_section(repo: Path) -> None:
    (repo / "AGENTS.md").write_text(_old_generated(repo) + "\n" + NOTE, encoding="utf-8")

    codex_mod.write_agents_md(repo, name="Acme", gh_username="acme-owner")

    text = _agents(repo)
    assert NOTE in text
    assert text.startswith(_current_block(repo))
    assert text.count("<!-- mainbranch:codex-guidance schema=") == 1
    assert text.count("## Repo Owner") == 1
    assert codex_mod.instructions_status(repo)["ok"] is True


def test_case_a_recognises_an_older_template_and_keeps_text_on_both_sides(
    repo: Path,
) -> None:
    current = codex_mod._read_template("AGENTS.md.tmpl")
    older = current.replace("## Linking\n", "## Links\n", 1)
    assert older != current
    old_text = _old_generated(repo, older)
    (repo / "AGENTS.md").write_text("Read me first.\n\n" + old_text + "\n" + NOTE, encoding="utf-8")

    result = codex_mod.write_agents_md(repo, name="Acme", gh_username="acme-owner")

    text = _agents(repo)
    assert result["refused"] == []
    assert text.startswith(_current_block(repo))
    assert "Read me first." in text
    assert NOTE in text
    assert "## Links\n" not in text


def test_case_a_edited_generated_text_is_refused_and_left_alone(repo: Path) -> None:
    edited = _old_generated(repo).replace("## Linking\n", "## Linking\n\nOur own rule.\n", 1)
    before = edited + "\n" + NOTE
    (repo / "AGENTS.md").write_text(before, encoding="utf-8")

    result = codex_mod.write_agents_md(repo, name="Acme", gh_username="acme-owner")

    assert _agents(repo) == before
    assert result["ok"] is False
    assert result["changed"] is False
    assert [item["code"] for item in result["refused"]] == ["unrecognised_generated_text"]
    assert codex_mod.AGENTS_MANAGED_BEGIN in result["refused"][0]["manual_step"]


def test_case_a_fully_generated_old_file_is_replaced_cleanly(repo: Path) -> None:
    (repo / "AGENTS.md").write_text(_old_generated(repo), encoding="utf-8")

    result = codex_mod.write_agents_md(repo, name="Acme", gh_username="acme-owner")

    assert result["changed"] is True
    assert _agents(repo) == _current_block(repo)


# --- Case B: a begin marker without an end marker ----------------------------


def test_case_b_missing_end_marker_is_refused(repo: Path) -> None:
    block = _current_block(repo).replace(codex_mod.AGENTS_MANAGED_END + "\n", "")
    before = block + "\n" + NOTE
    (repo / "AGENTS.md").write_text(before, encoding="utf-8")

    codex_mod.write_agents_md(repo, name="Acme", gh_username="acme-owner")

    assert _agents(repo) == before


def test_case_b_refusal_names_the_manual_repair(repo: Path) -> None:
    block = _current_block(repo).replace(codex_mod.AGENTS_MANAGED_END + "\n", "")
    (repo / "AGENTS.md").write_text(block + "\n" + NOTE, encoding="utf-8")

    plan = codex_mod.agents_md_plan(repo, name="Acme", gh_username="acme-owner")

    assert plan["operations"] == []
    assert [item["code"] for item in plan["refused"]] == ["missing_end_marker"]
    assert codex_mod.AGENTS_MANAGED_END in plan["refused"][0]["manual_step"]
    action = codex_mod.agents_md_operator_action(plan)
    assert action is not None
    assert action["id"] == "codex-agents-md"
    assert action["command"] == codex_mod.CODEX_REPAIR_COMMAND
    assert action["manual_step"] == plan["refused"][0]["manual_step"]


@pytest.mark.parametrize(
    ("damage", "code"),
    [
        ("drop_begin", "missing_begin_marker"),
        ("two_blocks", "marker_mismatch"),
        ("reversed", "marker_mismatch"),
    ],
)
def test_other_broken_marker_layouts_are_refused(repo: Path, damage: str, code: str) -> None:
    block = _current_block(repo)
    begin, end = codex_mod.AGENTS_MANAGED_BEGIN, codex_mod.AGENTS_MANAGED_END
    if damage == "drop_begin":
        before = NOTE + "\n" + block.replace(begin + "\n", "")
    elif damage == "two_blocks":
        before = block + "\n" + NOTE + "\n" + block
    else:
        before = f"{end}\n{NOTE}\n{begin}\n"
    (repo / "AGENTS.md").write_text(before, encoding="utf-8")

    result = codex_mod.write_agents_md(repo, name="Acme", gh_username="acme-owner")

    assert _agents(repo) == before
    assert [item["code"] for item in result["refused"]] == [code]


def test_a_refused_agents_md_also_leaves_transitional_paths(repo: Path) -> None:
    block = _current_block(repo).replace(codex_mod.AGENTS_MANAGED_END + "\n", "")
    (repo / "AGENTS.md").write_text(block + "\n" + NOTE, encoding="utf-8")
    skill = repo / ".agents" / "skills" / "main-branch" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(codex_mod.render_codex_global_skill_md("main-branch"), encoding="utf-8")

    result = codex_mod.write_agents_md(repo, name="Acme", gh_username="acme-owner")

    assert result["changed_paths"] == []
    assert skill.is_file()


# --- Case C: transitional repo-local Codex paths -----------------------------


def test_case_c_persons_file_in_a_transitional_path_survives(repo: Path) -> None:
    (repo / "AGENTS.md").write_text(_current_block(repo), encoding="utf-8")
    folder = repo / ".agents" / "skills" / "main-branch"
    folder.mkdir(parents=True)
    (folder / "my-notes.md").write_text("Notes I wrote myself.\n", encoding="utf-8")
    (folder / "SKILL.md").write_text(
        codex_mod.render_codex_global_skill_md("main-branch"), encoding="utf-8"
    )

    codex_mod.write_agents_md(repo, name="Acme", gh_username="acme-owner")

    assert (folder / "my-notes.md").read_text(encoding="utf-8") == "Notes I wrote myself.\n"
    assert not (folder / "SKILL.md").exists()


def test_case_c_plan_deletes_only_mb_files_and_reports_the_rest(repo: Path) -> None:
    (repo / "AGENTS.md").write_text(_current_block(repo), encoding="utf-8")
    folder = repo / ".agents" / "skills" / "main-branch"
    folder.mkdir(parents=True)
    (folder / "my-notes.md").write_text("Notes I wrote myself.\n", encoding="utf-8")
    (folder / "SKILL.md").write_text("A skill I wrote.\n", encoding="utf-8")
    (folder / "commands").mkdir()
    (folder / "commands" / "mb-start.md").write_text("Main Branch start.\n", encoding="utf-8")

    plan = codex_mod.agents_md_plan(repo)

    assert [(item["op"], item["rel"]) for item in plan["operations"]] == [
        ("delete", ".agents/skills/main-branch/commands/mb-start.md")
    ]
    assert plan["kept"] == [
        ".agents/skills/main-branch/SKILL.md",
        ".agents/skills/main-branch/my-notes.md",
    ]
    action = codex_mod.agents_md_operator_action(plan)
    assert action is not None
    assert ".agents/skills/main-branch/my-notes.md" in action["reason"]

    codex_mod.write_agents_md(repo)

    assert (folder / "SKILL.md").is_file()
    assert (folder / "my-notes.md").is_file()
    assert not (folder / "commands").exists()


def _write_repo_local_era_files(repo: Path) -> list[Path]:
    """The repo-local Codex files `mb` 0.3.2x wrote, in their shape."""
    skill_md = (
        "---\nname: main-branch-owner-loop\ndescription: >-\n  Main Branch owner loop.\n---\n\n"
        "# Main Branch owner loop for Codex\n\nThis is a Codex-native skill generated by `mb`.\n"
    )
    plugin = {
        "name": "main-branch-owner-loop",
        "version": "0.1.0",
        "homepage": "https://github.com/noontide-co/mainbranch",
        "repository": "https://github.com/noontide-co/mainbranch",
    }
    marketplace = {
        "name": "main-branch-local",
        "plugins": [{"name": "main-branch-owner-loop", "source": {"source": "local"}}],
    }
    files = {
        ".agents/skills/main-branch-owner-loop/SKILL.md": skill_md,
        ".agents/skills/main-branch-owner-loop/references/workflow-inventory.md": (
            "# Main Branch Codex Workflow Inventory\n\nGenerated by `mb`.\n"
        ),
        ".agents/plugins/marketplace.json": json.dumps(marketplace, indent=2) + "\n",
        ".agents/plugins/main-branch-owner-loop/.codex-plugin/plugin.json": (
            json.dumps(plugin, indent=2) + "\n"
        ),
        ".agents/plugins/main-branch-owner-loop/skills/main-branch-owner-loop/SKILL.md": (skill_md),
        ".agents/plugins/main-branch-owner-loop/commands/mb-start.md": (
            "---\ndescription: Start\n---\n\n# /mb-start\n\nUse the Main Branch owner-loop skill.\n"
        ),
    }
    written = []
    for relative, text in files.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        written.append(path)
    return written


def test_fully_generated_transitional_paths_are_removed_whole(repo: Path) -> None:
    (repo / "AGENTS.md").write_text(_current_block(repo), encoding="utf-8")
    _write_repo_local_era_files(repo)

    plan = codex_mod.agents_md_plan(repo)

    assert plan["kept"] == []
    assert codex_mod.agents_md_operator_action(plan) is None
    assert {item["op"] for item in plan["operations"]} == {"delete_tree"}

    codex_mod.write_agents_md(repo)

    assert not (repo / ".agents").exists()


def test_a_folder_holding_a_persons_file_is_not_removed(repo: Path) -> None:
    (repo / "AGENTS.md").write_text(_current_block(repo), encoding="utf-8")
    _write_repo_local_era_files(repo)
    mine = repo / ".agents" / "plugins" / "my-plugin.json"
    mine.write_text('{"name": "mine"}\n', encoding="utf-8")

    codex_mod.write_agents_md(repo)

    assert mine.is_file()
    assert not (repo / ".agents" / "plugins" / "marketplace.json").exists()
    assert not (repo / ".agents" / "skills").exists()


def test_a_person_written_marketplace_file_is_kept(repo: Path) -> None:
    (repo / "AGENTS.md").write_text(_current_block(repo), encoding="utf-8")
    marketplace = repo / ".agents" / "plugins" / "marketplace.json"
    marketplace.parent.mkdir(parents=True)
    marketplace.write_text('{"name": "team-tools", "plugins": []}\n', encoding="utf-8")

    plan = codex_mod.agents_md_plan(repo)
    codex_mod.write_agents_md(repo)

    assert plan["kept"] == [".agents/plugins/marketplace.json"]
    assert marketplace.is_file()


# --- Unchanged behaviour ------------------------------------------------------


def test_normal_in_marker_refresh_keeps_text_outside_the_markers(repo: Path) -> None:
    stale = (
        f"Intro.\n\n{codex_mod.AGENTS_MANAGED_BEGIN}\nold guidance\n"
        f"{codex_mod.AGENTS_MANAGED_END}\n\n{NOTE}"
    )
    (repo / "AGENTS.md").write_text(stale, encoding="utf-8")

    result = codex_mod.write_agents_md(repo, name="Acme", gh_username="acme-owner")

    assert result["ok"] is True
    assert _agents(repo) == "Intro.\n\n" + _current_block(repo) + "\n" + NOTE
    plan = codex_mod.agents_md_plan(repo, name="Acme", gh_username="acme-owner")
    assert plan == {"operations": [], "refused": [], "kept": []}


def test_plain_file_gets_the_block_in_front(repo: Path) -> None:
    (repo / "AGENTS.md").write_text(NOTE, encoding="utf-8")

    codex_mod.write_agents_md(repo, name="Acme", gh_username="acme-owner")

    assert _agents(repo) == _current_block(repo) + "\n" + NOTE


@pytest.mark.parametrize("existing", ["", "\n\n", None])
def test_empty_or_missing_file_gets_just_the_block(repo: Path, existing: str | None) -> None:
    if existing is not None:
        (repo / "AGENTS.md").write_text(existing, encoding="utf-8")

    result = codex_mod.write_agents_md(repo, name="Acme", gh_username="acme-owner")

    assert result["ok"] is True
    assert _agents(repo) == _current_block(repo)
