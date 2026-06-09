#!/usr/bin/env bash
#
# sync.sh — pull live settings from ~/.claude back into this repo
#
# Skills and agents are symlinked, so they never drift. The three copied
# files can: Claude Code edits ~/.claude/settings.json directly (via
# /config etc.). Run this before committing to refresh the repo copies.
#
# settings.json is sanitized on the way in: the "env" block (API keys)
# is stripped so secrets never enter git. Keep keys in
# ~/.claude/settings.local.json or accept that they stay local-only.
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE="$HOME/.claude"

jq 'del(.env)' "$CLAUDE/settings.json" > "$REPO/settings.json"
echo "synced  settings.json (env block stripped)"

for f in statusline.sh claude-powerline.json; do
  if [ -e "$CLAUDE/$f" ]; then
    cp "$CLAUDE/$f" "$REPO/$f"
    echo "synced  $f"
  fi
done

echo "---"
git -C "$REPO" status --short -- settings.json statusline.sh claude-powerline.json
echo "(commit with: git add -A && git commit)"
