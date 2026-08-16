#!/usr/bin/env python3
"""Completion gate for the studio skill.

Usage: python3 check.py [--shape document|page] <file.html>

Checks one self-contained HTML artifact for the properties the skill
promises: no network requests beyond an allowed remote webfont, a sane
document head, a heading tree that does not skip a level, working internal
anchors, a print block (document shape only), and a set of mechanical
anti-slop checks (gradients, rule-of-three card grids, uniform radius,
emoji headings, filler words, the 1200px-container-as-only-layout-idea,
blacklisted font families, Inter as display, and novel vocabulary classes).
Standard library only.

Exit codes: 0 = no failures, 1 = at least one failure, 2 = usage error.
"""

import os
import re
import sys

MAX_BYTES = 700 * 1024


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
TAG_RE = re.compile(r"<[^>]*>")
ENTITY_RE = re.compile(r"&[a-zA-Z#0-9]+;")

FONT_URL_RE = re.compile(
    r"fonts\.googleapis\.com|fonts\.gstatic\.com|\.(?:woff2?|ttf|otf)(?:[\"'?]|$)",
    re.IGNORECASE,
)

EXTERNAL_RULES = [
    (re.compile(r"<script\b[^>]*\bsrc\s*=", re.IGNORECASE), "external script reference"),
    (re.compile(r"<link\b[^>]*\brel\s*=\s*[\"']?stylesheet", re.IGNORECASE), "external stylesheet link"),
    (re.compile(r"@import\b", re.IGNORECASE), "CSS @import"),
    (re.compile(r"url\(\s*[\"']?\s*(?:https?:)?//", re.IGNORECASE), "remote url() in CSS"),
    (re.compile(r"\bsrc\s*=\s*[\"'](?:https?:)?//", re.IGNORECASE), "remote src attribute"),
]

BANNED_FAMILIES = [
    "Poppins", "Montserrat", "Raleway", "Lato", "Open Sans", "Nunito",
    "Quicksand", "Playfair Display", "Oswald", "Bebas Neue", "Comfortaa",
    "Josefin Sans", "Roboto", "Space Grotesk", "Manrope", "DM Sans",
    "DM Serif", "Instrument Sans", "Instrument Serif", "Fraunces",
]

FILLER_WORDS = [
    "seamlessly", "effortlessly", "powerful", "beautiful", "elevate",
    "unlock", "supercharge", "unleash", "delve", "game-changing",
    "cutting-edge",
]

CARD_KEYWORDS = ("card", "feature", "tier", "pillar", "benefit")

EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F]")

VOCAB_DOCUMENT = {
    "doc-header", "doc-meta", "lead", "toc", "summary", "callout",
    "callout-label", "kv", "table-wrap", "steps", "stat-row", "stat",
    "bar", "appendix", "sources",
}

VOCAB_PAGE = {
    "page-header", "nav", "hero", "hero-title", "hero-sub", "section",
    "section-head", "eyebrow", "lead", "grid", "panel", "feature",
    "stat-row", "stat", "quote", "table-wrap", "list", "steps", "cta",
    "btn", "note", "figure", "caption", "divider", "code", "badge",
    "meta", "footer",
    "swatch-grid", "swatch", "swatch-chip", "swatch-name", "swatch-value",
    "pair", "pair-label", "type-row", "type-sample", "type-spec", "glyphs",
    "scale-row", "scale-bar", "scale-label", "radius-row", "radius-tile",
    "elev-row", "elev-tile", "state-row", "state-label", "field",
}


def find_calls(text, name):
    """Find `name(...)` calls with balanced parens; returns (start, args)."""
    results = []
    for match in re.finditer(re.escape(name) + r"\(", text, re.IGNORECASE):
        start = match.end()
        depth = 1
        i = start
        while i < len(text) and depth > 0:
            if text[i] == "(":
                depth += 1
            elif text[i] == ")":
                depth -= 1
            i += 1
        if depth == 0:
            results.append((match.start(), text[start:i - 1]))
    return results


def check(path, raw, shape):
    failures = []  # (line, message)
    warnings = []  # (line, message)

    # Style blocks and comments are blanked for structural checks so that CSS
    # selectors such as a[href^="#fnref"] are not read as document markup.
    style_matches = list(STYLE_RE.finditer(raw))
    style_text = "\n".join(m.group(0) for m in style_matches)
    body = blank_regions(blank_regions(raw, STYLE_RE), COMMENT_RE)
    # Plain-text copy of body, alignment-preserving, for word-level checks.
    text_only = blank_regions(blank_regions(body, TAG_RE), ENTITY_RE)

    # --- FAIL: external references, remote font is WARN instead ----------
    spans = []
    for pattern, label in EXTERNAL_RULES:
        for match in pattern.finditer(raw):
            if any(start < match.end() and match.start() < end for start, end in spans):
                continue
            spans.append((match.start(), match.end()))
            snippet = " ".join(raw[match.start():match.start() + 90].split())
            line = line_of(raw, match.start())
            if FONT_URL_RE.search(snippet):
                msg = "remote font — breaks offline; base64-embed the subset woff2 for a shareable artifact (" + snippet + ")"
                warnings.append((line, msg))
            else:
                failures.append((line, label + " — " + snippet))

    # --- FAIL: document head ------------------------------------------------
    if not re.search(r"<!doctype\s+html\s*>", raw, re.IGNORECASE):
        failures.append((1, "missing <!doctype html> — required as the first line"))

    html_tag = re.search(r"<html\b[^>]*>", raw, re.IGNORECASE)
    if not html_tag:
        failures.append((1, "missing <html> element — no root tag found"))
    elif not re.search(r"\blang\s*=\s*[\"']?[a-zA-Z]", html_tag.group(0)):
        failures.append((line_of(raw, html_tag.start()), "missing lang= on <html> — screen readers need it"))

    if not re.search(r"<meta\b[^>]*\bcharset\s*=", raw, re.IGNORECASE):
        failures.append((1, "missing <meta charset> — encoding is undeclared"))

    if not re.search(r"<meta\b[^>]*\bname\s*=\s*[\"']?viewport", raw, re.IGNORECASE):
        failures.append((1, "missing <meta name=\"viewport\"> — mobile layout will break"))

    title = re.search(r"<title\b[^>]*>(.*?)</title\s*>", raw, re.IGNORECASE | re.DOTALL)
    if not title:
        failures.append((1, "missing <title> — no document title"))
    elif not title.group(1).strip():
        failures.append((line_of(raw, title.start()), "empty <title> — title is whitespace only"))

    # --- FAIL: headings -------------------------------------------------------
    headings = list(re.finditer(r"<h([1-6])\b[^>]*>(.*?)</h\1\s*>", body, re.IGNORECASE | re.DOTALL))
    h1s = [m for m in headings if m.group(1) == "1"]
    if len(h1s) != 1:
        where = ", ".join("line %d" % line_of(body, m.start()) for m in h1s) or "none found"
        anchor_line = line_of(body, h1s[0].start()) if h1s else 1
        failures.append((anchor_line, "expected exactly one <h1>, found %d — %s" % (len(h1s), where)))

    previous = None
    for match in headings:
        level = int(match.group(1))
        if previous is not None and level > previous + 1:
            snippet = strip_tags(match.group(2))
            msg = "heading level skipped, h%d after h%d" % (level, previous)
            msg = msg + " — \"" + snippet + "\""
            failures.append((line_of(body, match.start()), msg))
        previous = level

    # --- FAIL: dangling internal anchors --------------------------------------
    ids = set(re.findall(r"\bid\s*=\s*[\"']([^\"']+)[\"']", body))
    for match in re.finditer(r"\bhref\s*=\s*[\"']#([^\"']*)[\"']", body):
        target = match.group(1)
        if not target:
            continue  # bare href="#" is a legitimate no-op
        if target not in ids:
            msg = "dangling anchor href=\"#" + target + "\" — no element carries that id"
            failures.append((line_of(body, match.start()), msg))

    # --- FAIL: print block, document shape only -------------------------------
    if shape == "document" and not re.search(r"@media\b[^{]*\bprint\b", raw, re.IGNORECASE):
        failures.append((1, "no @media print block — the document will not print correctly"))

    # --- WARN: tables outside .table-wrap, document shape only ---------------
    if shape == "document":
        for match in re.finditer(r"<table\b", body, re.IGNORECASE):
            before = body[:match.start()]
            wrap = before.rfind("table-wrap")
            if wrap == -1 or "</div" in before[wrap:].lower():
                warnings.append((line_of(body, match.start()), "<table> not inside a .table-wrap — it will overflow narrow screens"))

    # --- WARN: images without alt ----------------------------------------------
    for match in re.finditer(r"<img\b[^>]*>", body, re.IGNORECASE):
        if not re.search(r"\balt\s*=", match.group(0)):
            warnings.append((line_of(body, match.start()), "<img> without alt= — add alt text, or alt=\"\" if decorative"))

    # --- WARN: file size ---------------------------------------------------------
    size = len(raw.encode("utf-8"))
    if size > MAX_BYTES:
        warnings.append((1, "file is %d KB — over the 700 KB budget" % (size // 1024)))

    # --- WARN: any script at all, document shape only; external stays FAIL -----
    if shape == "document":
        for match in re.finditer(r"<script\b(?![^>]*\bsrc\s*=)", raw, re.IGNORECASE):
            warnings.append((line_of(raw, match.start()), "<script> tag present — the default for this shape is zero JavaScript"))

    # === Mechanical anti-slop, all with line numbers ==========================

    # 1. Multi-hue gradient — FAIL
    for kind in ("linear-gradient", "radial-gradient", "conic-gradient"):
        for start, args in find_calls(style_text, kind):
            colors = re.findall(
                r"#[0-9a-fA-F]{3,8}\b|rgba?\([^()]*\)|hsla?\([^()]*\)|oklch\([^()]*\)|lab\([^()]*\)|\b[a-z]+\b",
                args,
            )
            css_keywords = {
                "to", "top", "bottom", "left", "right", "at", "center",
                "circle", "ellipse", "closest-side", "farthest-side",
                "closest-corner", "farthest-corner", "deg", "from",
                "in", "oklab", "srgb", "transparent",
            }
            distinct = set()
            for c in colors:
                low = c.strip().lower()
                if low in css_keywords:
                    continue
                if re.match(r"^-?\d", low):
                    continue
                distinct.add(low)
            if len(distinct) >= 2:
                msg = "multi-hue " + kind + " — two or more distinct colours in one gradient"
                failures.append((line_of(style_text, start), msg))

    # 2. Rule-of-three card grid — FAIL / WARN
    class_attr_re = re.compile(r"<(\w+)\b[^>]*\bclass\s*=\s*[\"']([^\"']+)[\"'][^>]*>", re.IGNORECASE)
    by_class = {}
    for match in class_attr_re.finditer(body):
        cls = match.group(2).strip()
        by_class.setdefault(cls, []).append(match.start())
    for cls, positions in by_class.items():
        if len(positions) == 3:
            first_line = line_of(body, positions[0])
            has_keyword = any(k in cls.lower() for k in CARD_KEYWORDS)
            message = "exactly three siblings share class=\"" + cls + "\""
            if has_keyword:
                failures.append((first_line, message + " — rule-of-three card grid"))
            else:
                warnings.append((first_line, message))

    # 3. Uniform radius — FAIL
    radius_values = {}
    for match in re.finditer(r"\bborder-radius\s*:\s*([^;]+);", style_text, re.IGNORECASE):
        value = match.group(1).strip().lower()
        if value not in ("0", "0px", "0%", "0rem"):
            radius_values.setdefault(value, []).append(match.start())
    for value, positions in radius_values.items():
        if len(positions) >= 4:
            msg = "uniform radius " + value + " declared " + str(len(positions)) + " times — same non-zero border-radius everywhere"
            failures.append((line_of(style_text, positions[0]), msg))
    radius_tokens = {}
    for name in ("--radius-sm", "--radius-md", "--radius-lg", "--radius-pill"):
        match = re.search(re.escape(name) + r"\s*:\s*([^;]+);", style_text, re.IGNORECASE)
        if match:
            radius_tokens[name] = match.group(1).strip().lower()
    if len(radius_tokens) == 4:
        distinct_tokens = set(radius_tokens.values())
        if len(distinct_tokens) == 1 and next(iter(distinct_tokens)) not in ("0", "0px", "0%", "0rem"):
            failures.append((1, "--radius-sm|md|lg|pill all resolve to the same non-zero value"))

    # 4. Emoji in a heading — FAIL
    for match in re.finditer(r"<h([1-6])\b[^>]*>(.*?)</h\1\s*>", body, re.IGNORECASE | re.DOTALL):
        found = EMOJI_RE.findall(match.group(2))
        if found:
            snippet = strip_tags(match.group(2))
            msg = "emoji " + repr(found[0]) + " in a heading — \"" + snippet + "\""
            failures.append((line_of(body, match.start()), msg))

    # 5. Filler word — FAIL
    for word in FILLER_WORDS:
        pattern = re.compile(r"\b" + re.escape(word) + r"\b", re.IGNORECASE)
        match = pattern.search(text_only)
        if match:
            failures.append((line_of(text_only, match.start()), "filler word \"" + word + "\""))

    # 6. Centred 1200px container as the only layout idea — FAIL
    max_width_hit = None
    for match in re.finditer(r"\bmax-width\s*:\s*(\d+(?:\.\d+)?)px", style_text, re.IGNORECASE):
        px = float(match.group(1))
        if 1100 <= px <= 1300:
            max_width_hit = match
            break
    if max_width_hit and not re.search(r"grid-template-columns", style_text, re.IGNORECASE):
        msg = "max-width: " + max_width_hit.group(1) + "px with no grid-template-columns anywhere — centred container is the only layout idea"
        failures.append((line_of(style_text, max_width_hit.start()), msg))

    # 7. Blacklisted family — FAIL
    for family in BANNED_FAMILIES:
        plus_form = family.replace(" ", "+")
        patterns = [re.escape(plus_form)]
        if " " in family:
            patterns.append(re.escape(family))
        else:
            patterns = [r"\b" + re.escape(family) + r"\b"]
        hit = None
        for pat in patterns:
            for match in re.finditer(pat, raw, re.IGNORECASE):
                context = raw[max(0, match.start() - 60):match.start() + len(match.group(0)) + 20]
                if re.search(r"font-family\s*:|@font-face|family\s*=", context, re.IGNORECASE):
                    hit = match
                    break
            if hit is not None:
                break
        if hit is not None:
            failures.append((line_of(raw, hit.start()), "blacklisted font family \"" + family + "\""))

    # 8. Inter as display — FAIL
    display_match = re.search(r"--font-display\s*:\s*([^;]+);", style_text, re.IGNORECASE)
    if display_match:
        first_family = display_match.group(1).split(",")[0].strip().strip("\"'")
        if first_family.lower() == "inter":
            failures.append((line_of(style_text, display_match.start()), "--font-display leads with Inter — Inter is body/UI only, never display"))

    # 9. Novel class — WARN
    vocab = VOCAB_DOCUMENT if shape == "document" else VOCAB_PAGE
    seen_classes = set()
    for match in re.finditer(r"\bclass\s*=\s*[\"']([^\"']+)[\"']", body, re.IGNORECASE):
        for token in match.group(1).split():
            base = re.sub(r"--[a-z0-9-]+$", "", token)
            if base in vocab or token in vocab:
                continue
            if token in seen_classes:
                continue
            seen_classes.add(token)
            msg = "class \"" + token + "\" is not in the " + shape + " vocabulary — fine if the content needs a shape the set lacks; name it in the hand-off"
            warnings.append((line_of(body, match.start()), msg))

    # --- Shadow discipline -----------------------------------------------------
    shadow_values = {}
    for match in re.finditer(r"\bbox-shadow\s*:\s*([^;]+);", style_text, re.IGNORECASE):
        value = match.group(1).strip()
        if value.lower() == "none":
            continue
        shadow_values.setdefault(value, match.start())
    if shape == "document":
        if len(shadow_values) > 1:
            first_pos = min(shadow_values.values())
            msg = str(len(shadow_values)) + " distinct box-shadow values — a document is one surface"
            failures.append((line_of(style_text, first_pos), msg))
    else:
        blurred = []
        for value, pos in shadow_values.items():
            nums = re.findall(r"(-?\d+(?:\.\d+)?)px", value)
            blur = abs(float(nums[2])) if len(nums) >= 3 else 0
            if blur >= 8:
                blurred.append((value, pos))
        if len(blurred) >= 3:
            first_pos = min(pos for _, pos in blurred)
            msg = str(len(blurred)) + " distinct box-shadow values with blur >= 8px — none of the seven measured references elevate with blur"
            warnings.append((line_of(style_text, first_pos), msg))

    return failures, warnings


def main(argv):
    args = argv[1:]
    shape = "document"
    if args[:1] == ["--shape"]:
        if len(args) < 2 or args[1] not in ("document", "page"):
            sys.stderr.write("usage: check.py [--shape document|page] <file.html>\n")
            return 2
        shape = args[1]
        args = args[2:]
    if len(args) != 1:
        sys.stderr.write("usage: check.py [--shape document|page] <file.html>\n")
        return 2
    path = args[0]
    if os.path.isdir(path):
        sys.stderr.write("usage: check.py [--shape document|page] <file.html>  (%s is a directory)\n" % path)
        return 2
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            raw = handle.read()
    except OSError as error:
        sys.stderr.write("usage: check.py [--shape document|page] <file.html>  (cannot read %s: %s)\n" % (path, error.strerror))
        return 2

    failures, warnings = check(path, raw, shape)

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
