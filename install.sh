#!/usr/bin/env bash
#
# install.sh — wire this repo into ~/.claude (and mirror skills into ~/.codex)
#
# Symlinks (repo is the live source of truth; edits apply instantly):
#   skills/<name>/  -> ~/.claude/skills/<name>
#   agents/<name>.md -> ~/.claude/agents/<name>.md
#   commands/<name>.md -> ~/.claude/commands/<name>.md
#   global-CLAUDE.md -> ~/.claude/CLAUDE.md
#
# Copies, refreshed every run (NOT symlinks):
#   skills/<name>/ -> ~/.codex/skills/<name>
#     Codex's skill scanner ignores symlinked directories, so the mirror must
#     be a real copy. Trade-off: editing a SKILL.md does NOT reach Codex live —
#     re-run ./install.sh to push edits. (Claude stays live via the symlink.)
#     Each copy gets a .agent-config-managed marker so --prune can clean up
#     copies of deleted skills without touching ~/.codex/skills/.system or
#     other hand-installed Codex skills.
#
# Copies, only if missing (Claude Code rewrites these itself, so a symlink
# would break; never clobbers an existing file):
#   settings.json, statusline.sh, claude-powerline.json -> ~/.claude/
#
# Plugins (declared in plugins.txt, applied via the `claude` CLI — NOT vendored):
#   marketplace/plugin lines -> `claude plugin marketplace add` / `install`
#   Idempotent no-ops if already present. Skipped if `claude` isn't on PATH,
#   or with --no-plugins.
#
# Idempotent; safe to re-run. Run once after cloning on a new machine.
#
#   ./install.sh              # link skills+agents, copy skills into Codex, copy settings if absent, sync plugins
#   ./install.sh --prune      # also remove dangling Claude symlinks + orphaned Codex copies
#   ./install.sh --no-plugins # skip the `claude plugin` sync step
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE="$HOME/.claude"
CODEX="$HOME/.codex"
PRUNE=0
FORCE=0
PLUGINS=1
for arg in "$@"; do
  case "$arg" in
    --prune) PRUNE=1 ;;
    --force) FORCE=1 ;;
    --no-plugins) PLUGINS=0 ;;
    *) echo "unknown option: $arg (expected --prune, --force and/or --no-plugins)"; exit 2 ;;
  esac
done

# Guard: the symlinks bake in this checkout's absolute path. Running from an
# ephemeral worktree (Supacode, or a temp git worktree) pins every ~/.claude
# skill+agent link to a path that vanishes when the worktree is cleaned up —
# silently breaking the whole personal skill set. Refuse unless --force.
case "$REPO" in
  */.supacode/repos/* | */.git/worktrees/* | */worktrees/*)
    if [ "$FORCE" != "1" ]; then
      echo "⛔ Refusing to install from what looks like an ephemeral worktree:"
      echo "     $REPO"
      echo "   Symlinks bake in this absolute path; when the worktree is removed,"
      echo "   every ~/.claude skill+agent link dangles. Run from your canonical"
      echo "   checkout (e.g. ~/dev/agent-config) instead, or pass --force if you"
      echo "   really mean to point the global install here."
      exit 1
    fi
    echo "⚠️  --force: installing from an ephemeral-looking path ($REPO)."
    ;;
esac

mkdir -p "$CLAUDE/skills" "$CLAUDE/agents" "$CLAUDE/commands"
# Mirror skills into Codex too, but only if Codex is actually installed
# (its skills dir already exists) — never create ~/.codex on a Claude-only box.
CODEX_SKILLS=""
[ -d "$CODEX/skills" ] && CODEX_SKILLS="$CODEX/skills"
MARKER=".agent-config-managed"
linked=0 skipped=0 copied=0 mirrored=0 pruned=0 plugins=0

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

copy_into() { # copy_into <source-dir> <dest-dir> — refreshed every run
  local src="$1" dest="$2" name
  name="$(basename "$dest")"
  # A symlink here is from an older install — drop it and replace with a copy.
  # A real dir without our marker is hand-installed; never clobber it.
  if [ ! -L "$dest" ] && [ -e "$dest" ] && [ ! -f "$dest/$MARKER" ]; then
    echo "⚠️  SKIP $name (codex) — an unmanaged entry exists at $dest."
    echo "    Move it aside first, then re-run."
    skipped=$((skipped + 1))
    return
  fi
  rm -rf "$dest"
  cp -R "$src" "$dest"
  : > "$dest/$MARKER"
  echo "copied  $name (codex)"
  mirrored=$((mirrored + 1))
}

# 1. Skills: every directory holding a SKILL.md.
#    Symlinked into ~/.claude (live source of truth) and COPIED into ~/.codex
#    (Codex ignores symlinked skill dirs) when Codex is installed — same
#    SKILL.md format works on both surfaces.
for dir in "$REPO"/skills/*/; do
  [ -f "$dir/SKILL.md" ] || continue
  link_into "${dir%/}" "$CLAUDE/skills/$(basename "$dir")"
  [ -n "$CODEX_SKILLS" ] && copy_into "${dir%/}" "$CODEX_SKILLS/$(basename "$dir")"
done

# 2. Agents: every markdown file in agents/
for file in "$REPO"/agents/*.md; do
  [ -f "$file" ] || continue
  link_into "$file" "$CLAUDE/agents/$(basename "$file")"
done

# 2b. Commands: every markdown file in commands/ becomes a global slash command.
for file in "$REPO"/commands/*.md; do
  [ -f "$file" ] || continue
  link_into "$file" "$CLAUDE/commands/$(basename "$file")"
done

# 3. Global CLAUDE.md: symlinked, like skills and agents — the repo stays the
#    live source of truth, so edits apply instantly and land in git history.
#    Unlike settings.json (which Claude Code rewrites via /config), this file is
#    only ever appended to by the `#` quick-capture shortcut, and an append
#    writes through a symlink to the target. If some future Claude Code version
#    rewrites it atomically instead, the symlink becomes a real file and
#    link_into's guard below reports it loudly on the next run — at which point
#    move the live file back into the repo.
link_into "$REPO/global-CLAUDE.md" "$CLAUDE/CLAUDE.md"

# 4. Settings files: copy only if missing (new-machine bootstrap).
#    settings.json in the repo has no secrets — add machine-local env/keys
#    to ~/.claude/settings.local.json, which is never tracked here.
for f in settings.json statusline.sh claude-powerline.json; do
  if [ ! -e "$CLAUDE/$f" ]; then
    cp "$REPO/$f" "$CLAUDE/$f"
    echo "copied  $f"
    copied=$((copied + 1))
  fi
done

# 5. Plugins: reproduce the marketplace + plugin set from plugins.txt via the
#    `claude` CLI. Content is NOT vendored — these commands add the marketplaces
#    and install the latest plugin versions, and no-op if already present.
if [ "$PLUGINS" = "1" ] && [ -f "$REPO/plugins.txt" ]; then
  if command -v claude >/dev/null 2>&1; then
    while read -r kind arg _; do
      case "$kind" in
        ''|\#*) continue ;;  # skip blanks and comments
        marketplace)
          if claude plugin marketplace add "$arg" >/dev/null 2>&1; then
            echo "plugin  marketplace $arg"
            plugins=$((plugins + 1))
          else
            echo "⚠️  FAILED to add marketplace $arg"
            skipped=$((skipped + 1))
          fi ;;
        plugin)
          if claude plugin install "$arg" >/dev/null 2>&1; then
            echo "plugin  $arg"
            plugins=$((plugins + 1))
          else
            echo "⚠️  FAILED to install plugin $arg"
            skipped=$((skipped + 1))
          fi ;;
        *) echo "⚠️  plugins.txt: unknown directive '$kind' (expected marketplace|plugin)" ;;
      esac
    done < "$REPO/plugins.txt"
  else
    echo "⚠️  SKIP plugins — 'claude' not on PATH. Run ./install.sh again where it is."
  fi
fi

# 6. Optionally prune deleted skills/agents.
if [ "$PRUNE" = "1" ]; then
  # Claude: dangling symlinks pointing into this repo (deleted skill/agent).
  for link in "$CLAUDE"/skills/* "$CLAUDE"/agents/* "$CLAUDE"/commands/*; do
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
  # Codex: our managed copies whose repo skill no longer exists. The marker
  # guards .system and hand-installed Codex skills, which lack it.
  if [ -n "$CODEX_SKILLS" ]; then
    for d in "$CODEX_SKILLS"/*/; do
      d="${d%/}"
      [ -f "$d/$MARKER" ] || continue
      name="$(basename "$d")"
      if [ ! -d "$REPO/skills/$name" ]; then
        rm -rf "$d"
        echo "pruned  $name (codex, orphaned)"
        pruned=$((pruned + 1))
      fi
    done
  fi
fi

echo "---"
echo "linked=$linked mirrored=$mirrored skipped=$skipped copied=$copied plugins=$plugins pruned=$pruned"
