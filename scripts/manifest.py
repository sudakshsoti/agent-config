#!/usr/bin/env python3
"""manifest.py — importable stdlib-only parser for plugins.txt.

plugins.txt declares third-party skill sources only (see AGENTS.md and the
header comment in plugins.txt). Grammar, one directive per line:

    external <owner/repo>[:<subdir>] [skill ...]

Blank lines and full-line or trailing `#`-comments are ignored. This module
is deliberately just a parser: it has no opinion on whether a name collides
with a repo-owned skill or with another line — callers (scripts/check-manifest.py
today, a later catalogue audit tomorrow) decide what a parsed entry means.

    from manifest import parse_plugins_file, ParseError, Entry

Stdlib only, no dependencies.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Entry:
    """One parsed `external` directive."""

    line_no: int
    raw: str
    source: str  # "<owner>/<repo>" without the optional :<subdir>
    subdir: Optional[str]  # text after ':' in the source token, or None
    skills: List[str] = field(default_factory=list)  # explicit allowlist; [] means bare


@dataclass
class ParseError:
    """A malformed line, with its 1-based line number and a human message."""

    line_no: int
    raw: str
    message: str


def _strip_comment(line):
    """Strip a `#`-comment. plugins.txt has no quoting, so the first '#' wins."""
    idx = line.find("#")
    return line if idx == -1 else line[:idx]


def parse_plugins_text(text):
    """Parse plugins.txt content. Return (entries, errors), both lists.

    `entries` holds every syntactically valid `external` line, in file order.
    `errors` holds every malformed line, in file order, each carrying its
    1-based line number. A line is malformed when it is neither blank/comment
    nor a well-formed `external <owner/repo>[:<subdir>] [skill ...]` directive
    — e.g. an unrecognized directive keyword, `external` with no argument, or
    a source token that is not `owner/repo` (optionally `:subdir`).
    """
    entries = []
    errors = []
    for line_no, raw in enumerate(text.splitlines(), start=1):
        stripped = _strip_comment(raw).strip()
        if not stripped:
            continue
        tokens = stripped.split()
        kind = tokens[0]
        if kind != "external":
            errors.append(ParseError(line_no, raw, "unknown directive %r (expected 'external')" % kind))
            continue
        if len(tokens) < 2:
            errors.append(ParseError(line_no, raw, "'external' with no source"))
            continue
        source_token = tokens[1]
        skills = tokens[2:]
        source, subdir = source_token, None
        if ":" in source_token:
            source, subdir = source_token.split(":", 1)
            if not subdir:
                errors.append(ParseError(line_no, raw, "empty subdir after ':' in %r" % source_token))
                continue
        parts = source.split("/")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            errors.append(ParseError(line_no, raw, "source %r is not owner/repo" % source))
            continue
        entries.append(Entry(line_no=line_no, raw=raw, source=source, subdir=subdir, skills=skills))
    return entries, errors


def parse_plugins_file(path):
    """Parse a plugins.txt file on disk. Return (entries, errors).

    A missing file parses as empty (no entries, no errors) — plugins.txt is
    optional, exactly as install.sh treats it.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except FileNotFoundError:
        return [], []
    return parse_plugins_text(text)
