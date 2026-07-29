#!/usr/bin/env bash
#
# install.sh — wire this repo into ~/.claude (and mirror skills into ~/.agents)
#
# Symlinks (repo is the live source of truth; edits apply instantly):
#   skills/<name>/  -> ~/.claude/skills/<name>
#   skills/<name>/  -> ~/.agents/skills/<name>   (only if Codex is installed)
#     The shared cross-agent skills root. Codex scans it alongside its own
#     ~/.codex/skills, and follows symlinked directories fine — so one link
#     serves Claude, Codex and anything else reading ~/.agents, live.
#     Do NOT also install into ~/.codex/skills: a skill present in both roots
#     is listed TWICE and burns double its share of Codex's skills context
#     budget (it warns about truncating descriptions when that fills up).
#     Step 1b removes copies left there by the older mirror mechanism.
#   agents/<name>.md -> ~/.claude/agents/<name>.md
#   commands/<name>.md -> ~/.claude/commands/<name>.md
#   hooks/<name> -> ~/.claude/hooks/<name>
#   global-CLAUDE.md -> ~/.claude/CLAUDE.md
#
# Copies, only if missing (the owning tool rewrites these itself, so a symlink
# would break; never clobbers an existing file):
#   settings.json             -> ~/.claude/settings.json
#   ccstatusline-settings.json -> ~/.config/ccstatusline/settings.json
#     (pass --force-statusline to overwrite an existing live file with the
#     repo's copy — needed to actually deploy a repo-side layout edit)
#   ccline-config.toml -> ~/.claude/ccline/config.toml
#     the active statusline as of 2026-07-27 (CCometixLine, via `ccline`,
#     installed separately with `npm i -g @cometix/ccline`). ccstatusline is
#     kept wired above only as a rollback path — statusLine in settings.json
#     now points at `ccline`, not `ccstatusline`.
#     (pass --force-ccline to overwrite an existing live file with the
#     repo's copy)
#
# Plugins (declared in plugins.txt, applied via the `claude` CLI — NOT vendored):
#   marketplace/plugin lines -> `claude plugin marketplace add` / `install`
#   Idempotent no-ops if already present. Skipped if `claude` isn't on PATH,
#   or with --no-plugins.
#
# Idempotent; safe to re-run. Run once after cloning on a new machine.
#
#   ./install.sh                  # link skills+agents (Claude + shared ~/.agents), copy settings if absent, sync plugins
#   ./install.sh --prune          # also remove dangling symlinks for deleted skills/agents
#   ./install.sh --no-plugins     # skip the `claude plugin` sync step
#   ./install.sh --force-statusline # redeploy ccstatusline-settings.json over an existing live file
#   ./install.sh --force-ccline   # redeploy ccline-config.toml over an existing live file
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE="$HOME/.claude"
CODEX="$HOME/.codex"
PRUNE=0
FORCE=0
PLUGINS=1
FORCE_STATUSLINE=0
FORCE_CCLINE=0
for arg in "$@"; do
  case "$arg" in
    --prune) PRUNE=1 ;;
    --force) FORCE=1 ;;
    --no-plugins) PLUGINS=0 ;;
    --force-statusline) FORCE_STATUSLINE=1 ;;
    --force-ccline) FORCE_CCLINE=1 ;;
    *) echo "unknown option: $arg (expected --prune, --force, --no-plugins, --force-statusline and/or --force-ccline)"; exit 2 ;;
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

mkdir -p "$CLAUDE/skills" "$CLAUDE/agents" "$CLAUDE/commands" "$CLAUDE/hooks"
# Mirror skills into the shared ~/.agents/skills root, but only if Codex is
# actually installed (its own dir already exists) — never create ~/.agents on a
# Claude-only box. Codex scans BOTH ~/.codex/skills and ~/.agents/skills, so
# installing into both roots makes every skill appear twice; we use only the
# shared one. See the mirror note in CLAUDE.md.
AGENTS_SKILLS=""
[ -d "$CODEX" ] && AGENTS_SKILLS="$HOME/.agents/skills"
[ -n "$AGENTS_SKILLS" ] && mkdir -p "$AGENTS_SKILLS"
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

mirror_into() { # mirror_into <source-dir> <dest-link> — shared ~/.agents root
  local src="$1" dest="$2" name
  name="$(basename "$dest")"
  # A real dir here is either a leftover copy from the old mirror mechanism
  # (marked) or a hand-installed skill (unmarked). Reclaim ours; never clobber
  # theirs.
  if [ ! -L "$dest" ] && [ -d "$dest" ]; then
    if [ -f "$dest/$MARKER" ]; then
      rm -rf "$dest"
    else
      echo "⚠️  SKIP $name (agents) — an unmanaged entry exists at $dest."
      echo "    Move it aside first, then re-run."
      skipped=$((skipped + 1))
      return
    fi
  fi
  rm -f "$dest"
  ln -s "$src" "$dest"
  echo "linked  $name (agents)"
  mirrored=$((mirrored + 1))
}

# 1. Skills: every directory holding a SKILL.md.
#    Symlinked into ~/.claude and into the shared ~/.agents/skills root that
#    Codex (and other agents) scan — the repo stays the live source of truth on
#    every surface, so editing a SKILL.md takes effect without re-running this.
for dir in "$REPO"/skills/*/; do
  [ -f "$dir/SKILL.md" ] || continue
  link_into "${dir%/}" "$CLAUDE/skills/$(basename "$dir")"
  [ -n "$AGENTS_SKILLS" ] && mirror_into "${dir%/}" "$AGENTS_SKILLS/$(basename "$dir")"
done

# 1b. Migration: drop copies left in ~/.codex/skills by the old mirror.
#     Codex scans ~/.codex/skills AND ~/.agents/skills, so a skill present in
#     both is listed twice and eats double its share of the skills context
#     budget. Unconditional (not gated on --prune) because leaving them is the
#     bug, not merely stale. Only ever removes dirs carrying our own marker —
#     .system and hand-installed Codex skills lack it and are untouched.
if [ -d "$CODEX/skills" ]; then
  for d in "$CODEX"/skills/*/; do
    d="${d%/}"
    [ -f "$d/$MARKER" ] || continue
    rm -rf "$d"
    echo "removed $(basename "$d") (codex copy, now served from ~/.agents)"
    pruned=$((pruned + 1))
  done
fi

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

# 2c. Hooks: every script in hooks/ becomes a hook helper. Symlinked, since
#     Claude Code only ever executes these — it never rewrites them. The
#     settings.json entries that invoke them are baked into the repo copy in
#     step 4, and reference "$HOME/.claude/hooks/<name>" so they survive a
#     different checkout path.
for file in "$REPO"/hooks/*; do
  [ -f "$file" ] || continue
  link_into "$file" "$CLAUDE/hooks/$(basename "$file")"
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

# 4. Settings file: copy only if missing (new-machine bootstrap).
#    settings.json in the repo has no secrets — add machine-local env/keys
#    to ~/.claude/settings.local.json, which is never tracked here.
f=settings.json
if [ ! -e "$CLAUDE/$f" ]; then
  cp "$REPO/$f" "$CLAUDE/$f"
  echo "copied  $f"
  copied=$((copied + 1))
fi

# 4b. ccstatusline layout: same copy-if-missing rule, same reason. The
#     ccstatusline TUI rewrites ~/.config/ccstatusline/settings.json in place,
#     so a symlink would let it write back into the repo unreviewed. Edit the
#     layout with the TUI, then run ./sync.sh to pull it back here.
#     --force-statusline overwrites the live file even when it already exists,
#     for the opposite direction: pushing a repo-side layout edit out live.
CCSL="$HOME/.config/ccstatusline"
if [ ! -e "$CCSL/settings.json" ]; then
  mkdir -p "$CCSL"
  cp "$REPO/ccstatusline-settings.json" "$CCSL/settings.json"
  echo "copied  ccstatusline-settings.json"
  copied=$((copied + 1))
elif [ "$FORCE_STATUSLINE" = "1" ]; then
  cp "$REPO/ccstatusline-settings.json" "$CCSL/settings.json"
  echo "forced  ccstatusline-settings.json (overwrote existing live file)"
  copied=$((copied + 1))
fi

# 4c. CCometixLine config: same copy-if-missing rule, same reason. Its own
#     `ccline -c` TUI rewrites ~/.claude/ccline/config.toml in place, so a
#     symlink would let it write back into the repo unreviewed. This is the
#     tool settings.json's statusLine actually invokes as of 2026-07-27 —
#     `npm i -g @cometix/ccline` installs the `ccline` binary separately;
#     install.sh does not install it.
CCLINE_DIR="$HOME/.claude/ccline"
if [ ! -e "$CCLINE_DIR/config.toml" ]; then
  mkdir -p "$CCLINE_DIR"
  cp "$REPO/ccline-config.toml" "$CCLINE_DIR/config.toml"
  echo "copied  ccline-config.toml"
  copied=$((copied + 1))
elif [ "$FORCE_CCLINE" = "1" ]; then
  cp "$REPO/ccline-config.toml" "$CCLINE_DIR/config.toml"
  echo "forced  ccline-config.toml (overwrote existing live file)"
  copied=$((copied + 1))
fi

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
  for link in "$CLAUDE"/skills/* "$CLAUDE"/agents/* "$CLAUDE"/commands/* "$CLAUDE"/hooks/*; do
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
  # Shared root: dangling symlinks pointing into this repo (deleted skill).
  if [ -n "$AGENTS_SKILLS" ]; then
    for link in "$AGENTS_SKILLS"/*; do
      [ -L "$link" ] || continue
      case "$(readlink "$link")" in
        "$REPO"/*)
          if [ ! -e "$link" ]; then
            rm -f "$link"
            echo "pruned  $(basename "$link") (agents, dangling)"
            pruned=$((pruned + 1))
          fi ;;
      esac
    done
  fi
fi

# 7. Post-run check: is the live settings.json on a permissive posture?
#    Step 4 only ever copies when the target is absent, so it never inspects an
#    existing file — and no repo tracks ~/.claude/settings.json any more, so
#    nothing else reports on it either. A machine provisioned from an older,
#    stale snapshot can be running with permission prompts bypassed and all Bash
#    whitelisted, and stay that way silently. Warn only; never rewrite the file.
if [ -e "$CLAUDE/settings.json" ]; then
  if command -v jq >/dev/null 2>&1; then
    if jq -e '
          (.permissions.defaultMode? == "bypassPermissions")
          or ((.permissions.allow? // []) | any(. == "Bash(*)" or . == "Bash"))
        ' "$CLAUDE/settings.json" >/dev/null 2>&1; then
      echo "⚠️  ~/.claude/settings.json is on a permissive posture:"
      echo "    defaultMode is 'bypassPermissions', and/or permissions.allow"
      echo "    whitelists Bash unconditionally. Likely provisioned from an old"
      echo "    stale snapshot. This repo's tracked settings.json is the safe one"
      echo "    ('auto' mode, scoped allowlist) — review the live file against it."
      echo "    Not changed automatically: live is authoritative for this path."
    else
      echo "checked settings.json — permission posture is not permissive"
    fi
  else
    echo "⚠️  SKIP settings.json posture check — 'jq' not on PATH."
  fi
fi

echo "---"
echo "linked=$linked mirrored=$mirrored skipped=$skipped copied=$copied plugins=$plugins pruned=$pruned"
