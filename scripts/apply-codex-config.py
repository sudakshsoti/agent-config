#!/usr/bin/env python3
"""Merge the repo-owned Codex config keys without touching machine state."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import tempfile
import tomllib


def merge_section(target: str, section: str, values: dict[str, object], source: str) -> str:
    header = f"[{section}]"
    source_lines = source.splitlines()
    assignments = {
        key: next(
            line for line in source_lines if re.match(rf"^{re.escape(key)}\s*=", line)
        )
        for key in values
    }

    section_match = re.search(
        rf"(?ms)^\[{re.escape(section)}\]\s*$.*?(?=^\[|\Z)", target
    )
    if not section_match:
        block = header + "\n" + "\n".join(assignments.values()) + "\n"
        return target.rstrip() + "\n\n" + block

    block = section_match.group(0).rstrip()
    for key, assignment in assignments.items():
        pattern = rf"(?m)^{re.escape(key)}\s*=.*$"
        if re.search(pattern, block):
            block = re.sub(pattern, assignment, block, count=1)
        else:
            block += "\n" + assignment
    block += "\n\n"
    return target[: section_match.start()] + block + target[section_match.end() :].lstrip("\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()

    source_text = args.source.read_text()
    source_data = tomllib.loads(source_text)
    target_text = args.target.read_text() if args.target.exists() else ""
    if target_text:
        tomllib.loads(target_text)

    merged = target_text
    for section, values in source_data.items():
        if not isinstance(values, dict):
            raise ValueError(f"managed top-level key must be a table: {section}")
        merged = merge_section(merged, section, values, source_text)
    tomllib.loads(merged)

    args.target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="config.toml.", dir=args.target.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(merged)
        os.replace(temporary, args.target)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


if __name__ == "__main__":
    main()
