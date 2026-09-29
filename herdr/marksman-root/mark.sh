#!/bin/sh
# Marksman accepts a workspace root only if it holds .marksman.toml or a .git
# *directory*. A linked worktree's .git is a file, so Marksman logs "Workspace
# folder is bogus" and serves nothing. Drop the marker file, and keep it out of
# git via the shared info/exclude (one file for every worktree of the repo).
dir=$(printf '%s' "$HERDR_PLUGIN_EVENT_JSON" | jq -r '[.. | objects | .checkout_path? // empty][0] // empty')
[ -n "$dir" ] && [ -f "$dir/.git" ] || exit 0
touch "$dir/.marksman.toml"
exclude=$(git -C "$dir" rev-parse --path-format=absolute --git-path info/exclude) || exit 0
mkdir -p "$(dirname "$exclude")"
grep -qxF '/.marksman.toml' "$exclude" 2>/dev/null || printf '%s\n' '/.marksman.toml' >>"$exclude"
