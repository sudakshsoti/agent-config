#!/usr/bin/env bash
#
# sync.sh — pull live settings from ~/.claude back into this repo
#
# Skills and agents are symlinked, so they never drift. settings.json is
# copied instead: Claude Code edits ~/.claude/settings.json directly (via
# /config etc.). Run this before committing to refresh the repo copy.
#
# settings.json is sanitized on the way in: the "env" block (API keys)
# is stripped so secrets never enter git. Keep keys in
# ~/.claude/settings.local.json or accept that they stay local-only.
#
# It also strips hook commands belonging to other tools (supacode, superset).
# Those show up in ~/.claude/settings.json because it's a blind copy of
# whatever's installed on this machine, but they're machine state, not
# configuration -- a fresh machine restoring from this repo would otherwise
# install hooks for tools it doesn't have. Matchers left empty by the strip,
# and events left with no matchers, are dropped too.
#
# claude-powerline.json is symlinked, so live edits already write through
# into the repo, so no pull-back is needed.
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE="$HOME/.claude"

# Write via a temp file and mv into place only once jq has succeeded. Redirecting
# straight into the repo copy truncates it before jq runs, so a malformed live
# file or a full disk leaves settings.json at 0 bytes — and since this repo is
# now the only copy, there is nothing left to restore it from.
tmp="$(mktemp "$REPO/.settings.json.XXXXXX")"
trap 'rm -f "$tmp"' EXIT
jq '
  del(.env)
  | if .hooks then
      (.hooks |= with_entries(
         (.value |= map(.hooks |= map(select(
            .command | test("supacode-managed-hook|SUPERSET_HOME_DIR") | not))))
         | .value |= map(select((.hooks | length) > 0))
       ))
      | (.hooks |= with_entries(select((.value | length) > 0)))
    else . end
' "$CLAUDE/settings.json" > "$tmp"
chmod 644 "$tmp"   # mktemp gives 600; keep the tracked file world-readable
mv "$tmp" "$REPO/settings.json"
echo "synced  settings.json (env block + third-party managed hooks stripped)"

echo "---"
git -C "$REPO" status --short -- settings.json claude-powerline.json
echo "(commit with: git add -A && git commit)"
