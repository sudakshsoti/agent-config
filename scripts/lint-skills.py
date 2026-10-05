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

The sharpest frontmatter rule is the block scalar one. Some harness YAML
parsers are lenient and others are strict; a bare unquoted multi-line
`description` containing a colon-space parses as a nested mapping under a
strict parser, so the whole skill fails to load with "mapping values are not
allowed in this context".

Stdlib only, deliberately: PyYAML is not a dependency of this repo and must
not become one for a lint. Hence the small parser in frontmatter.py, which handles exactly
the scalar forms a SKILL.md can legitimately use (block, plain, quoted) and
reports anything else rather than guessing.

  ./scripts/lint-skills.py [repo-root]

Third contract, dangling references. An audit found ten references to things
that no longer exist (a removed skill, an archived field, a deleted agent). For
every live skills/*/SKILL.md and skills/*/references/**/*.md, `lint_references`
fails when:

  - a relative markdown link, or a backticked path starting `references/`,
    `scripts/` or `skills/`, resolves to nothing — tried relative to the file,
    its skill directory, then the repo root;
  - a skill named in a hand-off context (`skill://x`, "the `x` skill",
    "hand off to `x`", "load `x`", "-> `x`") or in the parentheses of a
    description's "Not for ..." sentence is not a known skill.

Known skills are the live repo-owned skills/*/ directories, the skills named on
`external` lines in plugins.txt, any SKILL.md found under vendor/ (when cloned;
named by its frontmatter `name:`, as install.sh links it), and the names in the
tracked external-skills.txt. Vendored skills are therefore never false-failed in
a checkout where vendor/ is absent, provided plugins.txt or external-skills.txt names
them; a bare `external` line cannot be enumerated offline, so its skills go in
external-skills.txt. skills/_archive/ is neither scanned nor a live target.
Skipped as not-a-reference: fenced code blocks, placeholders (`<name>`, `*`,
`{}`), bare directory mentions (`references/`), `skills/_archive/...` paths
(history citations), and lines that say the
thing is gone (archived/deleted/removed/retired/no longer).

Fourth contract, external-skills.txt drift. When vendor/<slug> exists for a bare
`external` source, that source's section of external-skills.txt (the names under
its `# <owner/repo>[:<subdir>]` heading) must equal the frontmatter `name:` values
the clone ships, enumerated as install.sh does (audit-local.py's helpers). A name
the clone ships but the section lacks, or the section lists but the clone does
not ship, fails and names both. With no clone the check is silent; run
scripts/clone-bare-sources.py first to check a fresh checkout.

Fifth contract, OMP command wrappers. Each omp/commands/*.md must load a
`skill://<name>` that is a known skill (as above), so retiring a repo-owned
skill cannot leave `/name` loading nothing.

FAILs exit 1. WARNs never do — two skills are legitimately over the body
threshold today and shrinking them is somebody else's issue; a WARN that broke
the build would just get deleted.
"""

import importlib.util
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frontmatter import parse_frontmatter  # noqa: E402
from manifest import parse_plugins_file  # noqa: E402

MAX_NAME = 64
MAX_DESCRIPTION = 1024
WARN_DESCRIPTION = 1000
WARN_BODY_BYTES = 20000  # ~5k tokens
NAME_RE = re.compile(r"^[a-z0-9-]+$")
CATALOGUE_RE = re.compile(r"^- `([a-z0-9-]+)` — ")
STATED_COUNT_RE = re.compile(r"covers the (\d+) repo-owned skills")
BANNED_IN_NAME = ("claude", "anthropic")
# OMP drops `..` in skill:// URLs, so skill://a/../b/SKILL.md reads a/b/SKILL.md
# and fails. Every relative link to another skill carries its skill:// form on
# the same line (6 failed commit-push/pr runs, 2026-09-26..10-02).
SIBLING_LINK_RE = re.compile(r"\]\(\.\./([a-z0-9-]+)/SKILL\.md\)")


# Tracked list of the skills that bare `external` lines in plugins.txt ship
# (their names are unknowable offline without a vendor/ clone).
EXTERNAL_SKILLS_FILE = "external-skills.txt"
PATH_RE = re.compile(r"`((?:references|scripts|skills)/[^`\s]*)`")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.-]*:")
PLACEHOLDER_RE = re.compile(r"[<>*{}$]|\.\.\.")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
GONE_RE = re.compile(r"archived|deleted|removed|retired|no longer", re.I)
SKILL_REF_RES = (
    re.compile(r"skill://([a-z0-9][a-z0-9-]*)"),
    re.compile(r"`([a-z][a-z0-9-]*)` skills?\b"),
    re.compile(r"(?:hand[ -]?off to|\bload(?: the)?|→|->) `([a-z][a-z0-9-]*)`", re.I),
)
NOT_FOR_RE = re.compile(r"Not for(.*?)\.(?:\s|$)", re.S | re.I)
PAREN_NAMES_RE = re.compile(
    r"\((?:use )?([a-z][a-z0-9-]*(?:\s*(?:,|\bor\b|\band\b)\s*[a-z][a-z0-9-]*)*)\)"
)


def lint_skill(path, dirname):
    """Return (fails, warns) — two lists of human-readable strings."""
    fails, warns = [], []
    text = read_text(path)
    if text is None:
        return ["cannot read %s" % path], []

    fields, body, error = parse_frontmatter(text)
    if error:
        return [error], []
    if fields is None or body is None:  # unreachable: a missing result always sets error
        return ["internal error: frontmatter parsed with no fields or body"], []

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
                "use a block scalar (| or >-), or a strict parser fails to load the skill"
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

    for line_no, line in enumerate(body.splitlines(), 1):
        for target in SIBLING_LINK_RE.findall(line):
            if "skill://%s" % target not in line:
                fails.append(
                    "body line %d links ../%s/SKILL.md without `skill://%s` on that line"
                    % (line_no, target, target)
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
    lines = text.splitlines()
    listed = {m.group(1) for m in (CATALOGUE_RE.match(l) for l in lines) if m}

    present = set(dirnames)
    fails = []
    for name in sorted(listed - present):
        fails.append("skills/README.md lists %r but there is no skills/%s/SKILL.md" % (name, name))
    for name in sorted(present - listed):
        fails.append("skills/%s is not listed in skills/README.md" % name)

    # The prose also states the count ("The list below covers the N
    # repo-owned skills"); that number drifts independently of the bullet
    # list itself, so check it separately.
    stated = [m for m in (STATED_COUNT_RE.search(l) for l in lines) if m]
    if not stated:
        fails.append("skills/README.md has no 'covers the N repo-owned skills' sentence to check")
    else:
        stated_count = int(stated[0].group(1))
        if stated_count != len(present):
            fails.append(
                "skills/README.md states %d repo-owned skills but %d exist under skills/"
                % (stated_count, len(present))
            )

    return fails, []


def load_external_skills(repo_root):
    """Names listed in external-skills.txt (one per line, `#` comments); {} if absent."""
    text = read_text(os.path.join(repo_root, EXTERNAL_SKILLS_FILE))
    names = set()
    for line in (text or "").splitlines():
        name = line.split("#", 1)[0].strip()
        if name:
            names.add(name)
    return names


SECTION_HEADING_RE = re.compile(r"^#\s*([^\s/#]+/[^\s/#:]+(?::\S+)?)\s*$")


def external_skills_sections(repo_root):
    """external-skills.txt names grouped by `# <owner/repo>[:<subdir>]` heading."""
    text = read_text(os.path.join(repo_root, EXTERNAL_SKILLS_FILE))
    sections, current = {}, None
    for line in (text or "").splitlines():
        heading = SECTION_HEADING_RE.match(line.strip())
        if heading:
            current = sections.setdefault(heading.group(1), set())
            continue
        name = line.split("#", 1)[0].strip()
        if name and current is not None:
            current.add(name)
    return sections


def _audit_local():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit-local.py")
    spec = importlib.util.spec_from_file_location("audit_local", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses resolve their module by name
    spec.loader.exec_module(module)
    return module


def lint_external_drift(repo_root):
    """Fail where a cloned bare source ships different names than its section lists."""
    entries, _ = parse_plugins_file(os.path.join(repo_root, "plugins.txt"))
    sections = external_skills_sections(repo_root)
    audit = None
    fails, seen = [], set()
    for entry in entries:
        token = entry.source + (":" + entry.subdir if entry.subdir else "")
        clone = Path(repo_root, "vendor", audit_slug(entry.source))
        if entry.skills or token in seen or not clone.is_dir():
            continue
        seen.add(token)
        audit = audit or _audit_local()
        shipped = set(audit.discover_external_names(audit.external_source_root(clone, entry), entry))
        listed = sections.get(token, set())
        where = "%s section %r" % (EXTERNAL_SKILLS_FILE, token)
        if token not in sections:
            where = "%s has no section %r; it" % (EXTERNAL_SKILLS_FILE, token)
        missing, extra = sorted(shipped - listed), sorted(listed - shipped)
        if missing:
            fails.append("%s lacks names vendor/%s ships: %s" % (where, audit_slug(entry.source), ", ".join(missing)))
        if extra:
            fails.append("%s lists names vendor/%s does not ship: %s" % (where, audit_slug(entry.source), ", ".join(extra)))
    return fails


def audit_slug(source):
    """install.sh: slug="${repo%/*}-${repo#*/}"."""
    return source.replace("/", "-", 1)


def vendored_skill_name(skill_md):
    """A vendored skill's name: frontmatter `name:`, else its directory (as install.sh)."""
    text = read_text(skill_md)
    fields, _, _ = parse_frontmatter(text) if text else (None, None, None)
    name = fields.get("name") if fields else None
    value = (name.value or "").strip() if name is not None else ""
    return value or os.path.basename(os.path.dirname(skill_md))


def known_skills(repo_root, dirnames):
    """Live repo-owned skills + plugins.txt-named + external-skills.txt + cloned vendor/."""
    known = set(dirnames) | load_external_skills(repo_root)
    entries, _ = parse_plugins_file(os.path.join(repo_root, "plugins.txt"))
    for entry in entries:
        known.update(entry.skills)
        vendor = os.path.join(repo_root, "vendor", entry.source.replace("/", "-"))
        for dirpath, subdirs, files in os.walk(vendor):
            subdirs[:] = [d for d in subdirs if d not in (".git", "node_modules")]
            if "SKILL.md" in files:
                known.add(vendored_skill_name(os.path.join(dirpath, "SKILL.md")))
    return known


def _blank_fences(text):
    """Return text with fenced code block lines emptied (line numbers kept)."""
    out, fenced = [], False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            fenced = not fenced
            out.append("")
        else:
            out.append("" if fenced else line)
    return out


def _path_exists(target, file_dir, skill_dir, repo_root):
    target = target.split("#", 1)[0].rstrip(":")
    if not target:
        return True
    return any(
        os.path.exists(os.path.normpath(os.path.join(base, target)))
        for base in (file_dir, skill_dir, repo_root)
    )


def _lint_reference_file(path, skill_dir, repo_root, known):
    fails = []
    text = read_text(path)
    if text is None:
        return ["cannot read %s" % path]
    file_dir = os.path.dirname(path)
    rel = os.path.relpath(path, repo_root)
    lines = _blank_fences(text)

    for line_no, line in enumerate(lines, 1):
        gone = bool(GONE_RE.search(line))
        targets = [m for m in PATH_RE.findall(line)]
        targets += LINK_RE.findall(INLINE_CODE_RE.sub("", line))
        for target in targets:
            if SCHEME_RE.match(target) or target.startswith("#") or PLACEHOLDER_RE.search(target):
                continue
            if "_archive" in target.split("/") or target.endswith("/"):
                continue  # history citation, or a bare directory-convention mention
            if not _path_exists(target, file_dir, skill_dir, repo_root):
                fails.append("%s:%d: %s does not exist" % (rel, line_no, target))
        if gone:
            continue
        for regex in SKILL_REF_RES:
            for name in regex.findall(line):
                if name not in known:
                    fails.append("%s:%d: references unknown skill %r" % (rel, line_no, name))

    fields, _, _ = parse_frontmatter(text)
    desc = fields.get("description") if fields else None
    if desc is not None and desc.value:
        for sentence in NOT_FOR_RE.findall(desc.value):
            for group in PAREN_NAMES_RE.findall(sentence):
                for name in re.split(r"\s*(?:,|\bor\b|\band\b)\s*", group):
                    if name and name not in known:
                        fails.append(
                            "%s: description 'Not for' clause references unknown skill %r" % (rel, name)
                        )
    return fails


def lint_references(repo_root, dirnames):
    """Return fails for dangling paths and skill names (see module docstring)."""
    known = known_skills(repo_root, dirnames)
    fails = []
    for dirname in sorted(dirnames):
        skill_dir = os.path.join(repo_root, "skills", dirname)
        files = [os.path.join(skill_dir, "SKILL.md")]
        for dirpath, subdirs, names in os.walk(os.path.join(skill_dir, "references")):
            subdirs.sort()
            files += [os.path.join(dirpath, n) for n in sorted(names) if n.endswith(".md")]
        for path in files:
            fails += _lint_reference_file(path, skill_dir, repo_root, known)
    return fails


def lint_commands(repo_root, dirnames):
    """Fail where an omp/commands/*.md wrapper loads no skill, or one nothing ships."""
    known = known_skills(repo_root, dirnames)
    commands_dir = Path(repo_root, "omp", "commands")
    fails = []
    for path in sorted(commands_dir.glob("*.md")) if commands_dir.is_dir() else []:
        rel = path.relative_to(repo_root)
        names = SKILL_REF_RES[0].findall(read_text(str(path)) or "")
        if not names:
            fails.append("%s loads no skill:// URL" % rel)
        fails += ["%s loads unknown skill %r" % (rel, n) for n in names if n not in known]
    return fails


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
    print("skill references")
    ref_fails = lint_references(repo_root, sources)
    for detail in ref_fails:
        print("  FAIL  %s" % detail)
    if not ref_fails:
        print("  ok    no dangling paths or unknown skills in %d source skills" % len(sources))

    print()
    print("external-skills.txt drift")
    drift_fails = lint_external_drift(repo_root)
    for detail in drift_fails:
        print("  FAIL  %s" % detail)
    if not drift_fails:
        print("  ok    external-skills.txt matches every cloned bare source")

    print()
    print("omp command wrappers")
    cmd_fails = lint_commands(repo_root, sources)
    for detail in cmd_fails:
        print("  FAIL  %s" % detail)
    if not cmd_fails:
        print("  ok    every omp/commands wrapper loads a known skill")

    print()
    failed += len(cat_fails) + len(ref_fails) + len(drift_fails) + len(cmd_fails)
    summary = "%d passed, %d failed" % (passed, failed)
    if warned:
        summary += ", %d warnings (not fatal)" % warned
    print(summary)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
