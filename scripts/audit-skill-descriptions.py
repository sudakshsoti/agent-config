#!/usr/bin/env python3
"""Report skill description budgets and fail on policy or inventory drift.

The policy is the source of truth for managed descriptions.  External vendor
copies intentionally retain their upstream frontmatter; generated overlays are
checked when present.  Provider-specific discovery is reported separately so
unmanaged plugin skills never silently consume a managed budget.
"""

import argparse
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from skill_policy import (  # noqa: E402
    PolicyError,
    load_policy,
    parse_frontmatter,
    validate_inventory,
)


TOOLS = ("omp", "claude", "pi", "codex", "opencode")
EXPECTED_SHARED = 112
EXPECTED_OMP_LOCAL = 7
OVERRIDE_VALUES = {"off", "user-invocable-only", "name-only"}




def _settings_path():
    return Path(os.environ.get("CLAUDE_SETTINGS", str(Path.home() / ".claude" / "settings.json")))


def _load_overrides(path):
    """Load Claude skillOverrides, returning (overrides, errors)."""
    if not path.is_file():
        return {}, []
    try:
        with path.open("r", encoding="utf-8") as fh:
            settings = json.load(fh)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {}, ["cannot read Claude settings %s: %s" % (path, exc)]
    if not isinstance(settings, dict):
        return {}, ["Claude settings %s must be a JSON object" % path]
    overrides = settings.get("skillOverrides", {})
    if overrides is None:
        return {}, []
    if not isinstance(overrides, dict):
        return {}, ["Claude settings skillOverrides must be an object"]
    errors = []
    for name, value in sorted(overrides.items()):
        if not isinstance(name, str) or not isinstance(value, str):
            errors.append("Claude skillOverrides entries must map names to strings: %r" % ((name, value),))
        elif value not in OVERRIDE_VALUES:
            errors.append("unsupported Claude skillOverrides.%s value: %s" % (name, value))
    return overrides, errors


def _description_row(name, entry, source="shared", override=None):
    description = entry["description"]
    if override == "name-only":
        description = "(name only)"
        characters = 0
    else:
        characters = len(description)
    return {
        "name": name,
        "exposure": entry["exposure"],
        "characters": characters,
        "tokens": characters / 4,
        "description": description,
        "source": source,
        "override": override,
    }


def _rows(policy, tool, overrides):
    """Return the exact policy-managed membership for one provider."""
    rows = []
    if tool in ("codex", "opencode"):
        for name, entry in policy["skills"].items():
            rows.append(_description_row(name, entry))
        return sorted(rows, key=lambda row: (-row["characters"], row["name"]))

    for name, entry in policy["skills"].items():
        if entry["exposure"] != "automatic":
            continue
        override = overrides.get(name) if tool == "claude" else None
        if override in ("off", "user-invocable-only"):
            continue
        rows.append(_description_row(name, entry, override=override))

    if tool == "omp":
        for name, entry in policy["ompLocalSkills"].items():
            if entry["exposure"] == "automatic":
                rows.append(_description_row(name, entry, source="omp-local"))
    return sorted(rows, key=lambda row: (-row["characters"], row["name"]))


def _provider_roots():
    home = Path.home()
    return (
        ("Claude plugins", home / ".claude" / "plugins"),
        ("Claude local", home / ".claude" / "skills"),
        ("OMP local", home / ".omp" / "agent" / "skills"),
        ("OMP managed", home / ".omp" / "agent" / "managed-skills"),
        ("pi", home / ".pi" / "agent" / "skills"),
        ("Codex", home / ".codex" / "skills"),
        ("OpenCode", home / ".config" / "opencode" / "skills"),
    )


def _unmanaged(policy):
    """Discover provider skills not represented by the tracked policy."""
    managed = set(policy["skills"]) | set(policy["ompLocalSkills"])
    found = []
    seen = set()
    for provider, root in _provider_roots():
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("SKILL.md")):
            try:
                resolved = path.resolve()
            except OSError:
                resolved = path
            if resolved in seen:
                continue
            seen.add(resolved)
            try:
                text = path.read_text(encoding="utf-8")
                fields, _body, error = parse_frontmatter(text)
            except (OSError, UnicodeError) as exc:
                found.append((provider, path.name, 0, 0, "(unreadable: %s)" % exc))
                continue
            if error or not fields or "description" not in fields or not fields["description"].value:
                name = path.parent.name
                description = "(invalid or missing description)"
            else:
                name = fields.get("name").value if fields.get("name") else path.parent.name
                description = fields["description"].value
            if name in managed:
                continue
            characters = len(description)
            found.append((provider, name, characters, characters / 4, description))
    return sorted(found, key=lambda row: (-row[2], row[0], row[1], row[4]))


def _source_description(path):
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return None, "cannot read %s: %s" % (path, exc)
    fields, _body, error = parse_frontmatter(text)
    if error:
        return None, "%s: %s" % (path, error)
    return fields, None


def _check_drift(policy, overrides, root):
    """Return sorted policy/inventory/description drift messages."""
    errors = []
    if len(policy["skills"]) != EXPECTED_SHARED:
        errors.append("policy shared inventory has %d skills; expected %d" % (len(policy["skills"]), EXPECTED_SHARED))
    if len(policy["ompLocalSkills"]) != EXPECTED_OMP_LOCAL:
        errors.append("policy OMP-local inventory has %d skills; expected %d" % (len(policy["ompLocalSkills"]), EXPECTED_OMP_LOCAL))

    vendor_root = root / "vendor"
    errors.extend(validate_inventory(policy, str(root), str(vendor_root)))

    installed = Path.home() / ".agents" / "skills"
    if installed.is_dir():
        installed_names = {entry.name for entry in installed.iterdir() if entry.is_dir()}
        managed_names = set(policy["skills"])
        missing = sorted(managed_names - installed_names)
        extra = sorted(installed_names - managed_names)
        if missing:
            errors.append("installed shared inventory missing: %s" % ", ".join(missing))
        if extra:
            errors.append("unexpected installed shared skills: %s" % ", ".join(extra))

    # Repo-owned skills are policy materialised in place. Vendor copies are
    # deliberately excluded: their generated overlays carry the policy text.
    for name, entry in sorted(policy["skills"].items()):
        source = root / "skills" / name / "SKILL.md"
        if not source.is_file():
            continue
        fields, error = _source_description(source)
        if error:
            errors.append(error)
            continue
        if fields.get("name") is None or fields["name"].value != name:
            errors.append("%s declares name %r, expected %r" % (source, fields.get("name").value if fields.get("name") else None, name))
        if fields.get("description") is None or fields["description"].value != entry["description"]:
            errors.append("%s description differs from policy" % source)
        flag = fields.get("disable-model-invocation")
        has_manual_flag = flag is not None and str(flag.value).strip().lower() in ("true", "yes")
        if entry["exposure"] == "manual" and not has_manual_flag:
            errors.append("%s manual policy entry lacks disable-model-invocation: true" % source)
        if entry["exposure"] == "automatic" and flag is not None:
            errors.append("%s automatic policy entry has disable-model-invocation" % source)

    generated = root / ".generated" / "skills"
    if generated.is_dir():
        for name, entry in sorted(policy["skills"].items()):
            source = generated / name / "SKILL.md"
            if not source.is_file():
                continue
            fields, error = _source_description(source)
            if error:
                errors.append(error)
                continue
            if fields.get("description") is None or fields["description"].value != entry["description"]:
                errors.append("%s description differs from policy" % source)

    # Overrides can only shrink the automatic Claude catalogue. Unknown names
    # are allowed because Claude plugins are intentionally unbudgeted.
    for name, value in sorted(overrides.items()):
        if name in policy["skills"] and value not in OVERRIDE_VALUES:
            errors.append("unsupported Claude override for managed skill %s: %s" % (name, value))
    return sorted(set(errors))


def _render_rows(rows, limit):
    print("skill | exposure | characters | estimated tokens | effective description")
    print("----- | -------- | ---------- | ----------------- | --------------------")
    for row in rows[:limit]:
        print("%s | %s | %d | %.2f | %s" % (row["name"], row["exposure"], row["characters"], row["tokens"], row["description"]))


def _render_unmanaged(rows, limit):
    print("\nUnbudgeted unmanaged provider skills")
    if not rows:
        print("(none discovered)")
        return
    print("provider | skill | characters | estimated tokens | effective description")
    print("-------- | ----- | ---------- | ----------------- | --------------------")
    for provider, name, characters, tokens, description in rows[:limit]:
        print("%s | %s | %d | %.2f | %s" % (provider, name, characters, tokens, description))


def _parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool", choices=("all",) + TOOLS, default="all")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv=None):
    args = _parser().parse_args(argv)
    if args.limit < 0:
        print("error: --limit must be non-negative", file=sys.stderr)
        return 2
    try:
        policy = load_policy(str(ROOT / "skill-policy.json"))
        overrides, settings_errors = _load_overrides(_settings_path())
    except (PolicyError, OSError, UnicodeError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1

    drift = _check_drift(policy, overrides, ROOT)
    drift.extend(settings_errors)
    selected = TOOLS if args.tool == "all" else (args.tool,)
    # Build every report even when output is narrowed to one provider.  A
    # policy check must enforce all managed surfaces, not only the table shown.
    reports = {}
    for tool in TOOLS:
        rows = _rows(policy, tool, overrides)
        total = sum(row["characters"] for row in rows)
        reports[tool] = (rows, total)

    if args.check:
        caps = policy["budgets"]
        failures = list(drift)
        # The two caps are surfaces, not separate budgets per provider: all
        # manual-aware tools must fit the manual-aware cap, while Codex and
        # OpenCode use the conservative all-shared cap.
        for tool, (_rows_for_tool, total) in reports.items():
            if tool in ("codex", "opencode"):
                cap = caps["alwaysListedDescriptionCharacters"]
                label = "always-listed %s" % tool
            else:
                cap = caps["manualAwareDescriptionCharacters"]
                label = "manual-aware %s" % tool
            if total > cap:
                largest = sorted(reports[tool][0], key=lambda row: (-row["characters"], row["name"]))[:5]
                contributors = ", ".join("%s=%d" % (row["name"], row["characters"]) for row in largest)
                failures.append("%s catalogue exceeds cap by %d characters (%d > %d); largest contributors: %s" % (label, total - cap, total, cap, contributors))
        if failures:
            for failure in sorted(set(failures)):
                print("error: %s" % failure, file=sys.stderr)
            return 1

    print("Skill description audit")
    for tool in selected:
        rows, total = reports[tool]
        if tool in ("codex", "opencode"):
            cap_name = "always-listed cap"
            cap = policy["budgets"]["alwaysListedDescriptionCharacters"]
        else:
            cap_name = "manual-aware cap"
            cap = policy["budgets"]["manualAwareDescriptionCharacters"]
        print("\n%s: %d characters (%.2f estimated tokens); %s %d" % (tool, total, total / 4, cap_name, cap))
        _render_rows(rows, args.limit)
    _render_unmanaged(_unmanaged(policy), args.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
