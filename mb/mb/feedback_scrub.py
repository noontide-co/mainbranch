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

import bisect
import functools
import itertools
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
# A YAML ``key:``; ``_YAML_HEADER_TAIL_RE`` decides whether its value is below.
_YAML_KEY_RE = re.compile(rf"(?<![A-Za-z0-9_.\-])([\"']?)({_KEY})\1[ \t]*:(?=[ \t]|\r?$)")
# YAML node properties: a tag (``!!str``, ``!foo``, ``!<...>``) or an anchor (``&a``).
_YAML_PROPERTIES = r"(?:(?:!<[^>\n]*>|![^\s]*|&[^\s]+)(?:[ \t]+|(?=\r?$)))*"
# What may follow ``key:`` when the value sits on the lines below: properties, a
# ``|``/``>`` indicator with chomping and indent digits, and a `` # comment``.
_YAML_HEADER_TAIL_RE = re.compile(
    rf"[ \t]*{_YAML_PROPERTIES}(?:[|>](?:[1-9][-+]?|[-+][1-9]?)?)?(?:[ \t]+#[^\n]*)?[ \t]*\r?$"
)
# Properties before an inline value: ``key: !!str &a value``.
_YAML_INLINE_PROPERTIES_RE = re.compile(r"(?:(?:!<[^>\n]*>|![^\s]*|&[^\s]+)[ \t]+)+")
# An explicit key, ``? key``, and the ``:`` line that carries its value.
_YAML_EXPLICIT_KEY_RE = re.compile(
    rf"(?:^|(?<=[ \t]))\?[ \t]+([\"']?)({_KEY})\1[ \t]*(?:#[^\n]*)?\r?$"
)
_YAML_EXPLICIT_VALUE_RE = re.compile(r"[ \t]*:(?=[ \t]|\r?$)")
# What may precede a key for its column to be the YAML indentation: only
# indentation and ``- `` list markers, not prose.
_YAML_KEY_PREFIX_RE = re.compile(r"[ \t]*(?:-[ \t]+)*")
# A plain scalar's trailing comment.
_YAML_PLAIN_COMMENT_RE = re.compile(r"[ \t]+#")
# First characters of an inline value that is not a plain scalar.
_YAML_NOT_PLAIN = frozenset("\"'`{[|>*#")
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


def flow_end(text: str, start: int) -> int:
    """Index just past the ``{...}``/``[...]`` YAML flow collection at ``start``.

    Nested brackets are counted across lines; a quote that opens a scalar (after
    a bracket, comma, colon or whitespace) is skipped with ``quoted_end``, and
    a `` #`` comment runs to the end of its line, so its brackets do not count.
    An unclosed collection runs to the end of ``text``.
    """
    depth = 0
    index = start
    while index < len(text):
        char = text[index]
        if char in "{[":
            depth += 1
        elif char in "}]":
            depth -= 1
            if depth == 0:
                return index + 1
        elif char in QUOTES and text[index - 1] in " \t\r\n{[,:":
            index = quoted_end(text, index)
            continue
        elif char == "#" and text[index - 1] in " \t\r\n":
            line_end = text.find("\n", index)
            if line_end < 0:
                break
            index = line_end
        index += 1
    return len(text)


def key_segments(key: str) -> list[str]:
    return [
        segment.lower()
        for part in re.split(r"[_.\-]+", key)
        for segment in _SEGMENT_RE.findall(part)
    ]


@functools.lru_cache(maxsize=4096)
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


def _redact_values(
    text: str, pattern: re.Pattern[str], key_group: int, *, yaml: bool = False
) -> str:
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
        if yaml and ":" in match.group(key_group + 1):
            # ``key: !!str &a value``: the value follows the node properties.
            properties = _YAML_INLINE_PROPERTIES_RE.match(text, start)
            if properties:
                start = properties.end()
            end = flow_end(text, start) if text[start : start + 1] in ("{", "[") else None
        else:
            end = None
        if end is None:
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


def _yaml_secret_header(line: str) -> tuple[str, int, int] | None:
    """Classify a line that opens a secret YAML value: ``(kind, base, value start)``.

    ``block``: the value sits on the lines below. After the colon there may be
    a tag, an anchor, a ``|``/``>`` indicator with chomping and indent digits,
    and a trailing comment, and nothing else. ``plain``: an inline plain
    scalar starting at ``value start``, which may continue on lines more
    indented than ``base``. ``base`` is the key's column when only
    indentation and ``- `` markers precede it, else the line's indentation
    (prose before the key).
    """
    for match in _YAML_KEY_RE.finditer(line):
        if not is_secret_key(match.group(2)):
            continue
        prefix = _YAML_KEY_PREFIX_RE.match(line)
        base = match.start() if prefix and prefix.end() == match.start() else _indent(line)
        if _YAML_HEADER_TAIL_RE.match(line, match.end()):
            return "block", base, match.end()
        start = match.end()
        while start < len(line) and line[start] in " \t":
            start += 1
        properties = _YAML_INLINE_PROPERTIES_RE.match(line, start)
        if properties:
            start = properties.end()
        if line[start : start + 1] not in _YAML_NOT_PLAIN:
            return "plain", base, start
        return None
    return None


def _without_plain_value(line: str, start: int) -> str:
    """``line`` with its plain value from ``start`` replaced, keeping a comment."""
    comment = _YAML_PLAIN_COMMENT_RE.search(line, start)
    tail = line[comment.start() :] if comment else ("\r" if line.endswith("\r") else "")
    return line[:start] + REDACTED + tail


def _is_comment(line: str) -> bool:
    return line.lstrip(" \t").startswith("#")


def _is_dash(line: str) -> bool:
    stripped = line.strip()
    return stripped == "-" or stripped.startswith("- ")


def _block_end(lines: list[str], index: int, base: int, dash_columns: tuple[int, ...]) -> int:
    """Index just past the last line of the block that starts at ``lines[index]``.

    The block is every line more indented than ``base``, with blank and
    comment lines inside it. A ``- `` item at one of ``dash_columns`` (an
    indentless sequence) belongs to it too. The first other line at
    ``base`` or less ends it. Returns ``index`` when the block is empty.
    """
    end = index
    last_content = index
    while end < len(lines):
        current = lines[end]
        if current.strip() and (
            _indent(current) > base or (_indent(current) in dash_columns and _is_dash(current))
        ):
            last_content = end + 1
        elif current.strip() and not _is_comment(current):
            break
        end += 1
    return last_content


def _redacted_line(base: int, last: str) -> str:
    return " " * (base + 2) + REDACTED + ("\r" if last.endswith("\r") else "")


def _explicit_value(
    text: str, lines: list[str], starts: list[int], index: int, out: list[str]
) -> int:
    """Redact the ``:`` value of a secret ``? key``; return the next line index."""
    value = index
    while value < len(lines) and (not lines[value].strip() or _is_comment(lines[value])):
        value += 1
    if value == len(lines):
        return index
    match = _YAML_EXPLICIT_VALUE_RE.match(lines[value])
    if match is None:
        return index
    out.extend(lines[index:value])
    line = lines[value]
    base = _indent(line)
    if _YAML_HEADER_TAIL_RE.match(line, match.end()):
        out.append(line)
        last = _block_end(lines, value + 1, base, (base,))
        if last > value + 1:
            out.append(_redacted_line(base, lines[last - 1]))
        return max(last, value + 1)
    start = match.end()
    while line[start : start + 1] in (" ", "\t"):
        start += 1
    properties = _YAML_INLINE_PROPERTIES_RE.match(line, start)
    if properties:
        start = properties.end()
    if line[start : start + 1] in ("{", "["):
        # A flow collection may close on any line; skip whole lines up to it.
        close = flow_end(text, starts[value] + start)
        last = bisect.bisect_right(starts, close - 1)
    else:
        last = value + 1
    last = _block_end(lines, last, base, ())
    out.append(line[: match.end()] + " " + REDACTED + ("\r" if line.endswith("\r") else ""))
    if last > value + 1:
        out.append(_redacted_line(base, lines[last - 1]))
    return max(last, value + 1)


def _redact_yaml_blocks(text: str) -> str:
    """Redact the lines that belong to a secret YAML value.

    - ``key:`` with its value below: every following line more indented than
      the key line, plus ``- `` items at the key's own column (an indentless
      sequence), with blank and comment lines inside, up to the first other
      line at the key's indentation or less.
    - ``key: plain value`` that continues on more-indented lines: the whole
      first-line value (keeping a trailing comment) and the continuation.
      A single-line value is left to the value rule.
    - ``? key`` then ``: value``: the value line and its continuation.
    """
    lines = text.split("\n")
    starts = list(itertools.accumulate((len(line) + 1 for line in lines[:-1]), initial=0))
    out: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        out.append(line)
        index += 1
        explicit = _YAML_EXPLICIT_KEY_RE.search(line) if "?" in line else None
        if explicit and is_secret_key(explicit.group(2)):
            index = _explicit_value(text, lines, starts, index, out)
            continue
        header = _yaml_secret_header(line)
        if header is None:
            continue
        kind, base, start = header
        dash_columns = (base, _indent(line)) if kind == "block" else ()
        last = _block_end(lines, index, base, dash_columns)
        if last > index:
            if kind == "plain":
                # The value continues below, so all of its first line is value.
                out[-1] = _without_plain_value(line, start)
            out.append(_redacted_line(base, lines[last - 1]))
            index = last
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
    text = _redact_values(text, _PAIR_RE, 2, yaml=True)
    text = _redact_values(text, _FLAG_RE, 1)
    for token_pattern in (*_TOKEN_RULES, _connect_prefix_re(), TOKEN_RE):
        text = token_pattern.sub(REDACTED, text)
    text = _redact_sensitive_text(text)
    return QUERY_SECRET_RE.sub(lambda match: f"{match.group(1)}{REDACTED}", text)


_QUOTE_RE = re.compile("[\"'`]")


def _scrub_quoted_paths(text: str) -> str:
    out: list[str] = []
    position = 0
    index = 0
    while True:
        quote = _QUOTE_RE.search(text, index)
        if quote is None:
            break
        index = quote.start()
        char = text[index]
        opens = index == 0 or not text[index - 1].isalnum()
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
