"""frontmatter.py — shared stdlib-only parser for Markdown YAML frontmatter.

Handles exactly the scalar forms an agent or skill file can legitimately use
(block, plain, quoted) and reports anything else rather than guessing. PyYAML
is deliberately not a dependency. Shared by lint-skills.py, build-dist.py and
check-model-routing.py so no consumer carries a naive line reader.
"""

import re

KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_.-]*):(.*)$")


class Field:
    """One top-level frontmatter key, with the scalar style it was written in."""

    def __init__(self, value, style, multiline):
        self.value = value  # str, or None for a nested mapping
        self.style = style  # block | plain | quoted | empty | mapping
        self.multiline = multiline


def _is_continuation(line):
    """True if `line` continues the previous scalar rather than starting a key."""
    if not line.strip():
        return False
    if line[:1].isspace():
        return True
    return KEY_RE.match(line) is None and line.strip() != "---"


def _close_quote(text, quote):
    """Index just past the closing `quote` in `text`, or -1 if unterminated."""
    i = 0
    while i < len(text):
        c = text[i]
        if quote == '"' and c == "\\":
            i += 2
            continue
        if c == quote:
            if quote == "'" and text[i + 1 : i + 2] == "'":  # '' escapes a quote
                i += 2
                continue
            return i + 1
        i += 1
    return -1


def parse_frontmatter(text):
    """Return (fields, body, error). `fields` maps key -> Field."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, None, "no YAML frontmatter (file must open with ---)"
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, None, "frontmatter is never closed (no second ---)"

    fm = lines[1:end]
    body = "\n".join(lines[end + 1 :])
    fields = {}
    i = 0
    while i < len(fm):
        line = fm[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        m = KEY_RE.match(line)
        if not m:
            return None, None, "line %d is not a top-level key: %r" % (i + 2, line)
        key, rest = m.group(1), m.group(2)
        stripped = rest.strip()
        i += 1

        if stripped[:1] in ("|", ">"):
            # Block scalar: everything indented under it, verbatim.
            chunk = []
            while i < len(fm) and (not fm[i].strip() or fm[i][:1].isspace()):
                chunk.append(fm[i].strip())
                i += 1
            while chunk and not chunk[-1]:
                chunk.pop()
            fields[key] = Field(
                " ".join(c for c in chunk if c), "block", len([c for c in chunk if c]) > 1
            )
            continue

        if stripped == "":
            # Three things look like this: an empty value, a nested mapping, and
            # a bare multi-line plain scalar starting on the next line. The last
            # two are told apart by whether the first indented line is itself a
            # `key:` — which is precisely the ambiguity that makes a colon-space
            # inside an unquoted description swallow the rest as a mapping.
            if i < len(fm) and fm[i].strip() and fm[i][:1].isspace():
                mapping = KEY_RE.match(fm[i].strip()) is not None
                chunk = []
                while i < len(fm) and (not fm[i].strip() or fm[i][:1].isspace()):
                    chunk.append(fm[i].strip())
                    i += 1
                chunk = [c for c in chunk if c]
                if mapping:
                    fields[key] = Field(None, "mapping", False)
                else:
                    fields[key] = Field(" ".join(chunk), "plain", True)
            else:
                fields[key] = Field("", "empty", False)
            continue

        if stripped[0] in ("'", '"'):
            quote = stripped[0]
            closed = _close_quote(stripped[1:], quote)
            parts = [stripped]
            multiline = False
            while closed == -1 and i < len(fm):
                multiline = True
                parts.append(fm[i].strip())
                closed = _close_quote(fm[i], quote)
                i += 1
            value = " ".join(parts).strip()
            fields[key] = Field(value[1:-1] if len(value) > 1 else "", "quoted", multiline)
            continue

        # Plain (unquoted) scalar. Indented follow-on lines make it multi-line,
        # which is the form that breaks a strict parser.
        parts = [stripped]
        multiline = False
        while i < len(fm) and _is_continuation(fm[i]):
            multiline = True
            parts.append(fm[i].strip())
            i += 1
        fields[key] = Field(" ".join(parts), "plain", multiline)

    return fields, body, None
