#!/usr/bin/env python3
"""check-claude-skill-overrides.py — hide claude.ai copies of linked skills.

Every skill in distribution.txt and distribution-vendor.txt is uploaded to
claude.ai, and Claude Code syncs it back as `anthropic-skills:<name>`. The same
skill is also linked into ~/.claude/skills by install.sh, so without this each
one shows twice in the / menu and twice in the model's skill list.

claude/settings.json therefore carries one `skillOverrides` entry per
distributed skill, `"anthropic-skills:<name>": "off"`. The key must be the
qualified name: a bare `<name>` key would also switch off the local copy.
Skills that exist only on claude.ai (docx, pdf, ...) are not listed and keep
syncing.

    ./scripts/check-claude-skill-overrides.py [repo-root] [--fix]

Without --fix, exits 1 when the anthropic-skills:* entries differ from the
distribution lists. --fix rewrites them; other skillOverrides keys are kept.
install.sh merges the file add-only, so an entry removed here stays in the
live ~/.claude/settings.json until deleted by hand.
"""

import json
import os
import sys

PREFIX = "anthropic-skills:"
MANIFESTS = ("distribution.txt", "distribution-vendor.txt")
SETTINGS = os.path.join("claude", "settings.json")


def distributed(root):
    names = []
    for manifest in MANIFESTS:
        with open(os.path.join(root, manifest), encoding="utf-8") as handle:
            for raw in handle:
                line = raw.split("#", 1)[0].strip()
                if line and line not in names:
                    names.append(line)
    return names


def expected_overrides(current, names):
    kept = {k: v for k, v in current.items() if not k.startswith(PREFIX)}
    kept.update({PREFIX + name: "off" for name in names})
    return dict(sorted(kept.items()))


def main(argv):
    fix = "--fix" in argv
    args = [a for a in argv if a != "--fix"]
    root = args[0] if args else os.path.join(os.path.dirname(__file__), "..")
    path = os.path.join(root, SETTINGS)
    with open(path, encoding="utf-8") as handle:
        settings = json.load(handle)

    current = settings.get("skillOverrides", {})
    want = expected_overrides(current, distributed(root))
    if current == want:
        print("check-claude-skill-overrides: ok (%d synced copies hidden)" % sum(k.startswith(PREFIX) for k in want))
        return 0

    if fix:
        settings["skillOverrides"] = want
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(settings, indent=2, sort_keys=True) + "\n")
        print("check-claude-skill-overrides: rewrote %s" % SETTINGS)
        return 0

    missing = sorted(set(want) - set(current))
    stale = sorted(set(current) - set(want))
    for key in missing:
        print("FAIL %s: skillOverrides lacks %r" % (SETTINGS, key))
    for key in stale:
        print("FAIL %s: skillOverrides has %r, not in %s" % (SETTINGS, key, " or ".join(MANIFESTS)))
    for key in sorted(set(want) & set(current)):
        if want[key] != current[key]:
            print("FAIL %s: skillOverrides[%r] is %r, want %r" % (SETTINGS, key, current[key], want[key]))
    print("fix: ./scripts/check-claude-skill-overrides.py --fix")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
