#!/usr/bin/env python3
"""Create standard CLAUDE.md wrappers; dry-run unless --apply is given.

This command never creates or edits AGENTS.md. A malformed CLAUDE.md is
replaced with the single canonical import, so inspect the dry-run before apply.
"""

import argparse
import os
from pathlib import Path
import tempfile

from instruction_manifest import first_active_line, load_scopes


WRAPPER = "@AGENTS.md\n"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--cohort-root", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="write wrappers; default is dry-run")
    return parser.parse_args()


def replace_file(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".CLAUDE.md.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(WRAPPER)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    args = parse_args()
    refused = 0
    changes = 0
    for scope, display, _defer_reason in load_scopes(args.manifest, args.cohort_root):
        agents = scope / "AGENTS.md"
        claude = scope / "CLAUDE.md"
        if not agents.is_file() or agents.is_symlink() or not agents.read_text(encoding="utf-8").strip():
            print(f"{display}: refusing: missing AGENTS.md canonical content")
            refused += 1
            continue
        valid = claude.is_file() and not claude.is_symlink()
        if valid:
            valid = first_active_line(claude.read_text(encoding="utf-8")) == "@AGENTS.md"
        if valid:
            continue
        action = "replace" if claude.exists() or claude.is_symlink() else "create"
        if args.apply:
            replace_file(claude)
            print(f"{display}: {action}d CLAUDE.md")
        else:
            print(f"{display}: would {action} CLAUDE.md")
        changes += 1

    mode = "applied" if args.apply else "dry-run"
    print(f"repair: {mode}, {changes} wrapper change(s), {refused} refusal(s)")
    return 1 if refused else 0


if __name__ == "__main__":
    raise SystemExit(main())
