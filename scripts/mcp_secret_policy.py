#!/usr/bin/env python3
"""One policy for when an MCP server entry may carry a secret.

Shared by snapshot-machine-config.sh (scans whole files) and
seed-mcp-servers.py (checks each declared server). Each side keeps its own
extra checks; only the common rule lives here:

  a server whose `env` or `headers` holds a non-empty string is refused, because
  that is how OMP and Claude Code store inline API keys and Authorization
  headers.

CLI (used by snapshot-machine-config.sh):

    mcp_secret_policy.py FILE   print credential-shaped paths, one per line;
                                exit 0 when FILE should never be committed,
                                1 when it looks clean.
"""

import json
import re
import sys

SECRET_KEY = re.compile(
    r"^(authorization|api[_-]?key|apikey|token|access[_-]?token|"
    r"secret|password|passwd|bearer)$",
    re.I,
)
CARRIER_KEY = re.compile(r"^(env|headers)$", re.I)
TEXT_SECRET = re.compile(
    r"(api[_-]?key|secret|token|password)\s*[=:]\s*[\"']?[A-Za-z0-9_\-]{16,}",
    re.I,
)


def has_nonempty_string(node):
    if isinstance(node, str):
        return node.strip() != ""
    if isinstance(node, dict):
        return any(has_nonempty_string(v) for v in node.values())
    if isinstance(node, list):
        return any(has_nonempty_string(v) for v in node)
    return False


def carrier_keys(server):
    """Keys of `server` that are env/headers carriers holding a non-empty string."""
    if not isinstance(server, dict):
        return []
    return [k for k, v in server.items() if CARRIER_KEY.match(k) and has_nonempty_string(v)]


def refuse_reason(server):
    """Why this MCP server entry must not be recorded, or None when it may be."""
    keys = carrier_keys(server)
    if keys:
        return f"non-empty {keys[0]} (inline credentials never ride in a snapshot)"
    return None


def scan_json(data):
    """Paths of credential-shaped fields anywhere in parsed JSON."""
    hits = []

    def walk(node, path, in_mcp):
        if isinstance(node, dict):
            if in_mcp:
                hits.extend(f"{path}.{k}" if path else k for k in carrier_keys(node))
            for k, v in node.items():
                here = f"{path}.{k}" if path else k
                if SECRET_KEY.match(k) and has_nonempty_string(v):
                    hits.append(here)
                walk(v, here, in_mcp or k == "mcpServers")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]", in_mcp)

    walk(data, "", False)
    return hits


def scan(raw):
    """Hit descriptions for file text; JSON is scanned structurally, other text by pattern."""
    try:
        data = json.loads(raw)
    except ValueError:
        return ["text: assigned-looking secret"] if TEXT_SECRET.search(raw) else []
    return scan_json(data)


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    with open(argv[1]) as handle:
        hits = scan(handle.read())
    for hit in hits:
        print(hit)
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
