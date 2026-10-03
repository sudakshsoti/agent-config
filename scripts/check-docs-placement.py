#!/usr/bin/env python3
"""check-docs-placement.py — plans live in plans/ with a status line.

Looks only at files tracked by git: OMP autosaves approved plans into plans/
(`plan.autosaveDir`), and an untracked autosave must not fail the check.

  - Every tracked .md under plans/ must start with exactly `Status: planned`
    or `Status: active`. A finished plan is deleted, so `done` fails too.
  - A tracked .md under docs/ outside docs/research/ and docs/agents/ fails:
    plans and runbooks belong in plans/.

    ./scripts/check-docs-placement.py [repo-root]

FAILs exit 1.
"""

import os
import subprocess
import sys

STATUSES = ("Status: planned", "Status: active")
DOCS_ALLOWED = ("docs/research/", "docs/agents/")


def tracked_files(repo_root):
    result = subprocess.run(
        ["git", "-C", repo_root, "ls-files", "-z", "--", "plans", "docs"],
        capture_output=True,
        check=True,
    )
    return [p for p in result.stdout.decode("utf-8").split("\0") if p]


def first_line(path):
    with open(path, encoding="utf-8") as handle:
        return handle.readline().rstrip("\r\n")


def check(repo_root):
    fails = []
    for rel in tracked_files(repo_root):
        if not rel.endswith(".md"):
            continue
        path = os.path.join(repo_root, rel)
        if not os.path.isfile(path):
            continue  # tracked but deleted in the working tree
        if rel.startswith("plans/"):
            line = first_line(path)
            if line not in STATUSES:
                fails.append(
                    "%s: first line must be exactly `Status: planned` or "
                    "`Status: active` (got %r); a finished plan is deleted, "
                    "not marked done" % (rel, line)
                )
        elif rel.startswith("docs/") and not rel.startswith(DOCS_ALLOWED):
            fails.append(
                "%s: plans and runbooks belong in plans/ with a `Status: "
                "planned` or `Status: active` first line; docs/ keeps only "
                "docs/research/ and docs/agents/" % rel
            )
    return fails


def main(argv):
    if len(argv) > 2:
        sys.stderr.write("usage: check-docs-placement.py [repo-root]\n")
        return 2
    repo_root = argv[1] if len(argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print("docs placement")
    fails = check(repo_root)
    for detail in fails:
        print("  FAIL  %s" % detail)
    if not fails:
        print("  ok    tracked plans have a status line and docs/ holds no plans")

    print()
    print("%d failed" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
