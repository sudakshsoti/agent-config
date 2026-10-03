#!/usr/bin/env python3
"""check-manifest.py — catch drift in plugins.txt before install.sh does.

Three things fail here:
  - a malformed line (see scripts/manifest.py for the grammar);
  - a skill name listed twice on one `external` line's allowlist;
  - a skill name listed on two different `external` lines' allowlists.
    #90 collision precedence (AGENTS.md, Skills) would pick one silently,
    so two explicit claims on the same name is drift, not a valid config.

Two things are reported but never fail, because both are legitimate:
  - a bare `external <owner/repo>` source with no allowlist (imports every
    skill the source ships — deliberate for a small, curated repo);
  - an explicit skill name that also exists as a repo-owned `skills/<name>` —
    a repo-owned skill always shadows the external one at install time, so
    this is informational, not an error.

    ./scripts/check-manifest.py [repo-root]

FAILs exit 1. `info:` lines never affect the exit code.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manifest import parse_plugins_file  # noqa: E402


def check(repo_root):
    """Return (fails, infos) — lists of human-readable strings."""
    fails = []
    infos = []

    plugins_path = os.path.join(repo_root, "plugins.txt")
    entries, errors = parse_plugins_file(plugins_path)

    for error in errors:
        fails.append("plugins.txt:%d: %s" % (error.line_no, error.message))

    skills_dir = os.path.join(repo_root, "skills")
    try:
        repo_owned = {
            name
            for name in os.listdir(skills_dir)
            if os.path.isfile(os.path.join(skills_dir, name, "SKILL.md"))
        }
    except OSError:
        repo_owned = set()

    # name -> list of (line_no, source) that explicitly claim it.
    claims = {}

    for entry in entries:
        if not entry.skills:
            infos.append(
                "plugins.txt:%d: bare source %r has no allowlist — imports every skill it ships"
                % (entry.line_no, entry.source)
            )
            continue

        seen_on_line = set()
        for name in entry.skills:
            if name in seen_on_line:
                fails.append(
                    "plugins.txt:%d: duplicate external skill name: %s (listed twice on one line)"
                    % (entry.line_no, name)
                )
                continue
            seen_on_line.add(name)
            claims.setdefault(name, []).append((entry.line_no, entry.source))

            if name in repo_owned:
                infos.append(
                    "plugins.txt:%d: external skill name %r overlaps repo-owned skills/%s "
                    "(the repo-owned skill wins at install time)" % (entry.line_no, name, name)
                )

    for name, claimants in sorted(claims.items()):
        if len(claimants) > 1:
            where = ", ".join("line %d (%s)" % (line_no, source) for line_no, source in claimants)
            fails.append("duplicate external skill name: %s — claimed on %s" % (name, where))

    return fails, infos


def main(argv):
    if len(argv) > 2:
        sys.stderr.write("usage: check-manifest.py [repo-root]\n")
        return 2
    repo_root = argv[1] if len(argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print("plugins.txt manifest")
    fails, infos = check(repo_root)
    for detail in infos:
        print("  info: %s" % detail)
    for detail in fails:
        print("  FAIL  %s" % detail)
    if not fails:
        print("  ok    plugins.txt is well-formed with no duplicate external skill names")

    print()
    print("%d failed" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
