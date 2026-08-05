#!/usr/bin/env python3
"""Completion gate for the html-doc skill.

Usage: python3 check.py <file.html>

Checks one self-contained HTML document for the properties the skill promises:
no network requests, a sane document head, a heading tree that does not skip a
level, working internal anchors, and a print block. Standard library only.

Exit codes: 0 = no failures, 1 = at least one failure, 2 = usage error.
"""

import os
import re
import sys

MAX_BYTES = 500 * 1024


def line_of(text, index):
    """1-based line number of a character offset."""
    return text.count("\n", 0, index) + 1


def blank_regions(text, pattern):
    """Blank out matched regions, preserving every newline so line numbers hold."""
    out = list(text)
    for match in pattern.finditer(text):
        for i in range(match.start(), match.end()):
            if out[i] != "\n":
                out[i] = " "
    return "".join(out)


def strip_tags(fragment):
    fragment = re.sub(r"<[^>]*>", "", fragment)
    fragment = re.sub(r"&[a-zA-Z#0-9]+;", " ", fragment)
    fragment = " ".join(fragment.split())
    return fragment[:60] if len(fragment) <= 60 else fragment[:57] + "..."


STYLE_RE = re.compile(r"<style\b[^>]*>.*?</style\s*>", re.IGNORECASE | re.DOTALL)
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

EXTERNAL_RULES = [
    (re.compile(r"<script\b[^>]*\bsrc\s*=", re.IGNORECASE), "external script reference"),
    (
        re.compile(r"<link\b[^>]*\brel\s*=\s*[\"']?stylesheet", re.IGNORECASE),
        "external stylesheet link",
    ),
    (re.compile(r"@import\b", re.IGNORECASE), "CSS @import"),
    (
        re.compile(r"url\(\s*[\"']?\s*(?:https?:)?//", re.IGNORECASE),
        "remote url() in CSS",
    ),
    (re.compile(r"\bsrc\s*=\s*[\"'](?:https?:)?//", re.IGNORECASE), "remote src attribute"),
]


def check(path, raw):
    failures = []  # (line, message)
    warnings = []  # (line, message)

    # Style blocks and comments are blanked for structural checks so that CSS
    # selectors such as a[href^="#fnref"] are not read as document markup.
    body = blank_regions(blank_regions(raw, STYLE_RE), COMMENT_RE)

    # --- FAIL 1: external references ------------------------------------
    spans = []
    for pattern, label in EXTERNAL_RULES:
        for match in pattern.finditer(raw):
            if any(start < match.end() and match.start() < end for start, end in spans):
                continue
            spans.append((match.start(), match.end()))
            snippet = " ".join(raw[match.start() : match.start() + 70].split())
            failures.append(
                (line_of(raw, match.start()), "%s — %s" % (label, snippet))
            )

    # --- FAIL 2: document head ------------------------------------------
    if not re.search(r"<!doctype\s+html\s*>", raw, re.IGNORECASE):
        failures.append((1, "missing <!doctype html> — required as the first line"))

    html_tag = re.search(r"<html\b[^>]*>", raw, re.IGNORECASE)
    if not html_tag:
        failures.append((1, "missing <html> element — no root tag found"))
    elif not re.search(r"\blang\s*=\s*[\"']?[a-zA-Z]", html_tag.group(0)):
        failures.append(
            (line_of(raw, html_tag.start()), "missing lang= on <html> — screen readers need it")
        )

    if not re.search(r"<meta\b[^>]*\bcharset\s*=", raw, re.IGNORECASE):
        failures.append((1, "missing <meta charset> — encoding is undeclared"))

    if not re.search(r"<meta\b[^>]*\bname\s*=\s*[\"']?viewport", raw, re.IGNORECASE):
        failures.append((1, "missing <meta name=\"viewport\"> — mobile layout will break"))

    title = re.search(r"<title\b[^>]*>(.*?)</title\s*>", raw, re.IGNORECASE | re.DOTALL)
    if not title:
        failures.append((1, "missing <title> — no document title"))
    elif not title.group(1).strip():
        failures.append((line_of(raw, title.start()), "empty <title> — title is whitespace only"))

    # --- FAIL 3 and 4: headings -----------------------------------------
    headings = list(
        re.finditer(r"<h([1-6])\b[^>]*>(.*?)</h\1\s*>", body, re.IGNORECASE | re.DOTALL)
    )
    h1s = [m for m in headings if m.group(1) == "1"]
    if len(h1s) != 1:
        where = ", ".join("line %d" % line_of(body, m.start()) for m in h1s) or "none found"
        failures.append((line_of(body, h1s[0].start()) if h1s else 1,
                         "expected exactly one <h1>, found %d — %s" % (len(h1s), where)))

    previous = None
    for match in headings:
        level = int(match.group(1))
        if previous is not None and level > previous + 1:
            failures.append(
                (
                    line_of(body, match.start()),
                    "heading level skipped, h%d after h%d — \"%s\""
                    % (level, previous, strip_tags(match.group(2))),
                )
            )
        previous = level

    # --- FAIL 5: dangling internal anchors ------------------------------
    ids = set(re.findall(r"\bid\s*=\s*[\"']([^\"']+)[\"']", body))
    for match in re.finditer(r"\bhref\s*=\s*[\"']#([^\"']*)[\"']", body):
        target = match.group(1)
        if not target:
            continue  # bare href="#" is a legitimate no-op
        if target not in ids:
            failures.append(
                (
                    line_of(body, match.start()),
                    "dangling anchor href=\"#%s\" — no element carries that id" % target,
                )
            )

    # --- FAIL 6: print block --------------------------------------------
    if not re.search(r"@media\b[^{]*\bprint\b", raw, re.IGNORECASE):
        failures.append((1, "no @media print block — the document will not print correctly"))

    # --- WARN 1: tables outside .table-wrap -----------------------------
    for match in re.finditer(r"<table\b", body, re.IGNORECASE):
        before = body[: match.start()]
        wrap = before.rfind("table-wrap")
        if wrap == -1 or "</div" in before[wrap:].lower():
            warnings.append(
                (line_of(body, match.start()), "<table> not inside a .table-wrap — it will overflow narrow screens")
            )

    # --- WARN 2: images without alt -------------------------------------
    for match in re.finditer(r"<img\b[^>]*>", body, re.IGNORECASE):
        if not re.search(r"\balt\s*=", match.group(0)):
            warnings.append(
                (line_of(body, match.start()), "<img> without alt= — add alt text, or alt=\"\" if decorative")
            )

    # --- WARN 3: no dark mode -------------------------------------------
    if not re.search(r"prefers-color-scheme", raw, re.IGNORECASE):
        warnings.append((1, "no prefers-color-scheme — the document ignores dark mode"))

    # --- WARN 4: file size ----------------------------------------------
    size = len(raw.encode("utf-8"))
    if size > MAX_BYTES:
        warnings.append((1, "file is %d KB — over the 500 KB budget" % (size // 1024)))

    # --- WARN 5: any script at all --------------------------------------
    for match in re.finditer(r"<script\b", raw, re.IGNORECASE):
        warnings.append(
            (line_of(raw, match.start()), "<script> tag present — the default for this skill is zero JavaScript")
        )

    return failures, warnings


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: check.py <file.html>\n")
        return 2
    path = argv[1]
    if os.path.isdir(path):
        sys.stderr.write("usage: check.py <file.html>  (%s is a directory)\n" % path)
        return 2
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            raw = handle.read()
    except OSError as error:
        sys.stderr.write("usage: check.py <file.html>  (cannot read %s: %s)\n" % (path, error.strerror))
        return 2

    failures, warnings = check(path, raw)

    for line, message in sorted(failures, key=lambda item: item[0]):
        print("FAIL: line %d: %s" % (line, message))
    for line, message in sorted(warnings, key=lambda item: item[0]):
        print("WARN: line %d: %s" % (line, message))

    if failures:
        print("FAIL: %s (%d failures, %d warnings)" % (path, len(failures), len(warnings)))
        return 1
    print("PASS: %s (%d warnings)" % (path, len(warnings)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
