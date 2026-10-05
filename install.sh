#!/usr/bin/env bash
#
# install.sh — wire this repo into ~/.omp/agent and ~/.pi/agent, and link
#              repo-owned and external skills into the shared ~/.agents/skills
#              and into ~/.claude/skills for Claude Code
#
# Four destinations, and nothing else:
#
#   Shared skills (source-only; one link serves every consumer):
#     skills/<name>/         -> ~/.agents/skills/<name>
#     vendor/<owner>-<repo>/* -> ~/.agents/skills/<name>   (external lines)
#       The shared cross-agent skills root. OMP, Pi, Codex and OpenCode all
#       discover it natively, so a skill is linked ONCE rather than once per
#       harness. Filled — by a full install (repo-owned and external skills)
#       or a selective `--skills-only` install alike — only when
#       shared_root_consumers_present is true: at least one of ~/.codex,
#       ~/.pi/agent, ~/.config/opencode or ~/.omp/agent exists. This repo does
#       not write Codex or OpenCode config — their directories are checked
#       read-only, purely to decide whether the shared root is worth filling.
#       With no consumer present, ~/.agents is never created and --prune skips
#       the shared root the same way. Do NOT also link into
#       ~/.pi/agent/skills: a skill found in two roots is discovered twice and
#       burns double its share of the skills context budget.
#
#   Claude Code skills:
#     skills/<name>/         -> ~/.claude/skills/<name>
#     vendor/<owner>-<repo>/* -> ~/.claude/skills/<name>   (external lines)
#       The one harness that does NOT read the shared ~/.agents root, so it
#       needs its own link per skill — the same set, linked twice. Filled only
#       when ~/.claude already exists; this never creates the directory, so a
#       machine without Claude Code installed stays untouched.
#
#       This is the single exception to the "link a skill once" rule above, and
#       it is safe only because no *other* harness reads ~/.claude/skills:
#       omp/config.yml pins `skills.enableClaudeUser: false` for exactly this
#       reason. If that pin is removed, OMP scans both roots, every skill is
#       discovered twice, and the skills context budget is spent twice over.
#       Claude Code reads ~/.claude/skills and nothing else, so the two roots
#       stay disjoint per consumer.
#
#   OMP configuration:
#     omp/config.yml         -> ~/.omp/agent/config.yml
#       OMP's model roles, thinking level, statusline and task settings.
#       Symlinked even though OMP rewrites it: writes follow the link into the
#       repo and carry no credentials, so a TUI change shows up as a plain
#       `git diff` to review before committing. There is no sync step.
#       CORRECTION 2026-08-29: an earlier comment here claimed OMP reordered
#       or dropped nothing. FALSE for comments — a fully annotated
#       modelRoles/retry block was replaced in one session by a value-identical
#       version with every `#` line gone. Do NOT keep decision rationale in
#       this file; it belongs in `design/decisions.md` or this repo's AGENTS.md.
#       OMP locks the *resolved* path, so writes leave an empty
#       omp/config.yml.lock in the checkout — .gitignore covers it.
#     omp/keybindings.yml    -> ~/.omp/agent/keybindings.yml
#     omp/lsp.yml            -> ~/.omp/agent/lsp.yml
#       Partial overrides of OMP's built-in LSP server definitions. The server
#       binaries are machine dependencies; OMP activates one only when its root
#       markers match the working directory.
#     omp/themes/*.json      -> ~/.omp/agent/themes/*.json
#       Linked individually so machine-local themes survive.
#     omp/agents/*.md        -> ~/.omp/agent/agents/*.md
#       `adversary` is the cross-lineage plan reviewer; it pins
#       `model: "@adversary"`, so it follows the role in omp/config.yml.
#     omp/commands/*.md      -> ~/.omp/agent/commands/*.md
#       One-line `/name` wrappers that load the same-named skill, so `/push`
#       works without the `/skill:` prefix. The skill stays the source.
#     omp/overlays/*         -> ~/.config/omp/*
#       Holds search-keys.tpl, the 1Password template behind
#       `op inject -o ~/.omp/.env`. Linked file by file so other files in
#       ~/.config/omp stay untouched.
#     global-agents.md       -> ~/.omp/agent/AGENTS.md
#       Harness-neutral shared preferences, linked so one edit reaches every
#       installed harness. None of these tools rewrite the file.
#
#   Herdr configuration:
#     herdr/config.toml      -> ~/.config/herdr/config.toml
#       Herdr keybindings, including plugin-action bindings. Herdr rewrites the
#       file from its settings UI; the write follows the link. Applied only when
#       ~/.config/herdr exists. herdr/plugins.txt (`<owner/repo> <ref>` per line) is
#       installed with `herdr plugin install` unless --no-external.
#
#   Pi configuration:
#     pi/settings.json       -> ~/.pi/agent/settings.json
#       Pi's default model, Ctrl+P model list, thinking level, theme and
#       package list. Pi rewrites it itself (`pi install`, `/settings`, the
#       theme picker) and the write follows the symlink into the repo, so the
#       repo stays the live source with no sync step. Pi keeps credentials in
#       ~/.pi/agent/auth.json, never here.
#     pi/pi-fff.json         -> ~/.pi/agent/pi-fff.json
#       Persistent global extension config; stops FFF indexing $HOME.
#     pi/keybindings.json    -> ~/.pi/agent/keybindings.json
#     pi/workflows/model-tiers.json -> ~/.pi/workflows/model-tiers.json
#       small/medium/big model tiers for pi-dynamic-workflows. Pi's
#       /workflows-models may replace the link with a plain file; re-run to relink.
#     pi/prompts/*.md, pi/themes/*.json, pi/agents/*.md
#       Linked individually so machine-local entries survive.
#     pi/extensions/*/{index.js,index.ts,theme.json} -> ~/.pi/agent/extensions/*/
#       Linked file by file so local runtime data inside the directory survives.
#     pi/web-search.json     -> the live pi-web-access config path(s)
#       MERGED, not linked: the live file is also pi-web-access's credential
#       store, so only the repo-owned preference keys are pushed and credentials
#       stay machine-local. PI_CODING_AGENT_DIR and XDG_CONFIG_HOME are honored;
#       without either, both the 0.23.0 and 0.29.0 default paths are written.
#     global-agents.md       -> ~/.pi/agent/AGENTS.md
#
#   Claude Code configuration (only when ~/.claude exists and not the work machine):
#     claude/{statusline.sh,subagent-statusline.sh,claude-powerline.json}
#                            -> ~/.claude/
#       Linked. A real file already there with identical content is adopted
#       (replaced by the link) rather than skipped.
#     claude/settings.json   -> ~/.claude/settings.json
#       MERGED, not linked: Claude Code writes the file itself, herdr owns its
#       SessionStart hook there, and it holds OPENROUTER_API_KEY for the Jev
#       compaction plugin. Only the repo-owned keys are pushed; the key is
#       copied from JEV_OPENROUTER_API_KEY in ~/.omp/.env (1Password-injected,
#       never tracked) by scripts/apply-json-config.py.
#     claude/plugins.txt     -> `claude plugin marketplace add` + `install`
#       Skipped by --no-external.
#     snapshots/claude/mcp.json -> `claude mcp add-json --scope user`, adding
#       only servers ~/.claude.json lacks; existing servers are never touched.
#
#   Claude Code agents (only when ~/.claude exists; on the work machine only
#   with --claude-agents):
#     claude/agents/*.md     -> ~/.claude/agents/*.md, one link per agent.
#       Claude-only models inside Claude Code, so no new vendor sees work code;
#       the work gate keeps them opt-in rather than off.
#
#   OMP extras:
#     omp/plugins.txt        -> `omp plugin install` (skipped by --no-external)
#     snapshots/omp/mcp.json -> ~/.omp/agent/mcp.json, adding only missing servers
#
# Deliberately NOT tracked or linked (machine-local by design):
#   ~/.claude/CLAUDE.md — retired; global-agents.md reaches Claude Code only if
#     you add an `@` include by hand. --prune removes a stale link to it.
#   ~/.claude/hooks/ — written by `herdr integration install`, not by this repo.
#   ~/.claude.json, ~/.claude/plugins/ — Claude Code's state (accounts, caches).
#   ~/.omp/agent/mcp.json — never linked; see the "Secrets policy" section of
#     README.md. snapshots/omp/mcp.json is its snapshot (scripts/snapshot-
#     machine-config.sh); this installer only seeds missing servers from it.
#   ~/.omp/agent/extensions/ — written and overwritten by the tool that owns it.
#   ~/.omp/.env — produced by `op inject` from omp/overlays/search-keys.tpl.
#   ~/.omp/agent/agent.db — logins (`omp` /login); they do not transfer.
#   ~/.pi/agent/auth.json — OAuth tokens and provider API keys.
#   ~/.pi/agent/models-store.json — a refetchable provider catalog cache.
#   ~/.pi/agent/skills/ — Pi already discovers ~/.agents/skills, which this
#     script fills. Linking here too means every skill is discovered twice.
#
# Git hooks (repo-local config, not a harness path):
#   core.hooksPath -> .githooks   (tracked, so it survives a clone; .git/hooks
#   is unusable from a worktree, where .git is a file rather than a directory)
#
# External skill sources (declared in plugins.txt as `external` lines):
#   external <owner/repo>[:<subdir>] [skill ...] -> git clone/pull into
#   vendor/<owner>-<repo>/ (gitignored), then link its skills (all of them, or
#   only the named ones) into ~/.agents/skills, naming each by its frontmatter
#   `name:` rather than its directory. The optional :<subdir> pins which tree to
#   read when a repo ships several copies. Vendored by reference, never copied:
#   upstream files do not enter this repo's history and are not linted here.
#   Name collisions resolve by fixed precedence (AGENTS.md, Skills); each loser
#   is skipped with a warning and counted in `skipped`.
#
# Idempotent; safe to re-run. Run once after cloning on a new machine.
#
# Work machine: when chezmoi (owned by ~/dev/dotfiles) reports .machine=work,
# steps 3-5e are skipped and only skills are linked. OMP, Pi and Claude Code
# config routes prompts, repository source included, to OpenCode Go, Muse Code
# and OpenRouter, and employer code may only reach the employer's sanctioned
# vendor.
#
#   ./install.sh                     # link skills, OMP config and Pi config
#   ./install.sh --prune             # also clear managed links that are gone
#   ./install.sh --no-external       # skip the external git fetch (offline)
#   ./install.sh --skills-only=name,other-name  # link only named repo-owned
#                                   # skills into ~/.agents/skills
#   ./install.sh --claude-agents     # work machine: also link Claude Code agents
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENDOR="$REPO/vendor"
SKILLS_ROOT="$HOME/.agents/skills"
CLAUDE="$HOME/.claude"
CLAUDE_SKILLS="$CLAUDE/skills"
OMP="$HOME/.omp/agent"
OMP_OVERLAYS="$HOME/.config/omp"
PI="$HOME/.pi/agent"

# machine_profile: the chezmoi `.machine` value (personal, work or server), or
# nothing when chezmoi is absent or has no profile. Dotfiles owns the profile;
# this repo only reads it. Unknown installs as before, so the gate needs
# dotfiles applied first, which the dotfiles README's order guarantees.
machine_profile() {
  command -v chezmoi >/dev/null 2>&1 || return 0
  chezmoi data --format json 2>/dev/null |
    python3 -c 'import json, sys
try:
    print(json.load(sys.stdin).get("machine", ""))
except Exception:
    pass' 2>/dev/null || true
}
MACHINE="$(machine_profile)"

# shared_root_consumers_present: true when some tool that reads the shared
# ~/.agents/skills root is installed. Codex and OpenCode read that root
# natively even though this repo no longer writes their config, so checking
# for ~/.codex and ~/.config/opencode here decides only whether filling the
# shared root is worthwhile — it must NOT reintroduce any Codex/OpenCode
# config writes, and none are added below. Full installs (repo-owned and
# external skills), selective (--skills-only) installs and --prune all gate
# on this one predicate, so every consumer set produces identical shared-root
# links regardless of mode.
shared_root_consumers_present() {
  [ -d "$HOME/.codex" ] || [ -d "$PI" ] || [ -d "$HOME/.config/opencode" ] || [ -d "$OMP" ]
}

PRUNE=0
FORCE=0
EXTERNAL=1
SKILLS_ONLY=0
SELECTED_SKILLS=""
CLAUDE_AGENTS=0
for arg in "$@"; do
  case "$arg" in
  --prune) PRUNE=1 ;;
  --force) FORCE=1 ;;
  --no-external) EXTERNAL=0 ;;
  --claude-agents) CLAUDE_AGENTS=1 ;;
  --skills-only=*)
    if [ "$SKILLS_ONLY" = "1" ]; then
      echo "--skills-only may be specified only once"
      exit 2
    fi
    SKILLS_ONLY=1
    SELECTED_SKILLS="${arg#--skills-only=}"
    ;;
  *)
    echo "unknown option: $arg (expected --prune, --force, --no-external, --claude-agents, --skills-only=name,other-name)"
    exit 2
    ;;
  esac
done

# Guard: the symlinks bake in this checkout's absolute path. Running from an
# ephemeral git worktree pins every installed link to a path that vanishes when
# the worktree is cleaned up — silently breaking the whole personal skill set.
# Refuse unless --force.
case "$REPO" in
*/.git/worktrees/* | */worktrees/*)
  if [ "$FORCE" != "1" ]; then
    echo "⛔ Refusing to install from what looks like an ephemeral worktree:"
    echo "     $REPO"
    echo "   Symlinks bake in this absolute path; when the worktree is removed,"
    echo "   every installed skill link dangles. Run from your canonical"
    echo "   checkout (e.g. ~/dev/agent-config) instead, or pass --force if you"
    echo "   really mean to point the global install here."
    exit 1
  fi
  echo "⚠️  --force: installing from an ephemeral-looking path ($REPO)."
  ;;
esac

# Guard: a *linked* Git worktree (`git worktree add`) is refused structurally
# rather than by path, because its location is arbitrary. Its git dir lives
# under the primary checkout's .git/worktrees/, while its common git dir is that
# primary .git — the two differ exactly when a checkout is linked. Symlinks bake
# in this worktree's absolute path, so removing the worktree dangles every
# installed link. Git older than 2.31 has no --path-format, so fall back to
# plain rev-parse and resolve relative output against REPO. If Git cannot answer
# at all (not a repository, or a PATH stub), keep the path-pattern behavior
# above and carry on. --force overrides with a warning.
# Run Git without ambient repository selectors. A shell hook or wrapper can set
# GIT_DIR/GIT_INDEX_FILE/GIT_WORK_TREE for its own work; install.sh must always
# inspect and update the checkout named by REPO instead.
git_without_repo_selectors() {
  (
    unset GIT_DIR GIT_INDEX_FILE GIT_WORK_TREE
    git "$@"
  )
}

resolve_from_repo() { # resolve_from_repo <path> -> canonical absolute path
  local path parent base
  case "$1" in
  /*) path="$1" ;;
  *) path="$REPO/$1" ;;
  esac
  if [ -d "$path" ]; then
    (cd "$path" && pwd -P)
    return
  fi
  parent="$(dirname "$path")"
  base="$(basename "$path")"
  if ! parent="$(cd "$parent" && pwd -P)"; then
    return 1
  fi
  printf '%s/%s' "$parent" "$base"
}

git_dirs() { # git_dirs -> "<git-dir>\n<common-git-dir>", non-zero if unknown
  local dir common
  if dir="$(git_without_repo_selectors -C "$REPO" rev-parse --path-format=absolute --git-dir 2>/dev/null)" &&
    common="$(git_without_repo_selectors -C "$REPO" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"; then
    printf '%s\n%s\n' "$dir" "$common"
    return 0
  fi
  dir="$(git_without_repo_selectors -C "$REPO" rev-parse --git-dir 2>/dev/null)" || return 1
  common="$(git_without_repo_selectors -C "$REPO" rev-parse --git-common-dir 2>/dev/null)" || return 1
  local resolved_dir resolved_common
  resolved_dir="$(resolve_from_repo "$dir")" || return 1
  resolved_common="$(resolve_from_repo "$common")" || return 1
  printf '%s\n%s\n' "$resolved_dir" "$resolved_common"
}

if git_dirs_output="$(git_dirs)"; then
  git_dir="${git_dirs_output%%$'\n'*}"
  common_dir="${git_dirs_output#*$'\n'}"
  if [ "$git_dir" != "$common_dir" ]; then
    if [ "$FORCE" != "1" ]; then
      echo "⛔ Refusing to install from a linked worktree:"
      echo "     $REPO"
      echo "   Its git dir ($git_dir) differs from the common git dir"
      echo "   ($common_dir), so this checkout shares an object store with"
      echo "   another working tree. Symlinks bake in this absolute path; if"
      echo "   this worktree is removed, every installed link dangles. Run from"
      echo "   the primary checkout instead, or pass --force if you really mean"
      echo "   to point the global install here."
      exit 1
    fi
    echo "⚠️  --force: installing from a linked worktree ($REPO)."
  fi
fi

# Fetch external checkouts before linking skills.
fetch_external_sources() {
  [ -f "$REPO/plugins.txt" ] || return
  while read -r kind arg rest; do
    [ "$kind" = "external" ] || continue
    case "$arg" in
    */*) : ;;
    *) continue ;;
    esac
    local repo slug clone
    repo="${arg%%:*}"
    slug="${repo%/*}-${repo#*/}"
    clone="$VENDOR/$slug"
    if [ -d "$clone/.git" ]; then
      if git_without_repo_selectors -C "$clone" pull --ff-only --quiet 2>/dev/null; then
        echo "pulled  $repo (vendor/$slug)"
      else
        echo "⚠️  could not fast-forward vendor/$slug — using the checkout as-is"
      fi
    else
      mkdir -p "$VENDOR"
      if git_without_repo_selectors clone --depth 1 --quiet "https://github.com/$repo.git" "$clone" 2>/dev/null; then
        echo "cloned  $repo -> vendor/$slug"
      else
        echo "⚠️  FAILED to clone $repo"
      fi
    fi
  done <"$REPO/plugins.txt"
}

MARKER=".agent-config-managed"
linked=0 skipped=0 pruned=0 external=0
ACTIVE_SKILLS=" "
# name<TAB>source-dir per declared skill, recorded during enumeration so the
# same set can be linked into more than one root. Enumeration is independent of
# whether either root is filled, so the two destinations gate separately.
SKILL_SOURCES=""

link_into() { # link_into <source> <dest-link>
  local src="$1" link="$2" name
  name="$(basename "$link")"
  if [ -L "$link" ]; then
    rm -f "$link" # replace any existing symlink
  elif [ -f "$link" ] && cmp -s "$src" "$link"; then
    rm -f "$link" # byte-identical real file: nothing is lost by adopting it
    echo "adopt   $name — replaced an identical copy with the link"
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

link_skill_into() { # link_skill_into <source-dir> <dest-link>
  # A real directory here is either a leftover copy from the retired
  # mirror mechanism (marked with our own marker) or a hand-installed skill
  # (unmarked). Reclaim ours; never clobber theirs.
  local src="$1" dest="$2" name
  name="$(basename "$dest")"
  if [ ! -L "$dest" ] && [ -d "$dest" ]; then
    if [ -f "$dest/$MARKER" ]; then
      rm -rf "$dest"
    else
      echo "⚠️  SKIP $name — an unmanaged directory exists at $dest."
      echo "    Move it aside first, then re-run."
      skipped=$((skipped + 1))
      return
    fi
  fi
  link_into "$src" "$dest"
}

record_skill() { # record_skill <name> <source-dir>
  ACTIVE_SKILLS="$ACTIVE_SKILLS$1 "
  SKILL_SOURCES="$SKILL_SOURCES$1"$'\t'"$2"$'\n'
}

# resolve_external_candidates: when several external lines ship the same skill
# name, exactly one wins, by the precedence in AGENTS.md (Skills). Losers are
# skipped with a warning, never an error. Repo-owned skills were already
# filtered out when each candidate was collected.
EXTERNAL_CANDIDATES=""
resolve_external_candidates() {
  local name dir repo verdict
  [ -n "$EXTERNAL_CANDIDATES" ] || return 0
  while IFS=$'\t' read -r name dir repo verdict; do
    [ -n "$name" ] || continue
    if [ "$verdict" = "W" ]; then
      record_skill "$name" "$dir"
      if [ "$FILL_SHARED" = "1" ]; then
        link_skill_into "$dir" "$SKILLS_ROOT/$name"
      fi
    else
      echo "⚠️  SKIP $name (external $repo) — shadowed by external ${verdict#L:}"
      skipped=$((skipped + 1))
    fi
  done < <(printf '%s' "$EXTERNAL_CANDIDATES" | awk -F'\t' '
    { name[NR] = $1; dir[NR] = $2; repo[NR] = $3
      rank = $4 # explicit beats bare; earlier beats later within a kind
      if (!($1 in best) || rank > bestrank[$1]) { best[$1] = NR; bestrank[$1] = rank } }
    END { for (i = 1; i <= NR; i++)
      printf "%s\t%s\t%s\t%s\n", name[i], dir[i], repo[i], (best[name[i]] == i ? "W" : "L:" repo[best[name[i]]]) }')
}

if [ "$SKILLS_ONLY" = "1" ]; then
  if [ "$PRUNE" = "1" ]; then
    echo "--skills-only cannot be combined with --prune"
    exit 2
  fi
  if [[ ! "$SELECTED_SKILLS" =~ ^[a-zA-Z0-9_-]+(,[a-zA-Z0-9_-]+)*$ ]]; then
    echo "--skills-only requires a comma-separated list of repo-owned skill names"
    exit 2
  fi
  IFS=',' read -r -a selected_names <<<"$SELECTED_SKILLS"
  for name in "${selected_names[@]}"; do
    if [[ ! "$name" =~ ^[a-zA-Z0-9][a-zA-Z0-9_-]*$ ]] ||
      [ -L "$REPO/skills/$name" ] || [ ! -f "$REPO/skills/$name/SKILL.md" ]; then
      echo "invalid or missing repo-owned skill: $name"
      exit 2
    fi
  done

  # Nothing reads the shared root: create no ~/.agents at all, rather than
  # filling it for consumers that are not there.
  if ! shared_root_consumers_present; then
    echo "note: no shared-skill-root consumer present (~/.codex, ~/.pi/agent, ~/.config/opencode, ~/.omp/agent) — skipping ~/.agents/skills"
    exit 0
  fi

  # Check the root and every destination before creating a directory or
  # replacing a link, so a refusal never leaves a partial install.
  parent="$SKILLS_ROOT"
  while [ "$parent" != "$HOME" ] && [ "$parent" != "/" ]; do
    if { [ -e "$parent" ] || [ -L "$parent" ]; } && [ ! -d "$parent" ]; then
      echo "refusing non-directory skill root: $parent"
      exit 1
    fi
    parent="$(dirname "$parent")"
  done
  for name in "${selected_names[@]}"; do
    target="$SKILLS_ROOT/$name"
    if [ ! -L "$target" ] && [ -e "$target" ]; then
      echo "refusing real (non-symlink) skill destination: $target"
      exit 1
    fi
  done
  mkdir -p "$SKILLS_ROOT"
  for name in "${selected_names[@]}"; do
    link_into "$REPO/skills/$name" "$SKILLS_ROOT/$name"
  done
  echo "selected skill links=$linked"
  exit 0
fi

[ "$EXTERNAL" = "1" ] && fetch_external_sources

# Which roots get filled. The shared root is filled only when something reads
# it; ~/.claude/skills only when Claude Code is already installed. Neither
# directory is created speculatively. Skill *enumeration* below runs whenever
# either root is in play, so the two destinations gate independently and a
# machine with only one of them still gets a complete, correct set.
FILL_SHARED=0
if shared_root_consumers_present; then FILL_SHARED=1; fi
FILL_CLAUDE=0
if [ -d "$CLAUDE" ]; then FILL_CLAUDE=1; fi

if [ "$FILL_SHARED" = "1" ] || [ "$FILL_CLAUDE" = "1" ]; then
  if [ "$FILL_SHARED" = "1" ]; then mkdir -p "$SKILLS_ROOT"; fi

  # 1. Repo-owned skills: every directory holding a SKILL.md.
  for dir in "$REPO"/skills/*/; do
    [ -f "$dir/SKILL.md" ] || continue
    name="$(basename "$dir")"
    record_skill "$name" "${dir%/}"
    if [ "$FILL_SHARED" = "1" ]; then
      link_skill_into "${dir%/}" "$SKILLS_ROOT/$name"
    fi
  done

  # 2. External skill sources: `external <owner/repo>` lines in plugins.txt.
  #    Cloned into vendor/<owner>-<repo>/ (gitignored) and linked into the same
  #    shared root, so one link reaches OMP and Pi alike. Fetching honours
  #    --no-external; relinking always runs, so an offline re-run still repairs
  #    the links from what is already cloned.
  if [ -f "$REPO/plugins.txt" ]; then
    while read -r kind arg rest; do
      [ "$kind" = "external" ] || continue
      case "$arg" in
      */*) : ;;
      *)
        echo "⚠️  plugins.txt: external '$arg' is not owner/repo — skipped"
        skipped=$((skipped + 1))
        continue
        ;;
      esac
      # `owner/repo[:subdir]` — the optional subdir pins which tree to read when a
      # repo ships several, all with the same skill names.
      repo="${arg%%:*}"
      subdir=""
      case "$arg" in *:*) subdir="${arg#*:}" ;; esac
      slug="${repo%/*}-${repo#*/}"
      clone="$VENDOR/$slug"

      if [ ! -d "$clone" ]; then
        echo "⚠️  SKIP external $repo — vendor/$slug is absent (re-run without --no-external)"
        skipped=$((skipped + 1))
        continue
      fi

      # An optional space-separated skill list after the source narrows what gets
      # linked. Empty means every skill found — right for a small, curated repo,
      # wrong for a grab bag whose extras are dead weight in the context budget.
      want="$rest"
      explicit=0
      [ -n "$want" ] && explicit=1
      # Where the skill dirs live. An explicit subdir wins; otherwise skills/ if
      # present, else the repo root. A repo that is itself one skill puts SKILL.md
      # at the root, so that is checked separately below.
      if [ -n "$subdir" ]; then
        src_root="$clone/$subdir"
      elif [ -d "$clone/skills" ]; then
        src_root="$clone/skills"
      else
        src_root="$clone"
      fi

      # The skill's real name is its frontmatter `name:`, NOT its directory —
      # a repo may ship skills/macos/ declaring `name: macos-design-guidelines`,
      # and linking it as "macos" installs a skill whose directory and manifest
      # disagree.
      skill_name() { # skill_name <dir-with-SKILL.md>
        local n
        n="$(sed -n '/^---$/,/^---$/{s/^name:[[:space:]]*//p;}' "$1/SKILL.md" 2>/dev/null | head -1)"
        n="${n%\"}"
        n="${n#\"}"
        n="${n%\'}"
        n="${n#\'}"
        [ -n "$n" ] || n="$(basename "$1")"
        printf '%s' "$n"
      }

      link_skill() { # link_skill <dir>
        local dir="$1" name
        name="$(skill_name "$dir")"
        if [ -n "$want" ] && ! printf '%s ' $want | grep -q "^$name \| $name "; then
          return 1
        fi
        # A repo-owned skill always wins: same name, ours is the live one.
        if [ -d "$REPO/skills/$name" ]; then
          echo "⚠️  SKIP $name (external $repo) — shadowed by this repo's skills/$name"
          skipped=$((skipped + 1))
          return 1
        fi
        # Linking waits until every line is read, so precedence can see all
        # candidates (see resolve_external_candidates).
        EXTERNAL_CANDIDATES="$EXTERNAL_CANDIDATES$name"$'\t'"$dir"$'\t'"$repo"$'\t'"$explicit"$'\n'
        return 0
      }

      found=0
      if [ -f "$src_root/SKILL.md" ]; then
        # Single-skill repo: SKILL.md sits at the root.
        link_skill "$src_root" && found=$((found + 1))
      else
        for dir in "$src_root"/*/; do
          [ -f "$dir/SKILL.md" ] || continue
          link_skill "${dir%/}" && found=$((found + 1))
        done
      fi

      if [ "$found" = "0" ]; then
        echo "⚠️  external $arg — no matching SKILL.md found under vendor/$slug${subdir:+/$subdir}"
        skipped=$((skipped + 1))
      else
        external=$((external + 1))
      fi
    done <"$REPO/plugins.txt"
    resolve_external_candidates
  fi
else
  echo "note: no shared-skill-root consumer present (~/.codex, ~/.pi/agent, ~/.config/opencode, ~/.omp/agent) and no ~/.claude — skipping ~/.agents/skills and ~/.claude/skills"
fi

if [ "$FILL_SHARED" != "1" ] && [ "$FILL_CLAUDE" = "1" ]; then
  echo "note: no shared-skill-root consumer present — filling ~/.claude/skills only"
fi

# 2b. Claude Code: the one harness that does not read ~/.agents/skills, so the
#     same declared set is linked a second time into ~/.claude/skills. Safe
#     only while omp/config.yml pins skills.enableClaudeUser false — see this
#     file's header. Real directories already there (Paseo's own skills, any
#     hand-installed one) are left alone by link_skill_into.
if [ "$FILL_CLAUDE" = "1" ]; then
  mkdir -p "$CLAUDE_SKILLS"
  while IFS=$'\t' read -r name src; do
    [ -n "$name" ] || continue
    link_skill_into "$src" "$CLAUDE_SKILLS/$name"
  done <<<"$SKILL_SOURCES"
else
  echo "⚠️  SKIP claude — no $CLAUDE (Claude Code not installed). skills/ not linked."
fi

# 2c. Claude Code agents. They run only Claude models inside Claude Code, so
#     unlike steps 3-5e they may reach the work machine, where tokens are
#     tightest — but only when asked for with --claude-agents.
if [ -d "$CLAUDE" ] && [ -d "$REPO/claude/agents" ]; then
  if [ "$MACHINE" != "work" ] || [ "$CLAUDE_AGENTS" = "1" ]; then
    mkdir -p "$CLAUDE/agents"
    for agent in "$REPO"/claude/agents/*.md; do
      [ -f "$agent" ] || continue
      link_into "$agent" "$CLAUDE/agents/$(basename "$agent")"
    done
  else
    echo "note: claude agents not linked on the work machine; re-run with --claude-agents to add them"
  fi
fi

# Steps 3-5e link harness config, and never on the work machine: see the
# header. Skills above are already linked there.
if [ "$MACHINE" = "work" ]; then
  echo "⚠️  SKIP omp + pi + claude config — chezmoi says this is the work machine. Their model routing and the Claude compaction plugin reach providers work code must not; skills only."
else
  # 3. global-agents.md: harness-neutral shared preferences, linked into each
  #    installed harness's user-level instruction path so one edit reaches both.
  #    Named global-agents.md in the repo because this checkout's own root
  #    AGENTS.md already owns that name.
  [ -d "$OMP" ] && link_into "$REPO/global-agents.md" "$OMP/AGENTS.md"
  [ -d "$PI" ] && link_into "$REPO/global-agents.md" "$PI/AGENTS.md"

  # 4. OMP configuration. Only run when OMP is installed; say so out loud, since
  #    a silent no-op makes `./install.sh && readlink ~/.omp/agent/config.yml`
  #    look like it passed on a machine that never got the links.
  if [ ! -d "$OMP" ]; then
    echo "⚠️  SKIP omp — no $OMP (OMP not installed). config.yml, keybindings.yml, lsp.yml, themes/, agents/ and commands/ not linked."
  fi

  if [ -d "$OMP" ] && [ -f "$REPO/omp/config.yml" ]; then
    mkdir -p "$OMP"
    link_into "$REPO/omp/config.yml" "$OMP/config.yml"
  fi
  if [ -d "$OMP" ] && [ -f "$REPO/omp/keybindings.yml" ]; then
    link_into "$REPO/omp/keybindings.yml" "$OMP/keybindings.yml"
  fi
  if [ -d "$OMP" ] && [ -f "$REPO/omp/lsp.yml" ]; then
    link_into "$REPO/omp/lsp.yml" "$OMP/lsp.yml"
  fi
  if [ -d "$OMP" ] && [ -d "$REPO/omp/themes" ]; then
    mkdir -p "$OMP/themes"
    for theme_file in "$REPO"/omp/themes/*.json; do
      [ -f "$theme_file" ] || continue
      link_into "$theme_file" "$OMP/themes/$(basename "$theme_file")"
    done
  fi
  if [ -d "$OMP" ] && [ -d "$REPO/omp/agents" ]; then
    mkdir -p "$OMP/agents"
    for a in "$REPO"/omp/agents/*.md; do
      [ -f "$a" ] || continue
      link_into "$a" "$OMP/agents/$(basename "$a")"
    done
  fi
  if [ -d "$OMP" ] && [ -d "$REPO/omp/commands" ]; then
    mkdir -p "$OMP/commands"
    for c in "$REPO"/omp/commands/*.md; do
      [ -f "$c" ] || continue
      link_into "$c" "$OMP/commands/$(basename "$c")"
    done
  fi

  # 4b. OMP overlays folder (search-keys.tpl): linked individually so other
  #     files in ~/.config/omp are never touched.
  if [ -d "$REPO/omp/overlays" ]; then
    mkdir -p "$OMP_OVERLAYS"
    for overlay in "$REPO"/omp/overlays/*; do
      [ -f "$overlay" ] || continue
      link_into "$overlay" "$OMP_OVERLAYS/$(basename "$overlay")"
    done
  fi

  # 5. Pi configuration. Same reasoning as OMP above: Pi rewrites settings.json
  #    itself and the write follows the symlink into the repo.
  if [ ! -d "$PI" ]; then
    echo "⚠️  SKIP pi — no $PI (pi not installed). settings.json, verbosity.json, pi-fff.json, keybindings.json, workflows/model-tiers.json, prompts/, themes/, extensions/ and agents/ not linked."
  fi
  if [ -d "$PI" ] && [ -f "$REPO/pi/settings.json" ]; then
    mkdir -p "$PI"
    link_into "$REPO/pi/settings.json" "$PI/settings.json"
  fi
  if [ -d "$PI" ] && [ -f "$REPO/pi/verbosity.json" ]; then
    link_into "$REPO/pi/verbosity.json" "$PI/verbosity.json"
  fi
  if [ -d "$PI" ] && [ -f "$REPO/pi/pi-fff.json" ]; then
    link_into "$REPO/pi/pi-fff.json" "$PI/pi-fff.json"
  fi
  # pi keybindings: overrides only — every action Pi does not name here keeps its
  # default chord.
  if [ -d "$PI" ] && [ -f "$REPO/pi/keybindings.json" ]; then
    link_into "$REPO/pi/keybindings.json" "$PI/keybindings.json"
  fi
  if [ -d "$PI" ] && [ -f "$REPO/pi/workflows/model-tiers.json" ]; then
    mkdir -p "$HOME/.pi/workflows"
    link_into "$REPO/pi/workflows/model-tiers.json" "$HOME/.pi/workflows/model-tiers.json"
  fi
  if [ -d "$PI" ] && [ -d "$REPO/pi/prompts" ]; then
    mkdir -p "$PI/prompts"
    for prompt_file in "$REPO"/pi/prompts/*.md; do
      [ -f "$prompt_file" ] || continue
      link_into "$prompt_file" "$PI/prompts/$(basename "$prompt_file")"
    done
  fi
  if [ -d "$PI" ] && [ -d "$REPO/pi/themes" ]; then
    mkdir -p "$PI/themes"
    for theme_file in "$REPO"/pi/themes/*.json; do
      [ -f "$theme_file" ] || continue
      link_into "$theme_file" "$PI/themes/$(basename "$theme_file")"
    done
  fi
  # Pi extensions and their theme overrides: linked file by file so local runtime
  # data within ~/.pi/agent/extensions survives installation. A directory may
  # contain an index.js/index.ts extension, a theme.json, or both.
  if [ -d "$PI" ] && [ -d "$REPO/pi/extensions" ]; then
    mkdir -p "$PI/extensions"
    for extension_dir in "$REPO"/pi/extensions/*; do
      [ -d "$extension_dir" ] || continue
      target_dir="$PI/extensions/$(basename "$extension_dir")"
      # Reclaim a legacy directory symlink from the pre-file-by-file layout. The
      # files inside it are already this repo's files, so dropping the link loses
      # nothing. A link pointing anywhere else is hand-made: never clobber it.
      if [ -L "$target_dir" ]; then
        if [ "$(readlink "$target_dir")" = "$extension_dir" ]; then
          rm -f "$target_dir"
          echo "reclaim $(basename "$extension_dir") — replaced legacy directory symlink"
        else
          echo "⚠️  SKIP $(basename "$extension_dir") — $target_dir is a symlink to $(readlink "$target_dir")."
          skipped=$((skipped + 1))
          continue
        fi
      fi
      mkdir -p "$target_dir"
      for extension_file in "$extension_dir"/index.js "$extension_dir"/index.ts "$extension_dir"/theme.json; do
        [ -f "$extension_file" ] || continue
        link_into "$extension_file" "$target_dir/$(basename "$extension_file")"
      done
    done
  fi
  # pi subagents: custom agent definitions read by pi-dynamic-workflows (agentType).
  if [ -d "$PI" ] && [ -d "$REPO/pi/agents" ]; then
    mkdir -p "$PI/agents"
    for a in "$REPO"/pi/agents/*.md; do
      [ -f "$a" ] || continue
      link_into "$a" "$PI/agents/$(basename "$a")"
    done
  fi

  # 5b. pi web-search preferences: merged, never symlinked, because this one file
  #     is also pi-web-access's credential store — keys written there by the
  #     extension must not follow a link back into the repo. Only repo-owned
  #     preferences are pushed; credentials and unmanaged settings survive.
  #
  #     pi-web-access honors PI_CODING_AGENT_DIR, then XDG_CONFIG_HOME. Without
  #     either override, 0.23.0 reads ~/.pi/web-search.json and 0.29.0 reads
  #     ~/.pi/agent/web-search.json, so write both default paths during migration.
  if [ -d "$PI" ] && [ -f "$REPO/pi/web-search.json" ]; then
    if [ -n "${PI_CODING_AGENT_DIR:-}" ]; then
      web_search_configs=("$PI_CODING_AGENT_DIR/web-search.json")
    elif [ -n "${XDG_CONFIG_HOME:-}" ]; then
      web_search_configs=("$XDG_CONFIG_HOME/pi/web-search.json")
    else
      web_search_configs=("$HOME/.pi/web-search.json" "$PI/web-search.json")
    fi

    for web_search_config in "${web_search_configs[@]}"; do
      if python3 "$REPO/scripts/apply-json-config.py" \
        "$REPO/pi/web-search.json" "$web_search_config"; then
        echo "merged  pi/web-search.json -> $web_search_config"
      else
        echo "⚠️  pi/web-search.json not merged into $web_search_config; fix the file and re-run."
        skipped=$((skipped + 1))
      fi
    done
  fi

  # 5c. Herdr (agent multiplexer). herdr/config.toml carries keybindings and
  #     plugin-action bindings only; herdr rewrites it from its settings UI and
  #     the write follows the link into the repo. Plugins are declared in
  #     herdr/plugins.txt as `<owner/repo> <ref>` and installed by herdr itself,
  #     which builds them from source (network + toolchain), so --no-external
  #     skips that half. Plugin state under ~/.config/herdr/plugins is untracked.
  if [ -d "$HOME/.config/herdr" ]; then
    link_into "$REPO/herdr/config.toml" "$HOME/.config/herdr/config.toml"
    if [ "$EXTERNAL" = "1" ] && [ -f "$REPO/herdr/plugins.txt" ] && command -v herdr >/dev/null 2>&1; then
      herdr_installed="$(herdr plugin list 2>/dev/null || true)"
      while read -r plugin_repo plugin_ref _; do
        case "$plugin_repo" in "" | \#*) continue ;; esac
        case "$herdr_installed" in
        *"github:$plugin_repo@$plugin_ref"*) continue ;;
        esac
        if herdr plugin install "$plugin_repo" --ref "$plugin_ref" --yes >/dev/null 2>&1; then
          echo "plugin  $plugin_repo@$plugin_ref"
          external=$((external + 1))
        else
          echo "⚠️  herdr plugin $plugin_repo@$plugin_ref failed to install (needs network and a build toolchain); re-run to retry."
          skipped=$((skipped + 1))
        fi
      done <"$REPO/herdr/plugins.txt"
    fi
    # Repo-owned plugins (herdr/<dir>/herdr-plugin.toml) are linked, not
    # installed: no network or build, so this runs under --no-external too.
    if command -v herdr >/dev/null 2>&1; then
      herdr_linked="$(herdr plugin list 2>/dev/null || true)"
      for plugin_manifest in "$REPO"/herdr/*/herdr-plugin.toml; do
        [ -f "$plugin_manifest" ] || continue
        plugin_dir="$(dirname "$plugin_manifest")"
        case "$herdr_linked" in *"local:$plugin_dir"*) continue ;; esac
        if herdr plugin link "$plugin_dir" >/dev/null 2>&1; then
          echo "link    herdr/$(basename "$plugin_dir")"
        else
          echo "⚠️  herdr plugin link $plugin_dir failed; re-run to retry."
          skipped=$((skipped + 1))
        fi
      done
    fi
  else
    echo "⚠️  SKIP herdr — no ~/.config/herdr (herdr not run yet). herdr/config.toml and herdr/plugins.txt not applied."
  fi

  # 5d. Claude Code. Only when ~/.claude exists (run `claude` once on a new
  #     machine first); this never creates the directory. See the header for
  #     why settings.json is merged rather than linked.
  if [ -d "$CLAUDE" ]; then
    for claude_file in statusline.sh subagent-statusline.sh claude-powerline.json; do
      link_into "$REPO/claude/$claude_file" "$CLAUDE/$claude_file"
    done

    # Claude's OPENROUTER_API_KEY is the Jev key, JEV_OPENROUTER_API_KEY in
    # ~/.omp/.env (written by `op inject` from omp/overlays/search-keys.tpl).
    # It is kept apart from OMP's own OPENROUTER_API_KEY so Jev compaction is
    # billed to its own OpenRouter key. Without that file the merge still runs
    # and warns, leaving whatever key is already in settings.json.
    # A settings.json Claude Code cannot parse is the operator's to fix; do not
    # abort the rest of the install over it.
    if python3 "$REPO/scripts/apply-json-config.py" \
      "$REPO/claude/settings.json" "$CLAUDE/settings.json" \
      --env-from "$HOME/.omp/.env:JEV_OPENROUTER_API_KEY=OPENROUTER_API_KEY"; then
      echo "merged  claude/settings.json -> $CLAUDE/settings.json"
    else
      echo "⚠️  claude/settings.json not merged into $CLAUDE/settings.json; fix the file and re-run."
      skipped=$((skipped + 1))
    fi

    # Claude Code's own `mcp add-json` owns ~/.claude.json: add only the
    # servers it lacks, never edit one. The snapshot is the declared set.
    if command -v claude >/dev/null 2>&1 && [ -f "$REPO/snapshots/claude/mcp.json" ]; then
      while IFS=$'\t' read -r mcp_name mcp_json; do
        [ -n "$mcp_name" ] || continue
        if claude mcp add-json --scope user "$mcp_name" "$mcp_json" >/dev/null 2>&1; then
          echo "seeded  claude mcp server $mcp_name"
        else
          echo "⚠️  claude mcp add-json $mcp_name failed; re-run to retry."
          skipped=$((skipped + 1))
        fi
      done < <(python3 "$REPO/scripts/seed-mcp-servers.py" missing \
        "$REPO/snapshots/claude/mcp.json" "$HOME/.claude.json")
    fi

    # claude/plugins.txt: `<marketplace repo> <plugin>@<marketplace> <commit>`.
    if [ "$EXTERNAL" = "1" ] && [ -f "$REPO/claude/plugins.txt" ] && command -v claude >/dev/null 2>&1; then
      claude_plugins="$(claude plugin list 2>/dev/null || true)"
      while read -r market_repo plugin_id plugin_commit _; do
        case "$market_repo" in "" | \#*) continue ;; esac
        case "$claude_plugins" in
        *"$plugin_id"*) ;;
        *)
          # Adding a marketplace that is already known is not an error worth
          # stopping for; the install below is what decides success.
          claude plugin marketplace add "$market_repo" >/dev/null 2>&1 || true
          if claude plugin install "$plugin_id" >/dev/null 2>&1; then
            echo "plugin  claude $plugin_id"
            external=$((external + 1))
          else
            echo "⚠️  claude plugin $plugin_id failed to install (needs network); re-run to retry."
            skipped=$((skipped + 1))
            continue
          fi
          ;;
        esac
        python3 "$REPO/scripts/plugin-pin.py" \
          "$CLAUDE/plugins/installed_plugins.json" "$plugin_id" "$plugin_commit"
      done <"$REPO/claude/plugins.txt"
    fi
  else
    echo "⚠️  SKIP claude config — no $CLAUDE (run claude once first). statusline, settings.json, MCP servers and plugins not applied."
  fi

  # 5e. OMP extras: npm plugins, and MCP servers the snapshot names but the
  #     live ~/.omp/agent/mcp.json lacks. OMP owns that file, so existing
  #     servers are never edited and the file is never linked (README "Secrets
  #     policy").
  if [ -d "$OMP" ]; then
    if [ -f "$REPO/snapshots/omp/mcp.json" ]; then
      python3 "$REPO/scripts/seed-mcp-servers.py" merge \
        "$REPO/snapshots/omp/mcp.json" "$OMP/mcp.json"
    fi
    if [ "$EXTERNAL" = "1" ] && [ -f "$REPO/omp/plugins.txt" ] && command -v omp >/dev/null 2>&1; then
      omp_plugins="$(omp plugin list --json 2>/dev/null || true)"
      while read -r omp_plugin omp_plugin_version _; do
        case "$omp_plugin" in "" | \#*) continue ;; esac
        case "$omp_plugins" in *"\"name\": \"$omp_plugin\""*) continue ;; esac
        if omp plugin install "$omp_plugin@$omp_plugin_version" >/dev/null 2>&1; then
          echo "plugin  omp $omp_plugin@$omp_plugin_version"
          external=$((external + 1))
        else
          echo "⚠️  omp plugin $omp_plugin@$omp_plugin_version failed to install (needs network and bun on PATH); re-run to retry."
          skipped=$((skipped + 1))
        fi
      done <"$REPO/omp/plugins.txt"
    fi
    if [ ! -f "$HOME/.omp/.env" ]; then
      echo "note: no ~/.omp/.env — run: op inject -f -i ~/.config/omp/search-keys.tpl -o ~/.omp/.env && chmod 600 ~/.omp/.env, then re-run to push the Jev OpenRouter key into Claude settings."
    fi
  fi
fi

# 6. Git hooks: point git at the tracked .githooks/ instead of .git/hooks, so
#    the pre-commit lint arrives with a clone and works from a worktree (where
#    .git is a file and has no hooks/ directory to write into). Relative on
#    purpose — it resolves per checkout.
if git_without_repo_selectors -C "$REPO" rev-parse --git-dir >/dev/null 2>&1; then
  git_without_repo_selectors -C "$REPO" config core.hooksPath .githooks
  echo "wired   core.hooksPath -> .githooks"
fi

# 7. Prune.
if [ "$PRUNE" = "1" ]; then
  # 7a/7b share the fill gate: a run that declined to fill the shared root
  # does not prune it either.
  if shared_root_consumers_present; then
    # 7a. Shared root: links this repo no longer declares (skill deleted, or an
    #     external allowlist narrowed). Real directories are left alone, so a
    #     hand-installed skill is never deleted.
    for link in "$SKILLS_ROOT"/*; do
      [ -L "$link" ] || continue
      case " $ACTIVE_SKILLS " in
      *" $(basename "$link") "*) continue ;;
      esac
      case "$(readlink "$link")" in
      "$REPO"/* | "$VENDOR"/*)
        rm -f "$link"
        echo "pruned  $(basename "$link") (not declared)"
        pruned=$((pruned + 1))
        ;;
      esac
    done
    # 7b. Shared root: dangling links that point into this repo.
    for link in "$SKILLS_ROOT"/*; do
      [ -L "$link" ] || continue
      case "$(readlink "$link")" in
      "$REPO"/*)
        if [ ! -e "$link" ]; then
          rm -f "$link"
          echo "pruned  $(basename "$link") (dangling)"
          pruned=$((pruned + 1))
        fi
        ;;
      esac
    done
  fi

  # 7c. Claude Code skills root: same two rules as the shared root above —
  #     drop links this repo no longer declares, then dangling links that point
  #     into this checkout. Only symlinks into this repo or vendor/ are ever
  #     removed, so Paseo's real skill directories and any hand-installed or
  #     hand-linked skill survive untouched.
  if [ "$FILL_CLAUDE" = "1" ] && [ -d "$CLAUDE_SKILLS" ]; then
    for link in "$CLAUDE_SKILLS"/*; do
      [ -L "$link" ] || continue
      case " $ACTIVE_SKILLS " in
      *" $(basename "$link") "*) continue ;;
      esac
      case "$(readlink "$link")" in
      "$REPO"/* | "$VENDOR"/*)
        rm -f "$link"
        echo "pruned  $(basename "$link") (not declared)"
        pruned=$((pruned + 1))
        ;;
      esac
    done
    for link in "$CLAUDE_SKILLS"/*; do
      [ -L "$link" ] || continue
      case "$(readlink "$link")" in
      "$REPO"/*)
        if [ ! -e "$link" ]; then
          rm -f "$link"
          echo "pruned  $(basename "$link") (dangling)"
          pruned=$((pruned + 1))
        fi
        ;;
      esac
    done
  fi

  # 7d. Retired harness surfaces. This repo installs Claude Code skills,
  #     agents and config (steps 2b, 2c and 5d), but no Claude instruction file, and
  #     nothing at all for Codex or OpenCode — so clean up what an older version left
  #     behind — but only entries that provably belong to this repo: symlinks
  #     pointing into this checkout (or its vendor/), and copies carrying our
  #     own ownership marker. Anything else is the operator's and is left
  #     exactly as it is.
  display_path() { # display_path <absolute> -> ~-relative for humans
    printf '%s' "${1/#$HOME/~}"
  }
  prune_retired_link() { # prune_retired_link <path> [--warn-real]
    local path="$1" warn_real="${2:-}"
    if [ -L "$path" ]; then
      case "$(readlink "$path")" in
      "$REPO"/* | "$VENDOR"/*)
        rm -f "$path"
        echo "pruned  $(display_path "$path") (retired harness link)"
        pruned=$((pruned + 1))
        ;;
      esac
    elif [ -e "$path" ] && [ "$warn_real" = "--warn-real" ]; then
      echo "⚠️  left alone $(display_path "$path") — unmanaged real file, not created by this repo"
    fi
  }
  prune_retired_copies() { # prune_retired_copies <dir> <reason> — marker-only
    local dir="$1" reason="$2" d
    [ -d "$dir" ] || return 0
    for d in "$dir"/*/; do
      d="${d%/}"
      [ -e "$d/$MARKER" ] || continue
      rm -rf "$d"
      echo "pruned  $(display_path "$d") ($reason)"
      pruned=$((pruned + 1))
    done
  }

  prune_retired_link "$HOME/.claude/CLAUDE.md" --warn-real
  prune_retired_link "$HOME/.codex/AGENTS.md" --warn-real
  prune_retired_link "$HOME/.config/opencode/AGENTS.md" --warn-real

  # ~/.claude/skills is pruned by 7c above. In ~/.claude/agents a link into
  # this checkout survives only while it resolves to a declared
  # claude/agents/*.md; older agent links from elsewhere in the repo go.
  for link in "$HOME"/.claude/agents/*; do
    [ -L "$link" ] || continue
    case "$(readlink "$link")" in
    "$REPO"/claude/agents/*.md) [ -e "$link" ] && continue ;;
    esac
    prune_retired_link "$link"
  done
  for link in "$HOME"/.codex/agents/* "$HOME"/.codex/prompts/*; do
    [ -L "$link" ] || continue
    prune_retired_link "$link"
  done
  # ~/.codex/skills holds copies left by the old mirror; only ours carry the
  # marker, so .system and hand-installed Codex skills are untouched.
  prune_retired_copies "$HOME/.codex/skills" "codex copy, no longer used"

  # 7e. Config links: a repo source that was deleted or renamed leaves a
  #     dangling link in the live config directories. Same ownership rule as
  #     7a/7b: only symlinks into this checkout whose target is gone; real
  #     files and foreign links are never touched. Covers the file, glob and
  #     nested_glob entries of MANAGED_DESTINATIONS in
  #     scripts/ownership_collisions.py (the dangling test is name-agnostic,
  #     so listing the containing directories is enough).
  for link in \
    "$HOME"/.claude/* \
    "$HOME"/.omp/agent/* "$HOME"/.omp/agent/themes/* \
    "$HOME"/.omp/agent/agents/* "$HOME"/.omp/agent/commands/* \
    "$HOME"/.config/omp/* "$HOME"/.config/herdr/* \
    "$HOME"/.pi/agent/* "$HOME"/.pi/agent/prompts/* \
    "$HOME"/.pi/agent/themes/* "$HOME"/.pi/agent/agents/* \
    "$HOME"/.pi/agent/extensions/*/*; do
    [ -L "$link" ] || continue
    case "$(readlink "$link")" in
    "$REPO"/*)
      if [ ! -e "$link" ]; then
        rm -f "$link"
        echo "pruned  $(display_path "$link") (dangling config link)"
        pruned=$((pruned + 1))
      fi
      ;;
    esac
  done
fi

echo "---"
echo "linked=$linked skipped=$skipped external=$external pruned=$pruned"
