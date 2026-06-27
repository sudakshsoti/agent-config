#!/usr/bin/env bash
#
# install.sh — wire this repo into ~/.claude
#
# Symlinks (repo is the live source of truth; edits apply instantly):
#   skills/<name>/  -> ~/.claude/skills/<name>
#   agents/<name>.md -> ~/.claude/agents/<name>.md
#
# Copies (Claude Code rewrites these itself, so symlinks would break;
# copied only if missing — never clobbers an existing file):
#   settings.json, statusline.sh, claude-powerline.json -> ~/.claude/
#
# Idempotent; safe to re-run. Run once after cloning on a new machine.
#
#   ./install.sh          # link skills + agents, copy settings if absent
#   ./install.sh --prune  # also remove dangling symlinks that point here
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE="$HOME/.claude"
CODEX="$HOME/.codex"
PRUNE=0
[ "${1:-}" = "--prune" ] && PRUNE=1

mkdir -p "$CLAUDE/skills" "$CLAUDE/agents"
# Mirror skills into Codex too, but only if Codex is actually installed
# (its skills dir already exists) — never create ~/.codex on a Claude-only box.
CODEX_SKILLS=""
[ -d "$CODEX/skills" ] && CODEX_SKILLS="$CODEX/skills"
linked=0 skipped=0 copied=0 pruned=0

link_into() { # link_into <source> <dest-link>
  local src="$1" link="$2" name
  name="$(basename "$link")"
  if [ -L "$link" ]; then
    rm -f "$link" # replace any existing symlink
  elif [ -e "$link" ]; then
    echo "⚠️  SKIP $name — a real (non-symlink) entry exists at $link."
    echo "    Move it into the repo first, then re-run."
    skipped=$((skipped + 1))
    return
  fi
  ln -s "$src" "$link"
  echo "linked  $name"
  linked=$((linked + 1))
}

# 1. Skills: every directory holding a SKILL.md.
#    Linked into ~/.claude (all repos) and mirrored into ~/.codex (Codex)
#    when Codex is installed — same SKILL.md format works on both surfaces.
for dir in "$REPO"/skills/*/; do
  [ -f "$dir/SKILL.md" ] || continue
  link_into "${dir%/}" "$CLAUDE/skills/$(basename "$dir")"
  [ -n "$CODEX_SKILLS" ] && link_into "${dir%/}" "$CODEX_SKILLS/$(basename "$dir")"
done

# 2. Agents: every markdown file in agents/
for file in "$REPO"/agents/*.md; do
  [ -f "$file" ] || continue
  link_into "$file" "$CLAUDE/agents/$(basename "$file")"
done

# 3. Settings files: copy only if missing (new-machine bootstrap).
#    settings.json in the repo has no secrets — add machine-local env/keys
#    to ~/.claude/settings.local.json, which is never tracked here.
for f in settings.json statusline.sh claude-powerline.json; do
  if [ ! -e "$CLAUDE/$f" ]; then
    cp "$REPO/$f" "$CLAUDE/$f"
    echo "copied  $f"
    copied=$((copied + 1))
  fi
done

# 4. Optionally remove dangling symlinks that point into this repo.
if [ "$PRUNE" = "1" ]; then
  for link in "$CLAUDE"/skills/* "$CLAUDE"/agents/* ${CODEX_SKILLS:+"$CODEX_SKILLS"/*}; do
    [ -L "$link" ] || continue
    case "$(readlink "$link")" in
      "$REPO"/*)
        if [ ! -e "$link" ]; then
          rm -f "$link"
          echo "pruned  $(basename "$link") (dangling)"
          pruned=$((pruned + 1))
        fi ;;
    esac
  done
fi

echo "---"
echo "linked=$linked skipped=$skipped copied=$copied pruned=$pruned"
