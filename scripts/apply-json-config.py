#!/usr/bin/env python3
"""Merge a tracked, secret-free JSON config into a live machine-local one.

Used for files a tool both reads and writes, so a symlink into this repository
would let tool-written credentials or state follow the link into a git tree:

  - pi's `web-search.json`, which doubles as pi-web-access's credential store;
  - Claude Code's `~/.claude/settings.json`, which carries the herdr-managed
    hooks and an API key in `env`.

Only the keys the repo owns are pushed (source wins, objects merge recursively)
and unrelated machine-local keys survive untouched.

Credential-shaped keys are rejected in the tracked file, and the tracked files
are exercised by the fast pre-commit test, so an accidental credential fails
validation before the install merge or commit completes.

A secret that must live in the live file is supplied at merge time with
`--env-from DOTENV:NAME[=TARGET]`: NAME is read from the (untracked,
1Password-injected) dotenv file and written to the target's `env` object as
TARGET (default NAME). A missing file or name is a warning, not an error, so a
machine without the dotenv yet still installs.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile

# Keys the tracked file must never contain. Deliberately broad: every real
# credential key in these configs ends in "ApiKey"/"Key"/"Token", and no
# non-secret preference uses these words.
CREDENTIAL_KEY = re.compile(r"key|token|secret|password|credential", re.IGNORECASE)


def load_object(path: Path, *, required: bool) -> dict:
    """Read a JSON object, reporting problems instead of raising a traceback."""
    try:
        text = path.read_text()
    except FileNotFoundError:
        if required:
            raise SystemExit(f"error: missing source config: {path}")
        return {}
    except OSError as error:
        raise SystemExit(f"error: cannot read {path}: {error}")

    if not text.strip():
        return {}
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise SystemExit(f"error: invalid JSON in {path}: {error}")
    if not isinstance(data, dict):
        raise SystemExit(f"error: expected a JSON object in {path}")
    return data


def reject_credentials(data: dict, prefix: str = "") -> None:
    for key, value in data.items():
        if CREDENTIAL_KEY.search(key):
            raise SystemExit(
                f"error: refusing to push credential-shaped key {prefix}{key} "
                "into the live config (credentials belong in dotfiles, not here)"
            )
        if isinstance(value, dict):
            reject_credentials(value, f"{prefix}{key}.")


def merged(target: dict, source: dict) -> dict:
    """Recursively merge ``source`` over ``target``; source values win."""
    result = dict(target)
    for key, value in source.items():
        existing = result.get(key)
        if isinstance(value, dict) and isinstance(existing, dict):
            result[key] = merged(existing, value)
        else:
            result[key] = value
    return result


def read_dotenv_value(path: Path, name: str) -> str | None:
    """Return NAME's value from a KEY=value dotenv file, or None if absent."""
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return None
    value = None
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, rest = line.partition("=")
        if separator and key.strip() == name:
            value = rest.strip().strip("'\"")  # last assignment wins
    return value or None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument(
        "--env-from",
        action="append",
        default=[],
        metavar="DOTENV:NAME[=TARGET]",
        help="copy NAME from DOTENV into the target's env object as TARGET (default NAME; repeatable)",
    )
    args = parser.parse_args()

    source_data = load_object(args.source, required=True)
    reject_credentials(source_data)
    target_data = load_object(args.target, required=False)

    result = merged(target_data, source_data)

    for spec in args.env_from:
        dotenv, separator, names = spec.rpartition(":")
        name, _, target_name = names.partition("=")
        target_name = target_name or name
        if not separator or not dotenv or not name:
            raise SystemExit(f"error: --env-from expects DOTENV:NAME[=TARGET], got {spec!r}")
        value = read_dotenv_value(Path(dotenv).expanduser(), name)
        if value is None:
            print(
                f"warning: {name} not found in {dotenv}; leaving env.{target_name} as is",
                file=sys.stderr,
            )
            continue
        env = result.get("env")
        result["env"] = {**(env if isinstance(env, dict) else {}), target_name: value}

    if result == target_data:
        return  # already applied: leave the file and its mtime alone

    args.target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f"{args.target.name}.", dir=args.target.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
        # Keep an existing mode; mkstemp's 0600 is the safe default otherwise.
        if args.target.exists():
            os.chmod(temporary, args.target.stat().st_mode & 0o777)
        os.replace(temporary, args.target)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


if __name__ == "__main__":
    main()
