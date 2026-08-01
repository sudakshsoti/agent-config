# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Personal Claude Code configuration — skills, subagents, and settings — version-controlled here and wired into `~/.claude` by `install.sh`. Mostly there is no build, lint, or test step; "developing" here means editing skills/agents and committing. Several skills carry personal context, hence the repo is private.

The exception is the executable files under `hooks/`. Those are the only things here that can be *wrong* rather than merely badly worded, and they all fail silently on purpose (a hook must never block a prompt), so a broken one looks exactly like a quiet one. `./scripts/test-context-size.sh` covers the context pair: `hooks/context-budget.py`, and the `hooks/context_size.py` it imports `THRESHOLD` and `measure` from. Run it after touching either. The statusline is no longer on this list; it is a third-party binary reading a declarative JSON config, so it can be misconfigured but nothing in this repo can break it.

`hooks/memory-consolidate.py` is the sharpest of them, because it has *side effects* — at `SessionEnd` it spawns a detached `claude -p` run that can write and commit in `~/dev/claude-memory`. It never blocks (SessionEnd cannot block anything anyway), exits 0 and prints nothing on every path, and gates on a deliberately dumb transcript-size heuristic; the actual "is any of this worth keeping" judgement is the headless model's, not Python's. Two things will bite you: the recursion guard (that spawned run ends in a `SessionEnd` of its own, held off by the `CLAUDE_MEMORY_CONSOLIDATE` env marker plus the `prompt_input_exit` reason), and the machine-wide `/tmp/claude-memory-consolidate.lock` that makes two sessions ending together produce one write rather than two. `./scripts/test-memory-consolidate.sh` covers all of it against a stubbed `claude` binary and a throwaway vault — it never exercises a real headless call, so that boundary stays unproven by tests. Its log is `/tmp/claude-memory-consolidate.log`, which is the only place a failure is ever visible.

## The install/sync model (the one non-obvious thing)

Two different mechanisms, chosen per file type — get this wrong and you either lose live edits or clobber Claude Code's own writes:

- **Skills and agents are symlinked into `~/.claude`** (`skills/<name>/` → `~/.claude/skills/<name>`, `agents/<name>.md` → `~/.claude/agents/<name>.md`). For Claude the repo is the live source of truth — editing a `SKILL.md` here takes effect immediately; just commit when happy. Agents are Claude-only and are not mirrored.
- **Skills are also symlinked into `~/.agents/skills`** (the shared cross-agent root) when Codex is installed, so a `/<name>` slash command works in both surfaces from one source, live — editing a `SKILL.md` reaches Codex immediately, same as Claude. **Codex scans two roots — `~/.codex/skills` AND `~/.agents/skills` — so a skill installed into both is listed TWICE.** That is not cosmetic: Codex caps skills at 2% of context and starts truncating every skill's description when the budget fills, so duplication silently degrades discovery across the whole set. Install into the shared root only. (Verify with `codex exec "list skill names starting with design-"` — each name must appear once.)
  - Until 2026-07-30 this mirror was a **copy** into `~/.codex/skills`, on the premise that Codex's scanner ignored symlinked directories. That is no longer true as of codex-cli 0.145 — it follows them fine — and the copy was the cause of the double-listing, since something (the `skills` CLI, on 9 Jul) had separately linked the same skills into `~/.agents/skills`. `install.sh` step 1b now deletes any leftover `~/.codex/skills` copy carrying the `.agent-config-managed` marker, unconditionally rather than under `--prune`, because leaving one is an active bug rather than mere staleness. The marker is what keeps it off `~/.codex/skills/.system` and hand-installed Codex skills.
- **Grok Build needs no mirror step at all.** It reads `~/.claude/skills/` directly (same priority tier as its own `~/.grok/skills/`, per `grok inspect`) and follows the symlinks fine — so anything linked for Claude shows up in Grok automatically, live, the moment `install.sh` runs. No separate copy, no separate re-sync on edits.
- **`global-CLAUDE.md` is symlinked to `~/.claude/CLAUDE.md`** — the user-level memory file loaded in every project, regardless of cwd. Symlinked rather than copied because Claude Code only ever _appends_ to it (the `#` quick-capture shortcut), and an append writes through to the target. It is the one file here whose audience is Claude in _other_ repos, so keep it to standing habits that hold everywhere; project facts belong in that project's own `CLAUDE.md`. Note the tiers are **concatenated, not overridden** — a rule here that a project might contradict must defer explicitly, or the conflict resolves arbitrarily. Do not confuse it with this repo's own `CLAUDE.md`, which is about maintaining this repo.
- **`settings.json` is a copy**, not a symlink, because Claude Code rewrites it itself (via `/config` etc.) and would clobber a symlink. `install.sh` copies it only if missing (never overwrites). `sync.sh` pulls the live version back into the repo before committing.
- **The active statusline (as of 2026-07-31) is `claude-powerline`** (`npm i -g @owloops/claude-powerline`, v1.29.0 at time of writing). Installed separately; `install.sh` does not install the binary, only wires its config. `settings.json`'s `statusLine.command` is `claude-powerline --style=powerline`; that flag duplicates `display.style` in the config and is kept only as a fallback for the case where the config fails to load. **`claude-powerline.json` is symlinked, not copy-if-missing**, which is the one entry where the copy rule above flips. The reason: the binary only ever *reads* its config (`readFileSync`, and nothing else writes it), and there is no companion TUI that rewrites it in place, so the hazard that forces `settings.json` to be a copy simply does not exist here. Consequence: a repo edit is live immediately, and `sync.sh` has nothing to pull back.
  - Config search order, first hit wins: `--config` / `$CLAUDE_POWERLINE_CONFIG`, then `<projectDir>/.claude-powerline.json`, `$PWD/.claude-powerline.json`, `~/.claude/claude-powerline.json`, `~/.config/claude-powerline/config.json`. Worth knowing, because a stray `.claude-powerline.json` in a project directory silently wins over the global one.
  - Segments are configured under `display.lines[].segments` (16 names available), and `style` must be nested under `display`; a top-level `style` is ignored. `charset: "unicode"` and the powerline separators need a Nerd Font, with `"text"` as the ASCII fallback. The `block` and `weekly` segments read Claude Code's native `rate_limits` payload and render nothing without it.
  - `modelContextLimits.opus` is deliberately `1000000`, not the upstream 200000 default, to match the 1M-context Opus in use. At the default the context segment reads about 5x high, so do not "fix" it back.
  - Upstream also ships a `/powerline` slash command that writes `~/.claude/claude-powerline.json`. Because the target is a symlink, that writes straight through into the repo and turns up in `git diff`. Wanted behaviour, but surprising the first time.
  - Rollback is git history only, since both old config files are deleted. `backups/statusLine-block-backup-2026-07-31.json` holds the outgoing `ccline` statusLine block, and `backups/ccstatusline-settings.live-backup-2026-07-27.json` still holds the older ccstatusline layout.
- **Plugins are declared in `plugins.txt`, never vendored.** Each line is a marketplace (`anthropics/claude-plugins-official`, etc.) or a `plugin@marketplace`; `install.sh` replays them through the `claude plugin` CLI (`marketplace add` / `install`), which is idempotent and pulls the **latest** version. The plugin _content_ lives under `~/.claude/plugins/` (untracked, auto-updated upstream) — the repo tracks only _which_ plugins, so a fresh machine reproduces the set. This is why "update superpowers" is not a repo edit: it's a plugin that auto-updates from its marketplace. Sync step is skipped if `claude` isn't on PATH, or with `--no-plugins`. To add/remove a plugin, edit `plugins.txt` and re-run `./install.sh`.

```bash
./install.sh              # link skills/agents/commands/hooks + claude-powerline.json into ~/.claude and ~/.agents/skills, copy settings if absent, sync plugins. Idempotent.
./install.sh --prune      # also remove dangling symlinks (both roots) for deleted skills/agents
./install.sh --no-plugins # skip the `claude plugin` sync step (e.g. offline, or claude not on PATH)
./install.sh --force      # install anyway from a path that looks like an ephemeral worktree, which is otherwise refused
./sync.sh                 # before committing settings changes: refresh the repo's settings.json from ~/.claude (the only copy left)
```

Run `./install.sh` after adding or renaming a skill. **Editing** one needs no re-run on any surface now that both roots are symlinks. Use `--prune` after deletes. `install.sh` skips (with a warning) any `~/.claude` or `~/.agents/skills` path holding a real non-symlink entry it did not create — move it aside first.

**Gotcha — moving/renaming this checkout breaks the symlinks in both roots** (`~/.claude` and `~/.agents/skills` bake in the absolute repo path). After moving the repo, `cd` into the new location and re-run `./install.sh` to re-point everything. The statusline needs no special case: `claude-powerline.json` holds no absolute paths of its own, and being a symlink it gets re-pointed by that same plain `./install.sh` like everything else.

## Secrets policy

No secrets in git, even though the repo is private:

- `sync.sh` strips the `env` block from `settings.json` (`jq 'del(.env)'`) on the way in. API keys live in `~/.claude/settings.local.json`, which Claude Code merges at runtime and which is never tracked here.
- **Never put a token in a `SKILL.md`** — it commits in plaintext. (One historically leaked in the related `claude-projects` repo's git history.)

## Authoring skills

Each skill is a directory under `skills/` with a required `SKILL.md` (YAML frontmatter + instructions) and optional `references/`, `scripts/`, `assets/` subdirs. Conventions enforced by `skills/README.md`:

- Frontmatter requires `name` (≤64 chars, `[a-z0-9-]`, **must equal the directory name** — rename both together) and `description` (≤1024 chars). `user-invocable: true` makes it a `/<name>` slash command.
- **`description` is the only text always in context** — it is the discovery surface. Triggers (the phrases/situations that should fire the skill) belong here. If a skill isn't triggering, sharpen the description, not the body.
- Keep the `SKILL.md` body under ~5k tokens. Push bulk (long protocols, schemas, reference tables) into `references/foo.md` and link by relative path — it loads only on demand.
- `scripts/` are invoked via bash from within the skill; reference them by their installed path (`.claude/skills/<name>/scripts/<script>`), since that's where the symlink puts them.

Same format works on Claude Code, Claude.ai (zip upload), and the Claude API — but skills do **not** sync between surfaces; install each separately. See `skills/README.md` for per-surface install details.

## Distributable zips

`dist/<skill-name>.zip` — one zip per skill, committed to the repo — is the upload artifact for claude.ai and the Claude API, which install a skill from a zip rather than a symlink. Built by `./scripts/build-zip.sh` (all skills) or `./scripts/build-zip.sh <name>` (one skill); each archive holds a single top-level `<name>/` folder with `SKILL.md` at its root, which is what claude.ai expects.

These zips are snapshots, not symlinks — **editing a `SKILL.md` does not update its zip.** After adding, renaming, or editing a skill, re-run `./scripts/build-zip.sh` and commit the changed `dist/*.zip` files alongside the skill edit, or the committed zip silently drifts from the source.

## Authoring agents

Subagents are single markdown files in `agents/` with frontmatter: `name`, `description`, optional `tools` (comma-separated allowlist) and `model`. Invoked explicitly with `@<name>` or proactively per the description.
