"""Adversarial matrix for the ``mb feedback`` scrubber (#986, review round 3).

Every hostile case runs through all four stored fields: feedback text,
feedback command, refusal rule and refusal command. Values are synthetic
canaries; nothing here is a real credential or a real path.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from mb import feedback as feedback_mod

CANARY = "Zq7canary" + "0123456789abcdef"
PATH_MARKER = "private-project"

# Keys whose value must be redacted: any segment is a secret word.
SECRET_KEYS = [
    "access_token_v2",
    "client_secret_new",
    "password_confirmation",
    "token_value_backup",
    "secret_base",
    "SECRET_KEY",
    "accessToken",
    "apiKey",
    "x-api-key",
    "AWS_SECRET_ACCESS_KEY",
    "session_cookie",
    "authHeader",
    "private_key_pem",
    "db_password_hash",
    "MY_PWD",
    "credentials_blob",
    "bearerValue",
    "X-Amz-Signature",
    "sig",
    "passphrase",
]
KEY_FORMS = [
    "{k}={v}",
    "{k}: {v}",
    '{{"{k}": "{v}"}}',
    'export {k}="pre fix;{v}"',
    "https://x.test/cb?a=1&{k}={v}",
    "--{k} {v}",
]

QUOTE_SHAPES = {
    "multiline_double": f'X_TOKEN="line one\nline two {CANARY}"',
    "backslash_newline": f'X_TOKEN="part one \\\n{CANARY}"',
    "adjacent_fragments": f"X_TOKEN=\"a\"'b'{CANARY}",
    "json_nested_quotes": f'{{"token": "it\'s \\"q\\" {CANARY}"}}',
    "backtick": f"X_TOKEN=`{CANARY}`",
    "unterminated": f'X_TOKEN="unterminated {CANARY}',
    "single_multiline_with_double": f"X_SECRET='a \"b\" c\n{CANARY}'",
    "mismatched_quotes": f"X_TOKEN=\"abc' {CANARY}",
}

PATH_SHAPES = {
    "quoted_unix_apostrophe": f'"/srv/it\'s {PATH_MARKER}/x.yaml"',
    "single_quoted_unix_double": f"'/srv/say \"hi\" {PATH_MARKER}/x.yaml'",
    "quoted_windows_mixed": f'"C:\\Users\\a\'b/{PATH_MARKER}\\x.cfg"',
    "quoted_unc_double": f"'\\\\fileserver\\it\"s\\{PATH_MARKER}\\x'",
    "quoted_multiline": f'"/srv/multi\nline/{PATH_MARKER}/x"',
    "quoted_unterminated": f'"/srv/unterminated {PATH_MARKER}/x',
    "file_url": f"file:///srv/{PATH_MARKER}/x.yaml",
    "after_equals": f"--repo=/srv/{PATH_MARKER}/x",
    "after_paren": f"(/srv/{PATH_MARKER}/x)",
    "after_bracket": f"[/srv/{PATH_MARKER}/x]",
    "forward_drive": f"C:/{PATH_MARKER}/x.cfg",
    "quoted_forward_unc": f"'//fileserver/{PATH_MARKER}/x y'",
}

BENIGN = [
    "git@github.com:org/repo.git",
    "https://x.test//y/z",
    "see docs/a/b.md and ./core/offer.md",
    "ratio 3/4/5, and/or",
    "run /mb-start then /mb-end",
    "the token flow is confusing",
    "https://example.test/?token_count=25&page=2",
    "max_tokens=100 tokens_used: 1200",
    "tokenizer=bpe token_type=bearer",
    "author=Ana design=x signed=yes",
    "it's fine, don't worry",
    '"https://example.test/a/b"',
    "file://x.test/a/b",
    '{"name": "Main Branch", "count": 3}',
    "Note: status said ready",
    "'/mb-start' and \"/mb-end\"",
]


def _key_cases() -> dict[str, str]:
    return {
        f"{key}|{form}": form.format(k=key, v=CANARY) for key in SECRET_KEYS for form in KEY_FORMS
    }


SECRET_CASES = {**_key_cases(), **QUOTE_SHAPES}


def _stored_fields(state: Path, value: str) -> list[str]:
    log = state / "mainbranch" / "feedback.jsonl"
    if log.exists():
        log.unlink()
    feedback_mod.record(f"saw {value} here", command=f"mb connect {value}")
    assert feedback_mod.record_refusal(f"rule {value}", f"mb connect {value}")
    entries: list[dict[str, Any]] = [
        json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()
    ]
    return [entries[0]["text"], entries[0]["command"], entries[1]["rule"], entries[1]["command"]]


@pytest.fixture
def state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    return tmp_path / "state"


@pytest.mark.parametrize("case", sorted(SECRET_CASES))
def test_secret_case_is_redacted_in_all_four_fields(state: Path, case: str) -> None:
    for index, value in enumerate(_stored_fields(state, SECRET_CASES[case])):
        assert CANARY not in value, (case, index)


@pytest.mark.parametrize("case", sorted(PATH_SHAPES))
def test_path_case_is_scrubbed_in_all_four_fields(state: Path, case: str) -> None:
    for index, value in enumerate(_stored_fields(state, PATH_SHAPES[case])):
        assert PATH_MARKER not in value, (case, index, value)
        if index == 0:  # command and rule are structured, not scrubbed text
            assert "<local-path>" in value, (case, index, value)


@pytest.mark.parametrize("text", BENIGN)
def test_benign_text_is_unchanged(text: str) -> None:
    assert feedback_mod.scrub(text) == text


@pytest.mark.parametrize("key", ["token_count", "max_tokens", "tokenizer", "maxTokens"])
def test_allowlisted_metadata_keys_keep_values(key: str) -> None:
    assert feedback_mod.scrub(f"{key}=25") == f"{key}=25"


def test_colon_led_unc_is_a_documented_limit() -> None:
    # ``x://server/share`` cannot be told apart from a URL without context, so
    # it stays as written; docs/feedback.md records this.
    assert feedback_mod.scrub("smb://fileserver/share/x") == "smb://fileserver/share/x"


# --- Round 4: realistic leak families in free text -------------------------

YAML_SHAPES = {
    "literal_block": f"password: |\n  {CANARY}\n  more\nnext: 1",
    "folded_block_chomp": f"api_key: >-\n  {CANARY}\n  continued",
    "next_line_plain": f"token:\n  {CANARY}",
    "indented_keep": f"config:\n  secret_key: |+\n    {CANARY}\n",
    "list_item_block": f"- auth_token: |\n    line\n    {CANARY}",
    "quoted_key_block": f'"password": |\n  {CANARY}',
}
HEADER_SHAPES = {
    "digest": f'Authorization: Digest username="u", realm="r", response="{CANARY}"',
    "cookie_pairs": f"Cookie: theme=dark; sid={CANARY}; csrftoken={CANARY}",
    "set_cookie": f"Set-Cookie: sid={CANARY}; Path=/; HttpOnly",
    "proxy_basic": f"Proxy-Authorization: Basic {CANARY}",
    "custom_secret_header": f"X-Api-Key: abc {CANARY}",
    "curl_single_quoted_cookie": f"curl -H 'Cookie: a=1; csrf={CANARY}' https://x.test",
    "curl_double_quoted_digest": f'curl -H "Authorization: Digest response=\\"{CANARY}\\"" x',
}
FLAG_SHAPES = {
    "dash_leading_value": f"--password -{CANARY}",
    "next_line_value": f"--api-key\n  {CANARY}",
    "equals_value": f"mb x --client-secret={CANARY}",
    "continuation_value": f"--auth-token \\\n {CANARY}",
}
ESCAPE_SHAPES = {
    "escaped_space_semicolon": f"password=abc\\ def\\;{CANARY}",
    "export_escaped_spaces": f"export TOKEN=a\\ b\\ {CANARY}",
}
ROUND4_SECRET_SHAPES = {**YAML_SHAPES, **HEADER_SHAPES, **FLAG_SHAPES, **ESCAPE_SHAPES}
ROUND4_PATH_SHAPES = {
    "quoted_file_url_space": f'"file:///srv/my dir/{PATH_MARKER}/x"',
    "quoted_file_url_apostrophe": f'"file:///srv/it\'s dir/{PATH_MARKER}/x"',
    "quoted_first_segment_space": f'"/my project/{PATH_MARKER}/x"',
    "quoted_first_segment_apostrophe": f'"/it\'s here/{PATH_MARKER}/x"',
    "bare_escaped_space": f"/srv/my\\ project/{PATH_MARKER}/x",
}
BENIGN_EXTRA = [
    "Cookie banners are confusing",
    "the Authorization header was missing",
    "see `mb connect test` for details",
    "[docs](https://x.test/a/b)",
    "status: ready",
    "Accept: application/json",
    "Content-Type: text/plain",
    "mb status --json --repo .",
    "use --dry-run first",
    "line one\nline two",
    "name: |\n  some prose here",
]


@pytest.mark.parametrize("case", sorted(ROUND4_SECRET_SHAPES))
def test_round4_secret_case_is_redacted_in_all_four_fields(state: Path, case: str) -> None:
    for index, value in enumerate(_stored_fields(state, ROUND4_SECRET_SHAPES[case])):
        assert CANARY not in value, (case, index)


@pytest.mark.parametrize("case", sorted(ROUND4_PATH_SHAPES))
def test_round4_path_case_is_scrubbed_in_all_four_fields(state: Path, case: str) -> None:
    for index, value in enumerate(_stored_fields(state, ROUND4_PATH_SHAPES[case])):
        assert PATH_MARKER not in value, (case, index, value)


@pytest.mark.parametrize("text", BENIGN_EXTRA)
def test_round4_benign_text_is_unchanged(text: str) -> None:
    assert feedback_mod.scrub(text) == text


# --- Round 5: YAML headers with comments, tags, anchors ---------------------

YAML_ROUND5_SHAPES = {
    "literal_with_comment": f"password: | # note\n  {CANARY}\nnext: 1",
    "folded_strip_with_comment": f"api_key: >- # rotated monthly\n  {CANARY}\n  continued",
    "next_line_after_comment_line": f"token: # prod\n  # the prod one\n  {CANARY}",
    "next_line_after_outdented_comment": f"token:\n# the prod one\n  {CANARY}",
    "str_tag_next_line": f"secret: !!str\n  {CANARY}",
    "anchor_literal": f"token: &tok |\n  {CANARY}",
    "list_item_api_key": f"- api_key: | # primary\n    {CANARY}",
    "nested_list_item_anchor": f"keys:\n  - name: a\n    api_key: &k >-\n      {CANARY}",
    "tag_and_anchor_block": f"client_secret: !secret &s >+2\n    {CANARY}\n",
    "verbatim_tag_indent_first": f"password: !<tag:x.test,2026:s> |2-\n   {CANARY}",
    "blank_and_comment_inside_block": f"password: |\n  a\n\n  # x\n  {CANARY}",
    "crlf_header_with_comment": f"password: | # note\r\n  {CANARY}\r\nnext: 1",
    "inline_after_tag": f"password: !!str {CANARY}",
    "inline_after_anchor": f"token: &tok {CANARY}",
}
YAML_ROUND5_BENIGN = [
    "name: | # the title\n  some prose here\nnext: 1",
    "description: >- # folded\n  one\n  two",
    "base: &defaults\n  retries: 3\nservice:\n  <<: *defaults",
    "label: !!str\n  plain words",
    "items:\n  # first\n  - a\n  - b",
]


@pytest.mark.parametrize("case", sorted(YAML_ROUND5_SHAPES))
def test_round5_yaml_case_is_redacted_in_all_four_fields(state: Path, case: str) -> None:
    for index, value in enumerate(_stored_fields(state, YAML_ROUND5_SHAPES[case])):
        assert CANARY not in value, (case, index)


@pytest.mark.parametrize("text", YAML_ROUND5_BENIGN)
def test_round5_ordinary_yaml_is_unchanged(text: str) -> None:
    assert feedback_mod.scrub(text) == text


def test_yaml_block_stops_at_the_key_indentation() -> None:
    scrubbed = feedback_mod.scrub(f"password: | # note\n  {CANARY}\nname: kept")
    assert CANARY not in scrubbed
    assert scrubbed.endswith("\nname: kept")


# --- Round 6: indentless sequences, flow collections, plain continuations, ? keys

YAML_ROUND6_SHAPES = {
    "indentless_sequence": f"credentials:\n- {CANARY}\n- other\nnext: 1",
    "indentless_nested_items": (
        f"config:\n  tokens: # rotated\n  - name: a\n    value: {CANARY}\n  size: 2"
    ),
    "flow_map_nested": f"credentials: {{primary: {{user: u, pass: {CANARY}}}}}",
    "flow_map_with_props": f"auth: !!map &a {{primary: '{CANARY}'}}",
    "flow_sequence_multiline": f"secrets: [\n  a,\n  {CANARY}\n]",
    "plain_continuation": f"password: first\n  {CANARY}\nname: kept",
    "plain_continuation_tagged": f"password: !!str first\n  {CANARY}",
    "plain_continuation_list_item": f"- token: abc\n    {CANARY}\n- name: kept",
    "explicit_key_inline": f"? password\n: {CANARY}",
    "explicit_key_block": f"? api_key\n:\n  {CANARY}",
    "explicit_key_comment_flow": f"? token # k\n: [a,\n  {CANARY}]",
    "explicit_key_in_list": f"- ? secret\n  : {CANARY}",
}
YAML_ROUND6_BENIGN = [
    "items:\n- a\n- b\nnext: 1",
    "config: {name: x, size: 2}",
    "description: first line\n  second line\nname: y",
    "? name\n: value",
]


@pytest.mark.parametrize("case", sorted(YAML_ROUND6_SHAPES))
def test_round6_yaml_case_is_redacted_in_all_four_fields(state: Path, case: str) -> None:
    for index, value in enumerate(_stored_fields(state, YAML_ROUND6_SHAPES[case])):
        assert CANARY not in value, (case, index)


@pytest.mark.parametrize("text", YAML_ROUND6_BENIGN)
def test_round6_ordinary_yaml_is_unchanged(text: str) -> None:
    assert feedback_mod.scrub(text) == text


def test_round6_blocks_stop_at_sibling_keys() -> None:
    for shape in ("plain_continuation", "plain_continuation_list_item"):
        scrubbed = feedback_mod.scrub(YAML_ROUND6_SHAPES[shape])
        assert scrubbed.endswith("name: kept"), shape
    assert feedback_mod.scrub(YAML_ROUND6_SHAPES["indentless_sequence"]).endswith("\nnext: 1")


# --- Round 4: linear time ----------------------------------------------------

TIMING_FAMILIES = {
    "dotted_run": "a." * 2000,
    "double_quotes": '"' * 4000,
    "single_quotes": "'" * 4000,
    "backslashes": "\\" * 4000,
    "slashes": "/" * 4000,
    "equals": "=" * 4000,
    "colon_pairs": "a:" * 2000,
    "secret_assignments": "token=" * 667,
    "quoted_paths": "'/a" * 1333,
    "secret_flags": "--token " * 500,
    "schemes": "a://" * 1000,
    "header_names": "X-Api-Key: " * 363,
    "yaml_keys": "password:\n" * 400,
    "yaml_headers": "token: !!str &a |2- # c\n" * 167,
    "yaml_flow": "token: {" * 500,
    "yaml_explicit": "? token\n" * 500,
    "yaml_indentless": "token:\n- a\n" * 364,
    "path_segments": "/a" * 2000,
    "escaped_spaces": "\\ " * 2000,
    "long_key": "a" * 3999 + ":",
}


@pytest.mark.parametrize("family", sorted(TIMING_FAMILIES))
def test_scrub_is_fast_on_adversarial_input(family: str) -> None:
    import time

    text = TIMING_FAMILIES[family]
    assert len(text) >= 3990
    started = time.perf_counter()
    feedback_mod.scrub(text)
    assert time.perf_counter() - started < 1.0, family


def test_record_caps_text_before_scrubbing(state: Path) -> None:
    import time

    started = time.perf_counter()
    result = feedback_mod.record("a." * 32000)
    assert time.perf_counter() - started < 1.0
    assert result["ok"] is True
    assert result["entry"]["text"].endswith(" [truncated]")
    assert len(result["entry"]["text"]) <= feedback_mod.MAX_TEXT_CHARS + len(" [truncated]")


def test_truncation_inside_a_quote_still_redacts(state: Path) -> None:
    filler = "x" * (feedback_mod.MAX_TEXT_CHARS - 20)
    result = feedback_mod.record(f'{filler} token="{CANARY} and more"')
    assert CANARY[:8] not in result["entry"]["text"]


def test_scanner_is_linear_on_a_long_dotted_run() -> None:
    import time

    from mb import feedback_scrub

    started = time.perf_counter()
    feedback_scrub.scrub("a." * 8000)
    assert time.perf_counter() - started < 1.0
