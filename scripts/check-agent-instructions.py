#!/usr/bin/env python3
"""Read-only validation for the managed repository instruction cohort."""

import argparse
from pathlib import Path

from instruction_manifest import first_active_line, load_scopes


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--cohort-root", type=Path, required=True)
    parser.add_argument("--max-lines", type=int, default=200)
    parser.add_argument(
        "--skip-deferred", action="store_true",
        help="report and skip manifest entries deferred because their working trees were dirty",
    )
    return parser.parse_args()


def normalized(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def validate_scope(scope: Path, display: Path, max_lines: int):
    problems = []
    agents = scope / "AGENTS.md"
    claude = scope / "CLAUDE.md"

    if agents.is_symlink():
        problems.append(f"{display}: unexpected symlink AGENTS.md")
    elif not agents.is_file():
        problems.append(f"{display}: missing AGENTS.md")
    else:
        agents_text = agents.read_text(encoding="utf-8")
        line_count = len(agents_text.splitlines())
        if not agents_text.strip():
            problems.append(f"{display}/AGENTS.md is empty")
        if line_count > max_lines:
            problems.append(f"{display}/AGENTS.md has {line_count} lines (maximum {max_lines})")

    if claude.is_symlink():
        problems.append(f"{display}: unexpected symlink CLAUDE.md")
        return problems
    if not claude.is_file():
        problems.append(f"{display}: missing CLAUDE.md")
        return problems

    claude_text = claude.read_text(encoding="utf-8")
    if first_active_line(claude_text) != "@AGENTS.md":
        problems.append(f"{display}/CLAUDE.md: first active line must be exactly @AGENTS.md")

    if agents.is_file() and not agents.is_symlink():
        agents_body = normalized(agents.read_text(encoding="utf-8"))
        claude_body = normalized(claude_text)
        after_import = claude_body.split("@AGENTS.md", 1)[-1].strip()
        if agents_body and agents_body in after_import:
            problems.append(f"{display}/CLAUDE.md duplicates AGENTS.md content")

    if first_active_line(claude_text) == "@AGENTS.md" and not agents.is_file():
        problems.append(f"{display}/CLAUDE.md has broken @AGENTS.md import")
    return problems


def main():
    args = parse_args()
    problems = []
    checked = 0
    deferred = 0
    for scope, display, defer_reason in load_scopes(args.manifest, args.cohort_root):
        if defer_reason and args.skip_deferred:
            print(f"SKIP {display}: {defer_reason}")
            deferred += 1
            continue
        checked += 1
        problems.extend(validate_scope(scope, display, args.max_lines))

    if problems:
        print("agent instruction check failed:")
        for problem in problems:
            print(f"  - {problem}")
        print(f"{len(problems)} problem(s) across {checked} managed scope(s)")
        return 1
    if deferred:
        print(f"agent instruction check: {checked} checked, {deferred} deferred")
    else:
        print(f"agent instruction check: {checked} managed scope(s) ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
