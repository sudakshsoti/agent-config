#!/usr/bin/env bash
# snapshot-machine-config.sh — copy machine-local harness config into
# snapshots/ so it is version-controlled without being symlinked.
#
# Why a snapshot and not a symlink. Everything else in this repo is linked, so
# the repo is the live file and there is no sync step. Two surfaces cannot work
# that way:
#
#   ~/.omp/agent/mcp.json  — README's "Secrets policy" calls this a live leak
#     path: OMP writes the file itself, so an `omp mcp add` for a server with an
#     inline `env` API key would land a real credential in a git working tree.
#     A copy breaks that path — nothing OMP writes reaches the tree on its own.
#   ~/.claude.json         — Claude Code keeps its user-scope `mcpServers`
#     inside a ~70KB state blob that also holds userID, machineID and
#     oauthAccount. Only the `mcpServers` object is extracted here.
#
# The cost is drift: a snapshot is a point-in-time copy, so run this after
# changing one of these by hand or through a TUI.
#
#   ./scripts/snapshot-machine-config.sh           # refresh snapshots/ from live
#   ./scripts/snapshot-machine-config.sh --check    # report drift, exit 1 if any
#
# Not named test-* on purpose: it reads $HOME, so check.sh must not discover it.
#
# Every snapshot passes a credential scan first. A file that looks like it
# carries a secret is refused, loudly, and the old snapshot is left in place —
# the whole point of copying instead of linking is that a credential never
# reaches the tree, so failing closed is the only correct behavior.
set -uo pipefail

repo_root="$(cd "${BASH_SOURCE[0]%/*}/.." && pwd)"
snapshots="$repo_root/snapshots"

check_only=false
[ "${1:-}" = "--check" ] && check_only=true

drift=0
written=0
refused=0

# looks_like_secret <file> — 0 when the content should never be committed.
#
# Two rules, both keyed on the *value* rather than the key alone, because a key
# name on its own is a weak signal: claude-powerline.json has a display segment
# named `env` and a color named `env`, and neither is a credential.
#
#   1. `env` / `headers` holding a non-empty string, anywhere under an
#      `mcpServers` object. That is exactly how OMP stores an inline API key or
#      an Authorization header — the leak path README.md describes.
#   2. A token/key/secret/password/authorization field whose value is a
#      non-empty string, anywhere.
#
# `credentialId` is deliberately allowed: it is an opaque pointer into OMP's
# local credential store, not the credential itself.
looks_like_secret() {
  python3 - "$1" <<'GUARD'
import json, re, sys

raw = open(sys.argv[1]).read()
SECRET_KEY = re.compile(
    r"^(authorization|api[_-]?key|apikey|token|access[_-]?token|"
    r"secret|password|passwd|bearer)$",
    re.I,
)
CARRIER_KEY = re.compile(r"^(env|headers)$", re.I)

try:
    data = json.loads(raw)
except ValueError:
    # Not JSON (a shell script): scan the text for an assigned-looking secret.
    sys.exit(
        0
        if re.search(
            r"(api[_-]?key|secret|token|password)\s*[=:]\s*[\"']?[A-Za-z0-9_\-]{16,}",
            raw,
            re.I,
        )
        else 1
    )

hits = []


def has_nonempty_string(node):
    if isinstance(node, str):
        return node.strip() != ""
    if isinstance(node, dict):
        return any(has_nonempty_string(v) for v in node.values())
    if isinstance(node, list):
        return any(has_nonempty_string(v) for v in node)
    return False


def walk(node, path, in_mcp):
    if isinstance(node, dict):
        for k, v in node.items():
            here = f"{path}.{k}" if path else k
            if SECRET_KEY.match(k) and has_nonempty_string(v):
                hits.append(here)
            elif in_mcp and CARRIER_KEY.match(k) and has_nonempty_string(v):
                hits.append(here)
            walk(v, here, in_mcp or k == "mcpServers")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f"{path}[{i}]", in_mcp)


walk(data, "", False)
for h in hits:
    print(h)
sys.exit(0 if hits else 1)
GUARD
}

# capture <label> <dest-relative> <producer...> — producer writes live content
# to stdout; the result is scanned, then compared or committed.
capture() {
  local label="$1" dest="$snapshots/$2"
  shift 2
  local tmp
  tmp="$(mktemp)"
  if ! "$@" >"$tmp" 2>/dev/null; then
    echo "skip    $label (source unavailable)"
    rm -f "$tmp"
    return 0
  fi
  if [ ! -s "$tmp" ]; then
    echo "skip    $label (source empty)"
    rm -f "$tmp"
    return 0
  fi

  local found
  if found="$(looks_like_secret "$tmp")"; then
    echo "REFUSED $label — credential-shaped field(s): ${found//$'\n'/, }"
    echo "        snapshot left unchanged; see README.md \"Secrets policy\""
    refused=$((refused + 1))
    rm -f "$tmp"
    return 0
  fi

  if [ -f "$dest" ] && cmp -s "$tmp" "$dest"; then
    rm -f "$tmp"
    return 0
  fi

  drift=$((drift + 1))
  if [ "$check_only" = true ]; then
    echo "drift   $label"
  else
    mkdir -p "${dest%/*}"
    cat "$tmp" >"$dest"
    [ -x "$dest" ] || case "$dest" in *.sh) chmod +x "$dest" ;; esac
    echo "updated $label"
    written=$((written + 1))
  fi
  rm -f "$tmp"
}

# Claude Code: the statusline wrapper, its companion for subagents, and the
# claude-powerline theme the wrapper renders through. settings.json is not
# copied — it carries unrelated keys; snapshots/README.md documents the two
# keys that wire these scripts up.
capture "claude/statusline.sh" claude/statusline.sh \
  cat "$HOME/.claude/statusline.sh"
capture "claude/subagent-statusline.sh" claude/subagent-statusline.sh \
  cat "$HOME/.claude/subagent-statusline.sh"
capture "claude/claude-powerline.json" claude/claude-powerline.json \
  cat "$HOME/.claude/claude-powerline.json"

# Claude Code MCP: user scope only, extracted from the state blob.
claude_mcp() {
  python3 - "$HOME/.claude.json" <<'PY'
import json, sys
servers = json.load(open(sys.argv[1])).get("mcpServers", {})
json.dump({"mcpServers": servers}, sys.stdout, indent=2, sort_keys=True)
sys.stdout.write("\n")
PY
}
capture "claude/mcp.json" claude/mcp.json claude_mcp

# OMP MCP: copied whole, minus the lock file OMP keeps beside it.
capture "omp/mcp.json" omp/mcp.json cat "$HOME/.omp/agent/mcp.json"

echo "---"
if [ "$check_only" = true ]; then
  echo "drift=$drift refused=$refused"
  [ "$refused" -eq 0 ] && [ "$drift" -eq 0 ]
else
  echo "updated=$written refused=$refused"
  [ "$refused" -eq 0 ]
fi
