#!/usr/bin/env python3
"""Merge the repo-owned web-search preference keys into the live config.

The live `web-search.json` is read by the `pi-web-access` package and doubles as
its credential store, so it is merged rather than symlinked: provider API keys
written there by the extension or the curator UI must never follow a link back
into this repository. Only the keys the repo owns are pushed, and unrelated
machine-local keys survive untouched.

Credential-shaped keys are rejected, and the tracked file is exercised by the
fast pre-commit test, so an accidental credential fails validation before the
install merge or commit completes.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import tempfile

# Keys the tracked file must never contain. Deliberately broad: every real
# credential key in this config ends in "ApiKey"/"Key"/"Token", and no
# non-secret preference uses these words.
CREDENTIAL_KEY = re.compile(r"key|token|secret|password|credential", re.IGNORECASE)


def load_object(path: Path, *, required: bool) -> dict:
    """Read a JSON object, reporting problems instead of raising a traceback."""
    try:
        text = path.read_text()
    except FileNotFoundError:
        if required:
            raise SystemExit(f"error: missing web-search config: {path}")
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()

    source_data = load_object(args.source, required=True)
    reject_credentials(source_data)
    target_data = load_object(args.target, required=False)

    result = merged(target_data, source_data)
    if result == target_data:
        return  # already applied: leave the file and its mtime alone

    args.target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="web-search.json.", dir=args.target.parent)
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
