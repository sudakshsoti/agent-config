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
# holds no secrets — see the OMP steps below):
#   omp/config.yml -> ~/.omp/agent/config.yml
#     OMP's model roles, thinking level, statusline and task settings. Changing
#     a setting from the OMP TUI edits the repo copy directly; review with
#     `git diff` before committing.
#   omp/lsp.yml -> ~/.omp/agent/lsp.yml
#   omp/themes/*.json -> ~/.omp/agent/themes/*.json
#   omp/overlays/* -> ~/.config/omp/*
#     Model-role overlays read by ~/.local/bin/omp-{go,codex}-overlay and the
#     ompgo/ompcodex zsh wrappers. Linked file by file so .active-overlay —
#     runtime state owned by those scripts — is left alone.
#     Tracked themes are linked individually; other live theme files remain
#     machine-local. Only linked if ~/.omp/agent exists.
#   pi/settings.json -> ~/.pi/agent/settings.json
#     pi's default model, Ctrl+P model list, thinking level, theme and package
#     list. pi rewrites this file itself (`pi install`, `/settings`), and the
#     write follows the symlink into the repo — review with `git diff` before
#     committing, same as omp/config.yml.
#   pi/subagents.json -> ~/.pi/agent/subagents.json
#   pi/themes/*.json -> ~/.pi/agent/themes/*.json
#   pi/agents/*.md -> ~/.pi/agent/agents/*.md
#     Custom pi-subagents definitions. Only linked if ~/.pi/agent exists.

#
# Deliberately NOT tracked or linked (machine-local by design):
#   ~/.omp/agent/mcp.json — see the "Secrets policy" section of README.md.
#   ~/.pi/agent/auth.json — OAuth tokens and provider API keys.
#   ~/.pi/agent/models-store.json — a refetchable provider catalog cache.
#   ~/.pi/agent/skills/ — pi already discovers ~/.agents/skills, which step 2
#     fills. Linking here too means every skill is discovered twice.
#   ~/.omp/agent/extensions/ — written and overwritten by the tool that owns it.
#   ~/.omp/agent/models.yml — nothing to link. Step 3i used to install an
#     `ollama-local` provider here for session titles; removed 2026-08-29 when
#     the Ollama desktop app went away. See docs/2026-08-29-model-roles-post-codex.md.
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
# External skill sources (also declared in plugins.txt, as `external` lines):
#   external <owner/repo>[:<subdir>] [skill ...] -> git clone/pull into
#   vendor/<owner>-<repo>/ (gitignored), then symlink its skills (all of them,
#   or only the named ones) into ~/.claude/skills AND ~/.agents/skills,
#   naming each by its frontmatter `name:`, not its directory. The optional
#   :<subdir> pins which tree to read when a repo ships several copies.
#   exactly like a repo-owned skill. This is the ONLY way a third-party skill set
#   reaches Codex, opencode and omp: a Claude *plugin* is visible to Claude alone,
#   and many skill repos (emilkowalski/skills among them) ship no
#   .claude-plugin/marketplace.json, so they cannot be installed as plugins at all.
#   Vendored-by-reference, not copied: upstream files never enter this repo's
#   history, skip scripts/lint-skills.py and need no dist/<name>.zip.
#   A repo-owned skills/<name> always wins a name collision.
#
# Idempotent; safe to re-run. Run once after cloning on a new machine.
#
#   ./install.sh                  # link skills+agents (Claude + shared ~/.agents), copy settings if absent, sync plugins
#   ./install.sh --prune          # also remove dangling symlinks for deleted skills/agents
#   ./install.sh --no-plugins     # skip the `claude plugin` sync + external git fetches
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENDOR="$REPO/vendor"
CLAUDE="$HOME/.claude"
CODEX="$HOME/.codex"
OMP="$HOME/.omp/agent"
OPENCODE="$HOME/.config/opencode"
PI="$HOME/.pi/agent"
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
# ephemeral git worktree pins every ~/.claude
# skill+agent link to a path that vanishes when the worktree is cleaned up —
# silently breaking the whole personal skill set. Refuse unless --force.
case "$REPO" in
  */.git/worktrees/* | */worktrees/*)
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

mkdir -p "$CLAUDE/skills" "$CLAUDE/agents"
# Mirror skills into the shared ~/.agents/skills root, but only if Codex is
# actually installed (its own dir already exists) — never create ~/.agents on a
# Claude-only box. Codex scans BOTH ~/.codex/skills and ~/.agents/skills, so
# installing into both roots makes every skill appear twice; we use only the
# shared one. See the mirror note in CLAUDE.md.
AGENTS_SKILLS=""
[ -d "$CODEX" ] && AGENTS_SKILLS="$HOME/.agents/skills"
[ -n "$AGENTS_SKILLS" ] && mkdir -p "$AGENTS_SKILLS"
MARKER=".agent-config-managed"
linked=0 skipped=0 copied=0 mirrored=0 pruned=0 plugins=0 external=0

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

# 1c. External skill sources: `external <owner/repo>` lines in plugins.txt.
#     Cloned into vendor/<owner>-<repo>/ (gitignored) and symlinked into the
#     SAME two roots as repo-owned skills, so Codex, opencode and omp see them
#     too. A Claude plugin cannot do this — plugins are visible to Claude alone,
#     and a repo without .claude-plugin/marketplace.json is not installable as a
#     plugin in the first place. Fetching honours --no-plugins (it is the same
#     network step); relinking always runs, so an offline re-run still repairs
#     the symlinks from what is already cloned.
if [ -f "$REPO/plugins.txt" ]; then
  while read -r kind arg rest; do
    [ "$kind" = "external" ] || continue
    case "$arg" in
      */*) : ;;
      *) echo "⚠️  plugins.txt: external '$arg' is not owner/repo — skipped"; skipped=$((skipped + 1)); continue ;;
    esac
    # `owner/repo[:subdir]` — the optional subdir pins which tree to read when a
    # repo ships several (charleswiltgen/axiom carries one per agent flavour,
    # plus the .claude-plugin one, all with the same skill names).
    repo="${arg%%:*}"
    subdir=""
    case "$arg" in *:*) subdir="${arg#*:}" ;; esac
    slug="${repo%/*}-${repo#*/}"
    clone="$VENDOR/$slug"

    if [ "$PLUGINS" = "1" ]; then
      if [ -d "$clone/.git" ]; then
        if git -C "$clone" pull --ff-only --quiet 2>/dev/null; then
          echo "pulled  $repo (vendor/$slug)"
        else
          echo "⚠️  could not fast-forward vendor/$slug — using the checkout as-is"
        fi
      else
        mkdir -p "$VENDOR"
        if git clone --depth 1 --quiet "https://github.com/$repo.git" "$clone" 2>/dev/null; then
          echo "cloned  $repo -> vendor/$slug"
        else
          echo "⚠️  FAILED to clone $repo"
          skipped=$((skipped + 1))
          continue
        fi
      fi
    fi

    if [ ! -d "$clone" ]; then
      echo "⚠️  SKIP external $repo — vendor/$slug is absent (re-run without --no-plugins)"
      skipped=$((skipped + 1))
      continue
    fi

    # An optional space-separated skill list after the source narrows what gets
    # linked. Empty means every skill found — right for a small, curated repo,
    # wrong for a grab bag where the extras are dead weight in Codex's 2% budget.
    want="$rest"

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
    # ehmo/platform-design-skills ships skills/macos/ declaring
    # `name: macos-design-guidelines`, and linking it as "macos" installs a
    # skill whose directory and manifest disagree.
    skill_name() { # skill_name <dir-with-SKILL.md>
      local n
      n="$(sed -n '/^---$/,/^---$/{s/^name:[[:space:]]*//p;}' "$1/SKILL.md" 2>/dev/null | head -1)"
      n="${n%\"}"; n="${n#\"}"; n="${n%\'}"; n="${n#\'}"
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
      link_into "$dir" "$CLAUDE/skills/$name"
      [ -n "$AGENTS_SKILLS" ] && mirror_into "$dir" "$AGENTS_SKILLS/$name"
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
  done < "$REPO/plugins.txt"
fi

# 2. Agents: every markdown file in agents/
for file in "$REPO"/agents/*.md; do
  [ -f "$file" ] || continue
  link_into "$file" "$CLAUDE/agents/$(basename "$file")"
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

# 3b2. Global agent preferences: symlinked for the same reason as
#     claude-powerline.json above — none of these tools rewrite this file, so a
#     repo edit goes live immediately with nothing to sync back. Named
#     global-agents.md in the repo since the repo's own root AGENTS.md (the
#     project-instructions file for this checkout) already owns that name.
#     Linked into every installed tool's user-level instruction path so a
#     gotcha or preference added once reaches all of them.
link_into "$REPO/global-agents.md" "$CLAUDE/CLAUDE.md"
[ -d "$CODEX" ] && link_into "$REPO/global-agents.md" "$CODEX/AGENTS.md"
[ -d "$OMP" ] && link_into "$REPO/global-agents.md" "$OMP/AGENTS.md"
[ -d "$OPENCODE" ] && link_into "$REPO/global-agents.md" "$OPENCODE/AGENTS.md"
[ -d "$PI" ] && link_into "$REPO/global-agents.md" "$PI/AGENTS.md"

# 3c. Codex config: merge only the non-secret keys tracked in codex/config.toml.
#     Preserve unrelated user, MCP, desktop, and machine-managed settings.
if [ -d "$CODEX" ] && [ -f "$REPO/codex/config.toml" ]; then
  python3 "$REPO/scripts/apply-codex-config.py" \
    "$REPO/codex/config.toml" "$CODEX/config.toml"
  echo "merged  codex/config.toml"
fi

# 3e/3f/3g/3h only run when OMP is installed. Say so out loud when it isn't —
#     a silent no-op makes a verify of the form `./install.sh && readlink
#     ~/.omp/agent/config.yml` look like it passed on a machine that never got
#     the links. 3j is separate: it links into ~/dev repos, not ~/.omp.
if [ ! -d "$OMP" ]; then
  echo "⚠️  SKIP omp — no $OMP (OMP not installed). config.yml, lsp.yml, themes/ and agents/ not linked."
fi

# 3e. OMP config: symlinked, unlike codex/config.toml above. OMP *does* rewrite
#     this file (`omp config set`, and TUI toggles), and a write follows the
#     symlink and lands in the repo, carrying no credentials (OMP keeps auth in
#     its own state dir, not here). So the repo stays the live source of truth
#     and settings changed from the TUI show up as a plain `git diff` to review
#     before committing, with no sync step.
#
#     CORRECTION 2026-08-29: an earlier version of this comment claimed
#     "nothing is reordered or dropped". That is FALSE for comments. A fully
#     annotated modelRoles/retry block written by hand was replaced during a
#     single session by a value-identical version with every `#` line gone.
#     Values survived exactly; the rationale did not. So do NOT keep decision
#     rationale in this file — it belongs in docs/, and the model-role
#     reasoning lives in docs/2026-08-29-model-roles-post-codex.md.
#
#     Caveat: OMP locks the *resolved* path, so writes leave an empty
#     omp/config.yml.lock in the checkout — .gitignore covers it.
if [ -d "$OMP" ] && [ -f "$REPO/omp/config.yml" ]; then
  mkdir -p "$OMP"
  link_into "$REPO/omp/config.yml" "$OMP/config.yml"
fi
# 3f. OMP themes: tracked files are symlinked individually so machine-local
#     themes already present in ~/.omp/agent/themes remain untouched.
if [ -d "$OMP" ] && [ -d "$REPO/omp/themes" ]; then
  mkdir -p "$OMP/themes"
  for theme_file in "$REPO"/omp/themes/*.json; do
    [ -f "$theme_file" ] || continue
    link_into "$theme_file" "$OMP/themes/$(basename "$theme_file")"
  done
fi

# 3i. OMP overlays: the per-invocation and sticky model-role overlays that
#     ~/.local/bin/omp-{go,codex}-overlay and the zsh wrappers read from
#     ~/.config/omp/. They live here rather than in dotfiles because they are
#     model routing — the same subject as omp/config.yml — and splitting one
#     decision across two repos is what made "which repo owns this?" unanswerable.
#     Linked individually so ~/.config/omp/.active-overlay, which is runtime
#     state written by the overlay scripts, is never touched.
#
#     Note: the scripts that CONSUME these (~/.local/bin/omp-*-overlay) are
#     machine tooling and stay in dotfiles, as does the ~/.zshrc that defines
#     ompgo/ompcodex. They read a fixed ~/.config/omp path, so the split works
#     without either side knowing about the other.
if [ -d "$REPO/omp/overlays" ]; then
  mkdir -p "$HOME/.config/omp"
  for overlay in "$REPO"/omp/overlays/*; do
    [ -f "$overlay" ] || continue
    link_into "$overlay" "$HOME/.config/omp/$(basename "$overlay")"
  done
fi

# 3g. OMP LSP preferences: partial overrides of OMP's built-in server
#     definitions. The server binaries are machine dependencies; OMP activates
#     each one only when its root markers match the current working directory.
if [ -d "$OMP" ] && [ -f "$REPO/omp/lsp.yml" ]; then
  mkdir -p "$OMP"
  link_into "$REPO/omp/lsp.yml" "$OMP/lsp.yml"
fi

# 3h. OMP subagents: symlinked the same way. `adversary` is the cross-lineage
#     plan reviewer — it pins `model: "@adversary"`, so it follows the role in
#     omp/config.yml and can never resolve to an Anthropic model.
if [ -d "$OMP" ] && [ -d "$REPO/omp/agents" ]; then
  mkdir -p "$OMP/agents"
  for a in "$REPO"/omp/agents/*.md; do
    link_into "$a" "$OMP/agents/$(basename "$a")"
  done
fi

# 3k. pi config: symlinked, same reasoning as 3e for omp. pi rewrites
#     settings.json itself (`pi install`, `/settings`, the theme picker), and a
#     write follows the symlink into the repo, so the repo stays the live source
#     and TUI changes show up as a plain `git diff` with no sync step. pi keeps
#     credentials in ~/.pi/agent/auth.json, never in settings.json.
#
#     NOT linked, deliberately: auth.json (OAuth tokens and API keys),
#     models-store.json (a refetchable catalog cache), sessions/ and npm/
#     (runtime state and installed package trees).
#
#     NOT linked either: ~/.pi/agent/skills/. pi's own discovery list already
#     names ~/.agents/skills, which step 2 fills. A per-skill link here would be
#     discovered twice — the exact mistake baseline made and that AGENTS.md
#     warns about.
if [ ! -d "$PI" ]; then
  echo "⚠️  SKIP pi — no $PI (pi not installed). settings.json, subagents.json, themes/ and agents/ not linked."
fi
if [ -d "$PI" ] && [ -f "$REPO/pi/settings.json" ]; then
  link_into "$REPO/pi/settings.json" "$PI/settings.json"
fi
# 3l. pi-subagents settings: widget and FleetView off. Global scope only — the
#     /agents menu writes to <cwd>/.pi/subagents.json, never to this file, so a
#     project override never lands in the repo by accident.
if [ -d "$PI" ] && [ -f "$REPO/pi/subagents.json" ]; then
  link_into "$REPO/pi/subagents.json" "$PI/subagents.json"
fi
# 3m. pi themes: linked individually so machine-local themes already in
#     ~/.pi/agent/themes survive, and so theme packages that generate a theme
#     into that directory are never clobbered.
if [ -d "$PI" ] && [ -d "$REPO/pi/themes" ]; then
  mkdir -p "$PI/themes"
  for theme_file in "$REPO"/pi/themes/*.json; do
    [ -f "$theme_file" ] || continue
    link_into "$theme_file" "$PI/themes/$(basename "$theme_file")"
  done
fi
# 3n. pi subagents: custom agent definitions read by @tintinweb/pi-subagents.
#     `scout` exists to stop delegated lookups inheriting the session model —
#     it pins its own, per the "always pass an explicit model tier" rule in
#     global-agents.md.
if [ -d "$PI" ] && [ -d "$REPO/pi/agents" ]; then
  mkdir -p "$PI/agents"
  for a in "$REPO"/pi/agents/*.md; do
    [ -f "$a" ] || continue
    link_into "$a" "$PI/agents/$(basename "$a")"
  done
fi

# 3j. RETIRED 2026-08-29. Symlinked omp/projects/<repo>.config.yml into
#     ~/dev/<repo>/.omp/config.yml to keep `muse-spark-1.2-contributor` — the
#     one Go model that trains on prompts — out of OQGA and clinical-reasoning.
#     Removed when Muse Spark was accepted everywhere; see
#     docs/2026-08-29-model-roles-post-codex.md.

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
        external) continue ;;    # handled in step 1c, alongside the skills
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
        *) echo "⚠️  plugins.txt: unknown directive '$kind' (expected marketplace|plugin|external)" ;;
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
echo "linked=$linked mirrored=$mirrored skipped=$skipped copied=$copied plugins=$plugins external=$external pruned=$pruned"
