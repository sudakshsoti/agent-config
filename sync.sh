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
# The ccstatusline layout is pulled back the same way, for the same reason:
# its TUI rewrites ~/.config/ccstatusline/settings.json in place, so the live
# file is the one that drifts. No secrets in it, so it is copied verbatim.
#
# ccline's config.toml (the statusline actually in use as of 2026-07-27) is
# pulled back for the same reason: `ccline -c` rewrites it in place.
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE="$HOME/.claude"
CCSL="$HOME/.config/ccstatusline"
CCLINE_DIR="$HOME/.claude/ccline"

# Write via a temp file and mv into place only once jq has succeeded. Redirecting
# straight into the repo copy truncates it before jq runs, so a malformed live
# file or a full disk leaves settings.json at 0 bytes — and since this repo is
# now the only copy, there is nothing left to restore it from.
tmp="$(mktemp "$REPO/.settings.json.XXXXXX")"
trap 'rm -f "$tmp"' EXIT
jq 'del(.env)' "$CLAUDE/settings.json" > "$tmp"
chmod 644 "$tmp"   # mktemp gives 600; keep the tracked file world-readable
mv "$tmp" "$REPO/settings.json"
echo "synced  settings.json (env block stripped)"

if [ -f "$CCSL/settings.json" ]; then
  cp "$CCSL/settings.json" "$REPO/ccstatusline-settings.json"
  echo "synced  ccstatusline-settings.json"
else
  echo "skipped ccstatusline-settings.json ($CCSL/settings.json not found)"
fi

if [ -f "$CCLINE_DIR/config.toml" ]; then
  cp "$CCLINE_DIR/config.toml" "$REPO/ccline-config.toml"
  echo "synced  ccline-config.toml"
else
  echo "skipped ccline-config.toml ($CCLINE_DIR/config.toml not found)"
fi

echo "---"
git -C "$REPO" status --short -- settings.json ccstatusline-settings.json ccline-config.toml
echo "(commit with: git add -A && git commit)"
