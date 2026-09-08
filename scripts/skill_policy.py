#!/usr/bin/env python3
"""Policy validation and safe materialisation for agent skills.

This module deliberately has no YAML dependency.  Skill frontmatter is parsed
using the same small scalar subset as ``lint-skills.py`` and is rewritten as
text so metadata that this policy does not own remains byte-for-byte intact.
"""

import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import uuid
from pathlib import Path


KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_.-]*):(.*)$")
NAME_RE = re.compile(r"^[a-z0-9-]+$")
TOP_LEVEL_KEYS = {"version", "budgets", "skills", "ompLocalSkills"}
BUDGET_KEYS = {"manualAwareDescriptionCharacters", "alwaysListedDescriptionCharacters"}
SHARED_ENTRY_KEYS = {"exposure", "description"}
OMP_ENTRY_KEYS = {"root", "exposure", "description"}


class PolicyError(ValueError):
    """A policy, source skill, or atomic update failed validation."""


class DuplicateKeyError(ValueError):
    pass


def _pairs_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError("duplicate JSON key: %s" % key)
        result[key] = value
    return result


def _word_count(description):
    return len(description.split())


def _check_entry(name, entry, allowed, kind):
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        raise PolicyError("invalid %s skill name: %r" % (kind, name))
    if not isinstance(entry, dict):
        raise PolicyError("%s entry %s must be an object" % (kind, name))
    unknown = sorted(set(entry) - allowed)
    missing = sorted(allowed - set(entry))
    if unknown:
        raise PolicyError("unknown fields in %s.%s: %s" % (kind, name, ", ".join(unknown)))
    if missing:
        raise PolicyError("missing fields in %s.%s: %s" % (kind, name, ", ".join(missing)))
    exposure = entry["exposure"]
    if exposure not in ("manual", "automatic"):
        raise PolicyError("invalid exposure for %s.%s: %r" % (kind, name, exposure))
    description = entry["description"]
    if not isinstance(description, str) or not description.strip():
        raise PolicyError("missing description for %s.%s" % (kind, name))
    if "\n" in description or "\r" in description:
        raise PolicyError("description for %s.%s must be one line" % (kind, name))
    words = _word_count(description)
    lower, upper = (10, 25) if exposure == "manual" else (25, 45)
    if not lower <= words <= upper:
        raise PolicyError(
            "%s.%s description has %d words; expected %d-%d"
            % (kind, name, words, lower, upper)
        )


def validate_policy(policy):
    """Validate the complete policy object and return it."""
    if not isinstance(policy, dict):
        raise PolicyError("policy must be a JSON object")
    unknown = sorted(set(policy) - TOP_LEVEL_KEYS)
    missing = sorted(TOP_LEVEL_KEYS - set(policy))
    if unknown:
        raise PolicyError("unknown policy fields: %s" % ", ".join(unknown))
    if missing:
        raise PolicyError("missing policy fields: %s" % ", ".join(missing))
    if policy["version"] != 1:
        raise PolicyError("unsupported policy version: %r" % (policy["version"],))
    budgets = policy["budgets"]
    if not isinstance(budgets, dict):
        raise PolicyError("budgets must be an object")
    unknown = sorted(set(budgets) - BUDGET_KEYS)
    missing = sorted(BUDGET_KEYS - set(budgets))
    if unknown:
        raise PolicyError("unknown budget fields: %s" % ", ".join(unknown))
    if missing:
        raise PolicyError("missing budget fields: %s" % ", ".join(missing))
    for key in BUDGET_KEYS:
        value = budgets[key]
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise PolicyError("budget %s must be a positive integer" % key)

    skills = policy["skills"]
    if not isinstance(skills, dict) or not skills:
        raise PolicyError("skills must be a non-empty object")
    for name in sorted(skills):
        _check_entry(name, skills[name], SHARED_ENTRY_KEYS, "skills")

    omp = policy["ompLocalSkills"]
    if not isinstance(omp, dict) or not omp:
        raise PolicyError("ompLocalSkills must be a non-empty object")
    for name in sorted(omp):
        _check_entry(name, omp[name], OMP_ENTRY_KEYS, "ompLocalSkills")
        if omp[name]["root"] not in ("skills", "managed-skills"):
            raise PolicyError("invalid root for ompLocalSkills.%s: %r" % (name, omp[name]["root"]))
    return policy


def load_policy(path):
    """Load, validate, and return a policy JSON object."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            policy = json.load(fh, object_pairs_hook=_pairs_no_duplicates)
    except DuplicateKeyError as exc:
        raise PolicyError(str(exc)) from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PolicyError("cannot read policy %s: %s" % (path, exc)) from exc
    return validate_policy(policy)


class Field:
    """Parsed top-level frontmatter field, matching lint-skills.py's contract."""

    def __init__(self, value, style, multiline=False):
        self.value = value
        self.style = style
        self.multiline = multiline


def _is_continuation(line):
    if not line.strip():
        return False
    return line[:1].isspace() or (KEY_RE.match(line) is None and line.strip() != "---")


def _close_quote(text, quote):
    i = 0
    while i < len(text):
        if quote == '"' and text[i] == "\\":
            i += 2
            continue
        if text[i] == quote:
            if quote == "'" and text[i + 1 : i + 2] == "'":
                i += 2
                continue
            return i + 1
        i += 1
    return -1


def parse_frontmatter(text):
    """Return ``(fields, body, error)`` using lint-skills.py's scalar subset."""
    if not isinstance(text, str):
        return None, None, "skill text must be a string"
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
    fields = {}
    fm = lines[1:end]
    i = 0
    while i < len(fm):
        line = fm[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        match = KEY_RE.match(line)
        if not match:
            return None, None, "line %d is not a top-level key: %r" % (i + 2, line)
        key, rest = match.group(1), match.group(2)
        if key in fields:
            return None, None, "duplicate frontmatter key: %s" % key
        stripped = rest.strip()
        i += 1
        if stripped[:1] in ("|", ">"):
            chunk = []
            while i < len(fm) and (not fm[i].strip() or fm[i][:1].isspace()):
                chunk.append(fm[i].strip())
                i += 1
            while chunk and not chunk[-1]:
                chunk.pop()
            fields[key] = Field(" ".join(c for c in chunk if c), "block", len([c for c in chunk if c]) > 1)
            continue
        if stripped == "":
            if i < len(fm) and fm[i].strip() and fm[i][:1].isspace():
                mapping = KEY_RE.match(fm[i].strip()) is not None
                chunk = []
                while i < len(fm) and (not fm[i].strip() or fm[i][:1].isspace()):
                    chunk.append(fm[i].strip())
                    i += 1
                chunk = [c for c in chunk if c]
                fields[key] = Field(None if mapping else " ".join(chunk), "mapping" if mapping else "plain", not mapping)
            else:
                fields[key] = Field("", "empty")
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
            if closed == -1:
                return None, None, "unterminated quoted value for %s" % key
            fields[key] = Field(" ".join(parts)[1:-1], "quoted", multiline)
            continue
        parts = [stripped]
        multiline = False
        while i < len(fm) and _is_continuation(fm[i]):
            multiline = True
            parts.append(fm[i].strip())
            i += 1
        fields[key] = Field(" ".join(parts), "plain", multiline)
    return fields, "\n".join(lines[end + 1 :]), None


def _frontmatter_lines(text):
    """Return split lines, closing index, and exact body offset."""
    lines = text.splitlines(keepends=True)
    if not lines:
        raise PolicyError("no YAML frontmatter (file must open with ---)")
    if lines[0].rstrip("\r\n").strip() != "---":
        raise PolicyError("no YAML frontmatter (file must open with ---)")
    for index in range(1, len(lines)):
        if lines[index].rstrip("\r\n").strip() == "---":
            return lines, index
    raise PolicyError("frontmatter is never closed (no second ---)")


def _line_ending(line, fallback="\n"):
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    return fallback


def _consume_field(lines, index, end):
    """Consume a field and its continuation lines, returning the next index."""
    match = KEY_RE.match(lines[index].rstrip("\r\n"))
    if not match:
        return index + 1
    stripped = match.group(2).strip()
    next_index = index + 1
    if stripped[:1] in ("|", ">"):
        while next_index < end and (not lines[next_index].strip() or lines[next_index][:1].isspace()):
            next_index += 1
    elif stripped == "":
        while next_index < end and (not lines[next_index].strip() or lines[next_index][:1].isspace()):
            next_index += 1
    elif stripped[:1] in ("'", '"'):
        quote = stripped[0]
        closed = _close_quote(stripped[1:], quote)
        while closed == -1 and next_index < end:
            closed = _close_quote(lines[next_index].rstrip("\r\n"), quote)
            next_index += 1
    else:
        while next_index < end and _is_continuation(lines[next_index].rstrip("\r\n")):
            next_index += 1
    return next_index


def rewrite_frontmatter(text, description, exposure):
    """Rewrite owned fields while preserving unknown metadata and body exactly."""
    if not isinstance(description, str) or "\n" in description or "\r" in description:
        raise PolicyError("description must be a one-line string")
    if exposure not in ("manual", "automatic"):
        raise PolicyError("exposure must be manual or automatic")
    fields, _body, error = parse_frontmatter(text)
    if error:
        raise PolicyError(error)
    lines, end = _frontmatter_lines(text)
    newline = _line_ending(lines[0])
    out = []
    seen_description = False
    seen_disable = False
    quoted = json.dumps(description, ensure_ascii=False)
    i = 1
    while i < end:
        match = KEY_RE.match(lines[i].rstrip("\r\n"))
        key = match.group(1) if match else None
        if key == "description":
            ending = _line_ending(lines[i], newline)
            out.append("description: %s%s" % (quoted, ending))
            seen_description = True
            i = _consume_field(lines, i, end)
            continue
        if key == "disable-model-invocation":
            ending = _line_ending(lines[i], newline)
            if exposure == "manual":
                out.append("disable-model-invocation: true%s" % ending)
                seen_disable = True
            i = _consume_field(lines, i, end)
            continue
        out.append(lines[i])
        i += 1
    if not seen_description:
        ending = _line_ending(lines[end - 1], newline) if end else newline
        out.append("description: %s%s" % (quoted, ending))
    if exposure == "manual" and not seen_disable:
        ending = _line_ending(lines[end - 1], newline) if end else newline
        out.append("disable-model-invocation: true%s" % ending)
    return "".join(lines[:1] + out + lines[end:])


def _source_text(source_dir):
    path = os.path.join(os.fspath(source_dir), "SKILL.md")
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
        text = raw.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise PolicyError("cannot read %s: %s" % (path, exc)) from exc
    return path, raw, text


def _validate_source(source_dir, entry):
    if not isinstance(entry, dict):
        raise PolicyError("source policy entry must be an object")
    name = entry.get("name") or entry.get("_name")
    if not name:
        raise PolicyError("source policy entry is missing its name")
    path, raw, text = _source_text(source_dir)
    fields, _body, error = parse_frontmatter(text)
    if error:
        raise PolicyError("%s: %s" % (path, error))
    if "name" not in fields or fields["name"].value != name:
        actual = fields.get("name").value if "name" in fields else None
        raise PolicyError("%s declares name %r, expected %r" % (path, actual, name))
    if "description" not in fields:
        raise PolicyError("%s has no description" % path)
    return path, raw, text


def materialise_external_skill(source_dir, output_dir, entry):
    """Atomically rebuild an external skill overlay and return its output path."""
    source_dir = os.path.abspath(os.fspath(source_dir))
    output_dir = os.path.abspath(os.fspath(output_dir))
    name = (
        (entry.get("name") or entry.get("_name"))
        if isinstance(entry, dict)
        else None
    )
    if not name:
        name = os.path.basename(output_dir)
    if not name:
        raise PolicyError("materialisation entry is missing its name")
    if os.path.abspath(source_dir) == output_dir:
        raise PolicyError("source and output directories must differ")
    path, _raw, text = _validate_source(
        source_dir, dict(entry, name=name) if isinstance(entry, dict) else entry
    )
    rewritten = rewrite_frontmatter(text, entry["description"], entry["exposure"]).encode("utf-8")
    parent = os.path.dirname(output_dir)
    os.makedirs(parent, exist_ok=True)
    temp_dir = tempfile.mkdtemp(prefix=".%s.policy-" % name, dir=parent)
    backup = None
    try:
        target = os.path.join(temp_dir, "SKILL.md")
        with open(target, "wb") as fh:
            fh.write(rewritten)
        os.chmod(target, stat.S_IMODE(os.stat(path).st_mode))
        for child in os.scandir(source_dir):
            if child.name == "SKILL.md":
                continue
            link = os.path.join(temp_dir, child.name)
            os.symlink(os.path.relpath(os.path.join(source_dir, child.name), temp_dir), link)
        if os.path.lexists(output_dir):
            backup = os.path.join(parent, ".%s.old-%s" % (os.path.basename(output_dir), uuid.uuid4().hex))
            os.replace(output_dir, backup)
        try:
            os.replace(temp_dir, output_dir)
        except Exception:
            if backup is not None and os.path.lexists(backup):
                os.replace(backup, output_dir)
            raise
        temp_dir = None
        if backup is not None and os.path.lexists(backup):
            shutil.rmtree(backup) if os.path.isdir(backup) and not os.path.islink(backup) else os.unlink(backup)
        return output_dir
    finally:
        if temp_dir is not None and os.path.lexists(temp_dir):
            shutil.rmtree(temp_dir)


def _read_and_hash(path):
    with open(path, "rb") as fh:
        data = fh.read()
    return data, hashlib.sha256(data).digest()


def _atomic_backup(path, backup_path, data):
    if os.path.exists(backup_path):
        return
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".backup-", dir=os.path.dirname(backup_path))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temporary, backup_path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def apply_omp_local(omp_root, entries):
    """Apply OMP-local policy entries, preserving backups and racing safely.

    Missing entries are optional and produce warnings; successfully processed
    paths are returned as a list.
    """
    if not isinstance(entries, dict):
        raise PolicyError("OMP-local entries must be an object")
    applied = []
    for name in sorted(entries):
        entry = dict(entries[name])
        entry["name"] = name
        root = entry.get("root")
        target = os.path.join(os.fspath(omp_root), root, name, "SKILL.md")
        if not os.path.isfile(target):
            print("warning: optional OMP-local skill missing: %s" % target, file=sys.stderr)
            continue
        original, original_hash = _read_and_hash(target)
        try:
            text = original.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PolicyError("%s is not UTF-8: %s" % (target, exc)) from exc
        fields, _body, error = parse_frontmatter(text)
        if error:
            raise PolicyError("%s: %s" % (target, error))
        if "name" not in fields or fields["name"].value != name:
            raise PolicyError("%s declares the wrong skill name" % target)
        rewritten = rewrite_frontmatter(text, entry["description"], entry["exposure"]).encode("utf-8")
        current, current_hash = _read_and_hash(target)
        if current_hash != original_hash or current != original:
            raise PolicyError("OMP-local skill changed while applying policy: %s" % target)
        backup = os.path.join(os.fspath(omp_root), "skill-policy-backups", root, name, "SKILL.md")
        _atomic_backup(target, backup, original)
        mode = stat.S_IMODE(os.stat(target).st_mode)
        fd, temporary = tempfile.mkstemp(prefix=".skill-policy-", dir=os.path.dirname(target))
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(rewritten)
                fh.flush()
                os.fsync(fh.fileno())
            os.chmod(temporary, mode)
            current, current_hash = _read_and_hash(target)
            if current_hash != original_hash or current != original:
                raise PolicyError("OMP-local skill changed while applying policy: %s" % target)
            os.replace(temporary, target)
            temporary = None
        finally:
            if temporary is not None and os.path.exists(temporary):
                os.unlink(temporary)
        applied.append(target)
    return applied


def _vendor_sources(vendor_root):
    result = {}
    if not os.path.isdir(vendor_root):
        return result
    for root, dirs, files in os.walk(vendor_root):
        dirs[:] = [d for d in dirs if d != ".git"]
        if "SKILL.md" not in files:
            continue
        name = os.path.basename(root)
        try:
            with open(os.path.join(root, "SKILL.md"), "r", encoding="utf-8") as fh:
                fields, _body, error = parse_frontmatter(fh.read())
            if not error and fields and fields.get("name") and fields["name"].value:
                name = fields["name"].value
        except (OSError, UnicodeError):
            pass
        result.setdefault(name, []).append(root)
    return result


def inventory_sources(repo_root, vendor_root, names):
    """Resolve policy names to local or vendor source directories."""
    repo_skills = os.path.join(os.fspath(repo_root), "skills")
    vendor = _vendor_sources(vendor_root)
    sources = {}
    for name in sorted(names):
        local = os.path.join(repo_skills, name)
        if os.path.isfile(os.path.join(local, "SKILL.md")):
            sources[name] = [local]
            continue
        # A checkout can contain several copies of one plugin skill (axiom
        # carries cursor, codex, and plugin trees). One deterministic source is
        # enough for this pre-write validation.
        sources[name] = sorted(vendor.get(name, []))[:1]
    return sources


def validate_inventory(policy, repo_root, vendor_root, omp_root=None):
    """Validate source inventory and return sorted human-readable errors."""
    names = set(policy["skills"])
    sources = inventory_sources(repo_root, vendor_root, names)
    errors = []
    repo_skills = os.path.join(os.fspath(repo_root), "skills")
    if os.path.isdir(repo_skills):
        unexpected = sorted(
            entry.name
            for entry in os.scandir(repo_skills)
            if entry.is_dir()
            and os.path.isfile(os.path.join(entry.path, "SKILL.md"))
            and entry.name not in names
        )
        if unexpected:
            errors.append("unexpected repo skills: %s" % ", ".join(unexpected))
    missing = sorted(name for name, paths in sources.items() if not paths)
    if missing:
        errors.append("missing shared skills: %s" % ", ".join(missing))
    for name in sorted(sources):
        for source in sources[name]:
            entry = dict(policy["skills"][name])
            entry["name"] = name
            try:
                _validate_source(source, entry)
            except PolicyError as exc:
                errors.append(str(exc))
    if omp_root is not None:
        for name, entry in sorted(policy["ompLocalSkills"].items()):
            target = os.path.join(os.fspath(omp_root), entry["root"], name, "SKILL.md")
            if not os.path.isfile(target):
                print("warning: optional OMP-local skill missing: %s" % target, file=sys.stderr)
    return sorted(errors)


__all__ = [
    "PolicyError",
    "Field",
    "load_policy",
    "parse_frontmatter",
    "rewrite_frontmatter",
    "materialise_external_skill",
    "apply_omp_local",
    "validate_inventory",
]
