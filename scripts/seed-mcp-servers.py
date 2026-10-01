#!/usr/bin/env python3
"""Add MCP servers a snapshot declares but the live config lacks. Never edits one.

`snapshots/{omp,claude}/mcp.json` are point-in-time copies of live MCP config
(see scripts/snapshot-machine-config.sh). This is the other direction, for a
fresh machine: install the servers the snapshot names, and leave every server
that already exists exactly as the owning tool wrote it (OAuth state, credential
ids, tool-side edits all survive).

  seed-mcp-servers.py merge   SOURCE TARGET   add missing servers to TARGET
                                               (a JSON file with `mcpServers`;
                                               created when absent)
  seed-mcp-servers.py missing SOURCE EXISTING  print `name<TAB>json` for each
                                               server absent from EXISTING, for
                                               `claude mcp add-json`

A snapshot server carrying a non-empty `env` or `headers` is refused: those are
the carriers of inline API keys, and the snapshot script already refuses to
record them, so one showing up here means the file was edited by hand.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile

from mcp_secret_policy import refuse_reason


def load(path: Path, *, required: bool) -> dict:
    try:
        text = path.read_text()
    except FileNotFoundError:
        if required:
            raise SystemExit(f"error: missing {path}")
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


def servers_of(data: dict, path: Path) -> dict:
    servers = data.get("mcpServers", {})
    if not isinstance(servers, dict):
        raise SystemExit(f"error: mcpServers in {path} is not an object")
    return servers


def declared(source_path: Path) -> dict:
    servers = servers_of(load(source_path, required=True), source_path)
    for name, config in servers.items():
        if not isinstance(config, dict):
            raise SystemExit(f"error: server {name!r} in {source_path} is not an object")
        reason = refuse_reason(config)
        if reason is None:
            # Seed is stricter than the shared policy: any non-empty carrier.
            reason = next(
                (f"non-empty {c}" for c in ("env", "headers") if config.get(c)), None
            )
        if reason:
            raise SystemExit(f"error: refusing server {name!r}: {reason}")
    return servers


def write_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f"{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(json.dumps(data, indent=2) + "\n")
        if path.exists():
            os.chmod(temporary, path.stat().st_mode & 0o777)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def main(argv: list[str]) -> int:
    if len(argv) != 4 or argv[1] not in ("merge", "missing"):
        print(__doc__, file=sys.stderr)
        return 2
    mode, source, target = argv[1], Path(argv[2]), Path(argv[3])
    wanted = declared(source)
    live = load(target, required=False)
    existing = servers_of(live, target)
    absent = {name: config for name, config in wanted.items() if name not in existing}

    if mode == "missing":
        for name, config in absent.items():
            print(f"{name}\t{json.dumps(config, separators=(',', ':'))}")
        return 0

    if not absent:
        return 0
    live["mcpServers"] = {**existing, **absent}
    write_atomic(target, live)
    for name in absent:
        print(f"seeded  mcp server {name} -> {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
