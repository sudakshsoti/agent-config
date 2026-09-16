#!/usr/bin/env python3
"""build-dist.py — package the skills listed in distribution.txt for claude.ai.

Each listed skills/<name>/ becomes dist/<name>.zip, holding the skill folder at
the zip root (`<name>/SKILL.md`, `<name>/references/...`), which is the layout
claude.ai's skill upload expects.

The source SKILL.md is not zipped verbatim. claude.ai rejects any frontmatter
key outside name, description, license, allowed-tools, metadata and
compatibility, and the harness-only `disable-model-invocation` would fail the
upload, so disallowed keys are stripped from the packaged copy. The packaged
skill is then validated against the upload rules, so a zip that exists is one
that will import.

Zips are deterministic (sorted entries, fixed timestamps and modes) and are only
rewritten when their contents change, so an unchanged skill never produces a
diff. Staleness is judged by contents rather than zip bytes: zlib output can
differ between machines.

  ./scripts/build-dist.py [repo-root]               build from the working tree
  ./scripts/build-dist.py [repo-root] --from-index  build from the staged tree
  ./scripts/build-dist.py [repo-root] --check       report stale zips, write nothing

The pre-commit hook uses --from-index, so a zip matches what is being
committed; check.sh uses --check. Exit 1 on a validation failure or, with
--check, on any stale, missing or unlisted zip.
"""

import importlib.util
import io
import os
import re
import subprocess
import sys
import tempfile
import zipfile

MANIFEST = "distribution.txt"
DIST = "dist"
ALLOWED_KEYS = ("name", "description", "license", "allowed-tools", "metadata", "compatibility")
EXCLUDED_NAMES = {".DS_Store", "Thumbs.db"}
EXCLUDED_DIRS = {"__pycache__", "node_modules", ".git"}
ZIP_DATE = (1980, 1, 1, 0, 0, 0)
KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_.-]*):")
MAX_COMPATIBILITY = 500

_lint_spec = importlib.util.spec_from_file_location(
    "lint_skills", os.path.join(os.path.dirname(os.path.abspath(__file__)), "lint-skills.py")
)
lint = importlib.util.module_from_spec(_lint_spec)
_lint_spec.loader.exec_module(lint)


class BuildError(Exception):
    pass


def git(root, *args, binary=False):
    result = subprocess.run(
        ["git", "-C", root, *args], capture_output=True, text=not binary, check=False
    )
    if result.returncode != 0:
        stderr = result.stderr if not binary else result.stderr.decode(errors="replace")
        raise BuildError("git %s failed: %s" % (" ".join(args), stderr.strip()))
    return result.stdout


class WorkingTree:
    """Tracked plus untracked-but-not-ignored files, read from disk."""

    def __init__(self, root):
        self.root = root
        try:
            git(root, "rev-parse", "--is-inside-work-tree")
            self.in_git = True
        except (BuildError, FileNotFoundError):
            self.in_git = False

    def read(self, relpath):
        path = os.path.join(self.root, relpath)
        if not os.path.isfile(path):
            return None
        with open(path, "rb") as fh:
            return fh.read()

    def files(self, prefix):
        """Yield (relpath-within-prefix, bytes, executable)."""
        base = os.path.join(self.root, prefix)
        if self.in_git:
            out = git(self.root, "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", prefix + "/")
            paths = sorted({p for p in out.split("\0") if p})
        else:
            paths = []
            for dirpath, dirnames, filenames in os.walk(base):
                dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
                for f in filenames:
                    paths.append(os.path.relpath(os.path.join(dirpath, f), self.root))
        for relpath in paths:
            path = os.path.join(self.root, relpath)
            if os.path.islink(path):
                raise BuildError("%s is a symlink; claude.ai zips cannot carry links" % relpath)
            if not os.path.isfile(path):
                continue  # tracked but deleted in the working tree
            with open(path, "rb") as fh:
                data = fh.read()
            yield os.path.relpath(path, base), data, bool(os.stat(path).st_mode & 0o111)


class Index:
    """The staged tree: what the commit in progress will contain."""

    def __init__(self, root):
        self.root = root

    def read(self, relpath):
        out = git(self.root, "ls-files", "-s", "-z", "--", relpath)
        entry = next((e for e in out.split("\0") if e), None)
        if entry is None:
            return None
        return git(self.root, "cat-file", "blob", entry.split()[1], binary=True)

    def files(self, prefix):
        out = git(self.root, "ls-files", "-s", "-z", "--", prefix + "/")
        for entry in sorted(e for e in out.split("\0") if e):
            meta, relpath = entry.split("\t", 1)
            mode, sha = meta.split()[:2]
            if mode == "120000":
                raise BuildError("%s is a symlink; claude.ai zips cannot carry links" % relpath)
            if mode == "160000":
                continue  # submodule
            data = git(self.root, "cat-file", "blob", sha, binary=True)
            yield relpath[len(prefix) + 1 :], data, mode == "100755"


def parse_manifest(text):
    names, errors = [], []
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if not lint.NAME_RE.match(line):
            errors.append("%s:%d: %r is not a skill name" % (MANIFEST, lineno, line))
        elif line in names:
            errors.append("%s:%d: %r is listed twice" % (MANIFEST, lineno, line))
        else:
            names.append(line)
    return names, errors


def strip_frontmatter(text):
    """Drop top-level frontmatter keys claude.ai rejects. Returns (text, dropped)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return text, []
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return text, []
    kept, dropped, dropping = [], [], False
    for line in lines[1:end]:
        m = KEY_RE.match(line)
        if m:
            dropping = m.group(1) not in ALLOWED_KEYS
            if dropping:
                dropped.append(m.group(1))
        elif line.strip() and not line[:1].isspace() and not line.lstrip().startswith("#"):
            dropping = False
        if not dropping:
            kept.append(line)
    return "\n".join([lines[0], *kept, *lines[end:]]), dropped


def validate(name, entries):
    """claude.ai upload rules, applied to the packaged copy."""
    fails = []
    skill_mds = [p for p in entries if p.rsplit("/", 1)[-1] == "SKILL.md"]
    if skill_mds != ["SKILL.md"]:
        fails.append("needs exactly one SKILL.md, at the skill root (found %s)" % (skill_mds or "none"))
    if "SKILL.md" not in entries:
        return fails
    fields, body, error = lint.parse_frontmatter(entries["SKILL.md"][0].decode("utf-8"))
    if error:
        return fails + [error]
    for key in fields:
        if key not in ALLOWED_KEYS:
            fails.append("frontmatter key %r is not accepted by claude.ai" % key)
    field = fields.get("name")
    value = (field.value or "").strip() if field else ""
    if value != name:
        fails.append("name %r does not match %r" % (value, name))
    if len(value) > lint.MAX_NAME or not lint.NAME_RE.match(value) or "--" in value:
        fails.append("name %r is not ≤%d chars of [a-z0-9-]" % (value, lint.MAX_NAME))
    if value.startswith("-") or value.endswith("-"):
        fails.append("name %r starts or ends with a hyphen" % value)
    if any(banned in value for banned in lint.BANNED_IN_NAME):
        fails.append("name %r contains a reserved word" % value)
    field = fields.get("description")
    desc = (field.value or "").strip() if field and field.style != "mapping" else ""
    if not desc:
        fails.append("no `description` string in frontmatter")
    if len(desc) > lint.MAX_DESCRIPTION:
        fails.append("description is %d chars, max %d" % (len(desc), lint.MAX_DESCRIPTION))
    if "<" in desc or ">" in desc:
        fails.append("description contains an angle bracket")
    field = fields.get("compatibility")
    if field and len((field.value or "").strip()) > MAX_COMPATIBILITY:
        fails.append("compatibility is over %d chars" % MAX_COMPATIBILITY)
    if not body.strip():
        fails.append("SKILL.md has no body")
    return fails


def package(source, name):
    """Return {relpath: (bytes, executable)} for skills/<name>, ready to zip."""
    entries = {}
    for relpath, data, executable in source.files("skills/" + name):
        relpath = relpath.replace(os.sep, "/")
        parts = relpath.split("/")
        if parts[-1] in EXCLUDED_NAMES or any(p in EXCLUDED_DIRS for p in parts[:-1]):
            continue
        entries[relpath] = (data, executable)
    if "SKILL.md" in entries:
        text, _ = strip_frontmatter(entries["SKILL.md"][0].decode("utf-8"))
        entries["SKILL.md"] = (text.encode("utf-8"), entries["SKILL.md"][1])
    return entries


def zip_bytes(name, entries):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for relpath in sorted(entries):
            data, executable = entries[relpath]
            info = zipfile.ZipInfo("%s/%s" % (name, relpath), date_time=ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = ((0o100755 if executable else 0o100644) & 0xFFFF) << 16
            zf.writestr(info, data, compresslevel=9)
    return buf.getvalue()


def zip_contents(path):
    """{relpath: (bytes, executable)} of an existing zip, or None if unreadable."""
    try:
        with zipfile.ZipFile(path) as zf:
            out = {}
            for info in zf.infolist():
                if info.is_dir():
                    continue
                name, _, relpath = info.filename.partition("/")
                out[(name, relpath)] = (zf.read(info), bool((info.external_attr >> 16) & 0o111))
            return out
    except (OSError, zipfile.BadZipFile):
        return None


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    unknown = flags - {"--check", "--from-index"}
    if unknown or len(args) > 1 or flags >= {"--check", "--from-index"}:
        print("usage: build-dist.py [repo-root] [--check | --from-index]", file=sys.stderr)
        return 2
    root = os.path.abspath(args[0] if args else os.path.join(os.path.dirname(__file__), ".."))
    check = "--check" in flags
    try:
        source = Index(root) if "--from-index" in flags else WorkingTree(root)
        manifest = source.read(MANIFEST)
    except BuildError as exc:
        print("build-dist: %s" % exc, file=sys.stderr)
        return 1
    if manifest is None:
        print("build-dist: no %s; nothing to distribute" % MANIFEST)
        return 0
    names, errors = parse_manifest(manifest.decode("utf-8"))

    dist = os.path.join(root, DIST)
    wanted, stale = {}, []
    for name in names:
        try:
            entries = package(source, name)
        except BuildError as exc:
            errors.append("%s: %s" % (name, exc))
            continue
        if not entries:
            errors.append("%s: listed in %s but skills/%s has no files" % (name, MANIFEST, name))
            continue
        fails = validate(name, entries)
        if fails:
            errors.extend("%s: %s" % (name, f) for f in fails)
            continue
        wanted[name] = entries
        expected = {(name, p): v for p, v in entries.items()}
        if zip_contents(os.path.join(dist, name + ".zip")) != expected:
            stale.append(name)

    existing = sorted(f[:-4] for f in os.listdir(dist) if f.endswith(".zip")) if os.path.isdir(dist) else []
    unlisted = [n for n in existing if n not in names]

    if errors:
        for e in errors:
            print("  FAIL  %s" % e)
        print("build-dist: %d problem(s); no zips written" % len(errors))
        return 1

    if check:
        for n in stale:
            print("  STALE %s" % os.path.join(DIST, n + ".zip"))
        for n in unlisted:
            print("  UNLISTED %s" % os.path.join(DIST, n + ".zip"))
        if stale or unlisted:
            print("build-dist: dist/ is out of date; run ./scripts/build-dist.py")
            return 1
        print("build-dist: %d zip(s) up to date" % len(names))
        return 0

    os.makedirs(dist, exist_ok=True)
    for name in stale:
        target = os.path.join(dist, name + ".zip")
        fd, tmp = tempfile.mkstemp(dir=dist, suffix=".tmp")
        with os.fdopen(fd, "wb") as fh:
            fh.write(zip_bytes(name, wanted[name]))
        os.chmod(tmp, 0o644)
        os.replace(tmp, target)
        print("  built   %s" % os.path.join(DIST, name + ".zip"))
    for name in unlisted:
        os.remove(os.path.join(dist, name + ".zip"))
        print("  removed %s" % os.path.join(DIST, name + ".zip"))
    print("build-dist: %d zip(s) up to date" % len(names))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
