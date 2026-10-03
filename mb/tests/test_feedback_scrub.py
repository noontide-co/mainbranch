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
