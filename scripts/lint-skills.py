#!/usr/bin/env python3
"""lint-skills.py — enforce the source SKILL.md contract in skills/README.md.

Two contracts, both silent when violated. The first is frontmatter: a `name`
that does not match its directory does not error anywhere, it just makes the
skill load under the wrong name (or not at all). That really happened —
`composition-patterns` declared `name: vercel-composition-patterns` and one
harness listed it wrong for weeks.

The second is catalogue consistency: `skills/README.md` is the hand-written
index of the source skills, and a skill added or renamed without an index
edit (or an index entry whose directory is gone) is invisible drift.

The sharpest frontmatter rule is the block scalar one. Claude Code's YAML
parser is lenient; other harnesses are strict, and a bare unquoted multi-line
`description` containing a colon-space parses as a nested mapping, so the
whole skill fails to load with "mapping values are not allowed in this
context".

Stdlib only, deliberately: PyYAML is not a dependency of this repo and must
not become one for a lint. Hence the small parser below, which handles exactly
the scalar forms a SKILL.md can legitimately use (block, plain, quoted) and
reports anything else rather than guessing.

  ./scripts/lint-skills.py [repo-root]

FAILs exit 1. WARNs never do — two skills are legitimately over the body
threshold today and shrinking them is somebody else's issue; a WARN that broke
the build would just get deleted.
"""

import os
import re
import sys

MAX_NAME = 64
MAX_DESCRIPTION = 1024
WARN_DESCRIPTION = 1000
WARN_BODY_BYTES = 20000  # ~5k tokens
NAME_RE = re.compile(r"^[a-z0-9-]+$")
KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_.-]*):(.*)$")
CATALOGUE_RE = re.compile(r"^- `([a-z0-9-]+)` — ")
BANNED_IN_NAME = ("claude", "anthropic")


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
        # which is the form that breaks Codex.
        parts = [stripped]
        multiline = False
        while i < len(fm) and _is_continuation(fm[i]):
            multiline = True
            parts.append(fm[i].strip())
            i += 1
        fields[key] = Field(" ".join(parts), "plain", multiline)

    return fields, body, None


def lint_skill(path, dirname):
    """Return (fails, warns) — two lists of human-readable strings."""
    fails, warns = [], []
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()

    fields, body, error = parse_frontmatter(text)
    if error:
        return [error], []

    name = fields.get("name")
    if name is None or name.style in ("empty", "mapping") or not (name.value or "").strip():
        fails.append("no `name` in frontmatter")
    else:
        value = name.value.strip()
        if value != dirname:
            fails.append("name %r does not match directory %r" % (value, dirname))
        if len(value) > MAX_NAME:
            fails.append("name is %d chars, max %d" % (len(value), MAX_NAME))
        if not NAME_RE.match(value):
            fails.append("name %r is not [a-z0-9-]+" % value)
        lowered = value.lower()
        for banned in BANNED_IN_NAME:
            if banned in lowered:
                fails.append("name %r contains %r" % (value, banned))

    desc = fields.get("description")
    if desc is None or desc.style in ("empty", "mapping") or not (desc.value or "").strip():
        fails.append("no `description` in frontmatter")
    else:
        if desc.multiline and desc.style == "plain":
            fails.append(
                "multi-line description is a bare unquoted scalar — "
                "use a block scalar (| or >-), or Codex fails to load the skill"
            )
        length = len(desc.value)
        if length > MAX_DESCRIPTION:
            fails.append("description is %d chars, max %d" % (length, MAX_DESCRIPTION))
        elif length >= WARN_DESCRIPTION:
            warns.append("description is %d chars, close to the %d limit" % (length, MAX_DESCRIPTION))

    size = len(body.encode("utf-8"))
    if size > WARN_BODY_BYTES:
        warns.append(
            "body is %d bytes > %d (~5k tokens) — push bulk into references/"
            % (size, WARN_BODY_BYTES)
        )

    return fails, warns


def read_text(path):
    """Return the file's text, or None when it cannot be read."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def lint_catalogue(skills_dir, dirnames):
    """Return (fails, warns) comparing skills/README.md against the source tree.

    The catalogue is the bullet list of source skills; only lines of the form
    ``- `name` — description`` are entries, so prose that happens to mention a
    skill name in backticks is not mistaken for one.
    """
    readme = os.path.join(skills_dir, "README.md")
    text = read_text(readme)
    if text is None:
        return ["skills/README.md is missing — no catalogue to check"], []
    listed = {m.group(1) for m in (CATALOGUE_RE.match(l) for l in text.splitlines()) if m}

    present = set(dirnames)
    fails = []
    for name in sorted(listed - present):
        fails.append("skills/README.md lists %r but there is no skills/%s/SKILL.md" % (name, name))
    for name in sorted(present - listed):
        fails.append("skills/%s is not listed in skills/README.md" % name)
    return fails, []


def main(argv):
    if len(argv) > 2:
        sys.stderr.write("usage: lint-skills.py [repo-root]\n")
        return 2
    repo_root = argv[1] if len(argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills_dir = os.path.join(repo_root, "skills")
    if not os.path.isdir(skills_dir):
        sys.stderr.write("FATAL: no skills/ directory under %s\n" % repo_root)
        return 2

    try:
        entries = sorted(os.listdir(skills_dir))
    except OSError as exc:
        sys.stderr.write("FATAL: cannot read %s (%s)\n" % (skills_dir, exc))
        return 2

    print("skill frontmatter")
    passed = failed = warned = 0
    sources = []
    for dirname in entries:
        # _archive is deliberately not installed, so the contract does not apply.
        if dirname.startswith("_") or dirname.startswith("."):
            continue
        path = os.path.join(skills_dir, dirname, "SKILL.md")
        if not os.path.isfile(path):
            continue
        sources.append(dirname)
        fails, warns = lint_skill(path, dirname)
        for detail in fails:
            print("  FAIL  %s (%s)" % (dirname, detail))
        for detail in warns:
            print("  WARN  %s (%s)" % (dirname, detail))
        warned += len(warns)
        if fails:
            failed += 1
        else:
            passed += 1
            if not warns:
                print("  ok    %s" % dirname)

    print()
    print("skill catalogue")
    cat_fails, _ = lint_catalogue(skills_dir, sources)
    for detail in cat_fails:
        print("  FAIL  %s" % detail)
    if not cat_fails:
        print("  ok    %d source skills match skills/README.md" % len(sources))

    print()
    failed += len(cat_fails)
    summary = "%d passed, %d failed" % (passed, failed)
    if warned:
        summary += ", %d warnings (not fatal)" % warned
    print(summary)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
