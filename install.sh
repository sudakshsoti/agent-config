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
#   claude-powerline.json -> ~/.claude/claude-powerline.json
#     the active statusline as of 2026-07-31 (@owloops/claude-powerline).
#     Symlinked, not copied — the binary only ever reads its config, there is
#     no companion TUI that rewrites it in place — so there is nothing to sync
#     back and repo edits go live immediately.
#
# Merged settings (repo-owned keys only; other settings remain untouched):
#   codex/config.toml -> ~/.codex/config.toml
#     Codex rewrites this file from its TUI and it may contain machine-local
#     credentials, so it cannot safely be symlinked or replaced wholesale.
#
# Also symlinked (the owning tool rewrites it, but writes follow the link and it
# holds no secrets — see step 3e):
#   omp/config.yml -> ~/.omp/agent/config.yml
#     OMP's model roles, thinking level, statusline and task settings. Changing
#     a setting from the OMP TUI edits the repo copy directly; review with
#     `git diff` before committing. Only linked if ~/.omp/agent exists.
#
# Deliberately NOT tracked or linked (machine-local by design):
#   ~/.omp/agent/mcp.json — see the "Secrets policy" section of README.md.
#   ~/.omp/agent/extensions/ — written and overwritten by the tool that owns it.
#
# Copies, only if missing (the owning tool rewrites these itself, so a symlink
# would break; never clobbers an existing file):
#   settings.json             -> ~/.claude/settings.json
#
# Git hooks (repo-local config, not ~/.claude):
#   core.hooksPath -> .githooks   (tracked, so it survives a clone; .git/hooks
#   is unusable from a worktree, where .git is a file rather than a directory)
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
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE="$HOME/.claude"
CODEX="$HOME/.codex"
OMP="$HOME/.omp/agent"
PRUNE=0
FORCE=0
PLUGINS=1
for arg in "$@"; do
  case "$arg" in
    --prune) PRUNE=1 ;;
    --force) FORCE=1 ;;
    --no-plugins) PLUGINS=0 ;;
    *) echo "unknown option: $arg (expected --prune, --force, --no-plugins)"; exit 2 ;;
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
#     step 3, and reference "$HOME/.claude/hooks/<name>" so they survive a
#     different checkout path.
for file in "$REPO"/hooks/*; do
  [ -f "$file" ] || continue
  link_into "$file" "$CLAUDE/hooks/$(basename "$file")"
done

# 3. Settings file: copy only if missing (new-machine bootstrap).
#    settings.json in the repo has no secrets — add machine-local env/keys
#    to ~/.claude/settings.local.json, which is never tracked here.
f=settings.json
if [ ! -e "$CLAUDE/$f" ]; then
  cp "$REPO/$f" "$CLAUDE/$f"
  echo "copied  $f"
  copied=$((copied + 1))
fi

# 3b. claude-powerline config: symlinked, not copy-if-missing, unlike
#     settings.json above. claude-powerline never writes its own config — there
#     is no companion TUI that could write back into the repo unreviewed — so a
#     symlink means a repo edit goes live immediately with no re-run and
#     nothing to sync back.
link_into "$REPO/claude-powerline.json" "$CLAUDE/claude-powerline.json"

# 3b2. Global CLAUDE.md: symlinked for the same reason as claude-powerline.json
#     above — Claude Code only ever reads this file, never rewrites it, so a
#     repo edit goes live immediately with nothing to sync back. Named
#     global-claude.md in the repo since the repo's own root CLAUDE.md (the
#     project-instructions file for this checkout) already owns that name.
link_into "$REPO/global-claude.md" "$CLAUDE/CLAUDE.md"

# 3c. Codex config: merge only the non-secret keys tracked in codex/config.toml.
#     Preserve unrelated user, MCP, desktop, and machine-managed settings.
if [ -d "$CODEX" ] && [ -f "$REPO/codex/config.toml" ]; then
  python3 "$REPO/scripts/apply-codex-config.py" \
    "$REPO/codex/config.toml" "$CODEX/config.toml"
  echo "merged  codex/config.toml"
fi

# 3e/3f only run when OMP is installed. Say so out loud when it isn't —
#     a silent no-op makes a verify of the form `./install.sh && readlink
#     ~/.omp/agent/config.yml` look like it passed on a machine that never got
#     the links.
if [ ! -d "$OMP" ]; then
  echo "⚠️  SKIP omp — no $OMP (OMP not installed). config.yml and agents/ not linked."
fi

# 3e. OMP config: symlinked, unlike codex/config.toml above. OMP *does* rewrite
#     this file (`omp config set`, and TUI toggles), but a write follows the
#     symlink and lands in the repo intact — verified: only trailing whitespace
#     is normalised, nothing is reordered or dropped — and the file carries no
#     credentials (OMP keeps auth in its own state dir, not here). So the repo
#     stays the live source of truth and settings changed from the TUI show up
#     as a plain `git diff` to review before committing, with no sync step.
#     Caveat: OMP locks the *resolved* path, so writes leave an empty
#     omp/config.yml.lock in the checkout — .gitignore covers it.
if [ -d "$OMP" ] && [ -f "$REPO/omp/config.yml" ]; then
  mkdir -p "$OMP"
  link_into "$REPO/omp/config.yml" "$OMP/config.yml"
fi

# 3f. OMP subagents: symlinked the same way. `adversary` is the cross-lineage
#     plan reviewer — it pins `model: "@adversary"`, so it follows the role in
#     omp/config.yml and can never resolve to an Anthropic model.
if [ -d "$OMP" ] && [ -d "$REPO/omp/agents" ]; then
  mkdir -p "$OMP/agents"
  for a in "$REPO"/omp/agents/*.md; do
    link_into "$a" "$OMP/agents/$(basename "$a")"
  done
fi

# 3d. Git hooks: point git at the tracked .githooks/ instead of .git/hooks, so
#     the pre-commit lint arrives with a clone and works from a worktree (where
#     .git is a file and has no hooks/ directory to write into). Relative on
#     purpose — it resolves per checkout.
if git -C "$REPO" rev-parse --git-dir >/dev/null 2>&1; then
  git -C "$REPO" config core.hooksPath .githooks
  echo "wired   core.hooksPath -> .githooks"
fi

# 4. Plugins: reproduce the marketplace + plugin set from plugins.txt via the
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

# 5. Optionally prune deleted skills/agents.
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

# 6. Post-run check: is the live settings.json on a permissive posture?
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
