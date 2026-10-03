"""Scrub secrets and local paths out of ``mb feedback`` lines (#986).

The feedback file is local and never sent, and the agent rails already ask
for a credential-free summary. This is defence in depth, so the default is to
redact and only known-harmless forms survive:

- A ``key=value``, ``key: value``, ``"key": "value"`` or ``--key value``
  pair is redacted when any segment of the key (split on ``_``, ``-``, ``.``
  and case changes) is a secret word, unless the whole key is on a short
  allowlist of harmless metadata such as ``token_count``.
- Quoted text is read by one scanner that matches the opening quote to its
  closing twin, across lines, honouring backslash escapes. An unterminated
  quote runs to the end of the field. The same scanner reads secret values
  (adjacent quoted and bare fragments are one value) and quoted paths.
- Provider token shapes (GitHub, Slack, OpenAI, AWS and others), Bearer and
  Basic credentials and URL passwords are redacted wherever they appear.
- Home paths become ``~``; every other absolute path (Unix, ``file:///``,
  Windows drive with either slash, UNC with either slash, quoted or not)
  becomes ``<local-path>``. URLs, relative paths and slash commands stay.

Known limit: ``scheme://server/share`` with a colon is indistinguishable from
a URL, so it is left as written.
"""

from __future__ import annotations

import functools
import re
from pathlib import Path

REDACTED = "<redacted>"
LOCAL_PATH = "<local-path>"
QUOTES = "\"'`"

# A key is secret when any of its segments is one of these words.
SECRET_WORDS = frozenset(
    {
        "token",
        "tokens",
        "secret",
        "secrets",
        "password",
        "passwd",
        "pwd",
        "passphrase",
        "apikey",
        "credential",
        "credentials",
        "auth",
        "authorization",
        "signature",
        "sig",
        "session",
        "cookie",
        "bearer",
    }
)
# ... or when two adjacent segments are one of these pairs.
SECRET_PAIRS = frozenset({("api", "key"), ("private", "key"), ("access", "key")})
# Whole keys (lowercased, segments joined by ``_``) that are harmless metadata
# even though a segment is a secret word. Keep this short.
ALLOWED_KEYS = frozenset(
    {
        "token_count",
        "tokens_used",
        "max_tokens",
        "max_output_tokens",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "token_type",
        "token_limit",
        "tokenizer",
    }
)

_KEY = r"[A-Za-z_][A-Za-z0-9_.-]*"
# ``key=value``, ``key: value`` and ``"key": "value"``.
_PAIR_RE = re.compile(rf"(?<![A-Za-z0-9_.\-])([\"'`]?)({_KEY})\1([ \t]*[:=]=?[ \t]*)")
# ``--key value``, ``--key=value`` and ``--key`` with its value on the next
# line (also after a ``\`` continuation). The value may start with ``-``.
_FLAG_RE = re.compile(rf"(?<![\w-])--?({_KEY})(?:=|[ \t]*\\?\r?\n[ \t]*|[ \t]+)")
# ``Name: value`` HTTP headers. ``://`` is a URL, not a header.
_HEADER_RE = re.compile(
    r"(?<![A-Za-z0-9-])([A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*)[ \t]*:(?!//)[ \t]*"
)
SENSITIVE_HEADERS = frozenset(
    {"authorization", "proxy-authorization", "cookie", "set-cookie", "www-authenticate"}
)
# A YAML key whose value is a ``|``/``>`` block or sits on the indented lines below.
_YAML_KEY_RE = re.compile(
    rf"(?<![A-Za-z0-9_.\-])([\"']?)({_KEY})\1[ \t]*:[ \t]*(?:[|>][-+0-9]*)?[ \t]*\r?$"
)
_SEGMENT_RE = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+")
# Characters that end a bare (unquoted) value.
_VALUE_STOP = frozenset(";&,)]}<>|")

_CREDENTIAL_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?i)\b((?:basic|bearer)\s+)[A-Za-z0-9+/=._~-]{8,}"), rf"\1{REDACTED}"),
    # scheme://user:password@host
    # A scheme starts at a non-scheme character and is at most 32 long, so a
    # long ``a.a.a.`` run is not rescanned from every position.
    (
        re.compile(r"(?i)(?<![a-z0-9+.-])([a-z][a-z0-9+.-]{0,31}://[^\s:/@]+:)[^\s@/]+@"),
        rf"\1{REDACTED}@",
    ),
)
_TOKEN_RULES: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"(?<![\w-])(?:gh[pousr]_|github_pat_|glpat-|xox[abposr]-|"
        r"sk-(?:proj-|live-|test-)?|sk_(?:live|test)_|rk_(?:live|test)_|hf_|npm_|"
        r"pypi-|AIza|fal-)[A-Za-z0-9_-]{8,}"
    ),
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
)

_PATH_CHARS = r"[^\s\"'`<>|(),;\[\]]"
_OTHER_HOME_RE = re.compile(r"(?<![\w~])(?:/Users|/home)/[^/\s\"'`]+")
_FILE_URL_RE = re.compile(rf"(?i)\bfile:///{_PATH_CHARS}*")
# Windows drive paths with either slash, and UNC shares with either slash. A
# ``//`` after a colon or a word character is a URL, not a share.
_WINDOWS_PATH_RE = re.compile(
    rf"(?<![\w])[A-Za-z]:[\\/]{_PATH_CHARS}*"
    rf"|(?<![\w\\])\\\\[^\s\\\"'`<>|]+\\{_PATH_CHARS}*"
    rf"|(?<![\w:/])//[^\s/\"'`<>|]+/{_PATH_CHARS}*"
)
# Any absolute Unix path with at least two segments, including one right after
# a colon in error prose (``failed:/srv/x/y``). A URL's ``://`` is followed by a
# second slash, which no path segment starts with, so URLs are untouched; so
# are relative paths and a lone ``/mb-start`` slash command.
_UNIX_PATH_RE = re.compile(
    r"(?<![\w/.~\\-])/(?:(?:\\.|[^\s/\"'`<>|(),;\[\]\\])+/)+"
    r"(?:\\.|[^\s\"'`<>|(),;\[\]\\])*"
)
# What a quoted string must start with to be read as a path. The first Unix
# segment may hold spaces and the other quote; it ends at ``/``.
_QUOTED_PATH_START_RE = {
    quote: re.compile(
        rf"file:///|[A-Za-z]:[\\/]|\\\\|//|/[^/\n{re.escape(quote)}]+/", re.IGNORECASE
    )
    for quote in QUOTES
}


def quoted_end(text: str, start: int) -> int:
    """Index just past the quote that closes the one at ``start``.

    Matches the opening delimiter to its twin, across lines, skipping any
    backslash-escaped character (including a backslash-newline). An
    unterminated quote runs to the end of ``text``.
    """
    quote = text[start]
    index = start + 1
    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2
            continue
        if char == quote:
            return index + 1
        index += 1
    return len(text)


def value_end(text: str, start: int) -> int:
    """Index just past an assignment value starting at ``start``.

    Adjacent quoted and bare fragments (``"a"'b'c``) are one value; a bare
    fragment ends at unquoted, unescaped whitespace or a separator.
    """
    index = start
    while index < len(text):
        char = text[index]
        if char in QUOTES:
            index = quoted_end(text, index)
        elif char == "\\":
            # ``\ ``, ``\;`` and a backslash-newline continue the value.
            index += 2
        elif char.isspace() or char in _VALUE_STOP:
            break
        else:
            index += 1
    return index


def key_segments(key: str) -> list[str]:
    return [
        segment.lower()
        for part in re.split(r"[_.\-]+", key)
        for segment in _SEGMENT_RE.findall(part)
    ]


def is_secret_key(key: str) -> bool:
    segments = key_segments(key)
    if "_".join(segments) in ALLOWED_KEYS:
        return False
    if any(segment in SECRET_WORDS for segment in segments):
        return True
    return any(pair in SECRET_PAIRS for pair in zip(segments, segments[1:], strict=False))


def _redacted_value(value: str) -> str:
    quote = value[0] if value[:1] in tuple(QUOTES) else ""
    return f"{quote}{REDACTED}{quote}"


def _redact_values(text: str, pattern: re.Pattern[str], key_group: int) -> str:
    out: list[str] = []
    position = 0
    search_from = 0
    while True:
        match = pattern.search(text, search_from)
        if match is None:
            break
        if not is_secret_key(match.group(key_group)):
            search_from = match.end(key_group)
            continue
        start = match.end()
        end = value_end(text, start)
        if end == start:
            search_from = match.end()
            continue
        out.append(text[position:start])
        out.append(_redacted_value(text[start:end]))
        position = search_from = end
    out.append(text[position:])
    return "".join(out)


def _redact_headers(text: str) -> str:
    """Redact a sensitive header's whole value: every cookie pair, Digest field.

    The value runs to the end of the line, or to the closing quote when the
    header sits inside a quoted argument (``curl -H 'Cookie: ...'``).
    """
    out: list[str] = []
    position = 0
    search_from = 0
    while True:
        match = _HEADER_RE.search(text, search_from)
        if match is None:
            break
        name = match.group(1)
        lowered = name.lower()
        sensitive = lowered in SENSITIVE_HEADERS or ("-" in name and is_secret_key(name))
        if not sensitive:
            search_from = match.end(1)
            continue
        opening = match.start(1) - 1
        while opening >= 0 and text[opening] in " \t":
            opening -= 1
        line_end = text.find("\n", match.end())
        end = len(text) if line_end < 0 else line_end
        if opening >= 0 and text[opening] in QUOTES:
            closing = quoted_end(text, opening)
            closed = text[closing - 1 : closing] == text[opening] and closing - 1 > opening
            end = closing - 1 if closed else closing
        if end > match.end():
            out.append(text[position : match.end()])
            out.append(REDACTED)
            position = end
        search_from = max(end, match.end())
    out.append(text[position:])
    return "".join(out)


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" \t"))


def _redact_yaml_blocks(text: str) -> str:
    """Redact the indented block under a secret YAML key (``key: |`` or ``key:``)."""
    lines = text.split("\n")
    out: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        out.append(line)
        index += 1
        match = _YAML_KEY_RE.search(line)
        if match is None or not is_secret_key(match.group(2)):
            continue
        base = _indent(line)
        end = index
        last_content = index
        while end < len(lines) and (not lines[end].strip() or _indent(lines[end]) > base):
            if lines[end].strip():
                last_content = end + 1
            end += 1
        if last_content > index:
            out.append(" " * (base + 2) + REDACTED)
            index = last_content
    return "\n".join(out)


@functools.cache
def _connect_prefix_re() -> re.Pattern[str]:
    from mb.connect import CREDENTIAL_VALUE_PREFIXES

    return re.compile(
        r"(?<![\w-])(?:"
        + "|".join(re.escape(prefix) for prefix in CREDENTIAL_VALUE_PREFIXES)
        + r")[A-Za-z0-9_\-]{8,}"
    )


def scrub_secrets(text: str) -> str:
    # Imported here so connect can call ``record_refusal`` without an import cycle.
    from mb.connect import _redact_sensitive_text
    from mb.issue import QUERY_SECRET_RE, TOKEN_RE

    text = _redact_yaml_blocks(text)
    text = _redact_headers(text)
    for pattern, replacement in _CREDENTIAL_RULES:
        text = pattern.sub(replacement, text)
    text = _redact_values(text, _PAIR_RE, 2)
    text = _redact_values(text, _FLAG_RE, 1)
    for token_pattern in (*_TOKEN_RULES, _connect_prefix_re(), TOKEN_RE):
        text = token_pattern.sub(REDACTED, text)
    text = _redact_sensitive_text(text)
    return QUERY_SECRET_RE.sub(lambda match: f"{match.group(1)}{REDACTED}", text)


def _scrub_quoted_paths(text: str) -> str:
    out: list[str] = []
    position = 0
    index = 0
    while index < len(text):
        char = text[index]
        opens = char in QUOTES and (index == 0 or not text[index - 1].isalnum())
        if not opens or not _QUOTED_PATH_START_RE[char].match(text, index + 1):
            index += 1
            continue
        end = quoted_end(text, index)
        closed = end <= len(text) and text[end - 1 : end] == char and end - 1 > index
        out.append(text[position:index])
        out.append(f"{char}{LOCAL_PATH}{char}" if closed else f"{char}{LOCAL_PATH}")
        position = index = end
    out.append(text[position:])
    return "".join(out)


def scrub_paths(text: str) -> str:
    home = str(Path.home())
    if home and home not in {"/", "\\"}:
        text = text.replace(home, "~")
    text = _scrub_quoted_paths(text)
    text = _FILE_URL_RE.sub(LOCAL_PATH, text)
    text = _WINDOWS_PATH_RE.sub(LOCAL_PATH, text)
    text = _OTHER_HOME_RE.sub("~", text)
    return _UNIX_PATH_RE.sub(LOCAL_PATH, text)


def scrub(text: str) -> str:
    """Redact secret-shaped values, then absolute paths, from ``text``."""
    return scrub_paths(scrub_secrets(text))
