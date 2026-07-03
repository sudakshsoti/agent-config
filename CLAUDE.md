# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Personal Claude Code configuration — skills, subagents, settings, and statusline — version-controlled here and wired into `~/.claude` by `install.sh`. There is no build, lint, or test step; "developing" here means editing skills/agents and committing. Several skills carry personal context, hence the repo is private.

## The install/sync model (the one non-obvious thing)

Two different mechanisms, chosen per file type — get this wrong and you either lose live edits or clobber Claude Code's own writes:

- **Skills and agents are symlinked into `~/.claude`** (`skills/<name>/` → `~/.claude/skills/<name>`, `agents/<name>.md` → `~/.claude/agents/<name>.md`). For Claude the repo is the live source of truth — editing a `SKILL.md` here takes effect immediately; just commit when happy. Agents are Claude-only and are not mirrored.
- **Skills are also mirrored into `~/.codex/skills` as copies** (not symlinks) when Codex is installed, so a `/<name>` slash command works in both surfaces from one source. Codex's skill scanner **ignores symlinked directories** — a symlinked skill silently never appears in Codex — so the mirror must be a real copy. The trade-off: a Codex copy is a snapshot, so **editing a `SKILL.md` does NOT reach Codex until you re-run `./install.sh`** (Claude still updates live). Each copy carries a `.agent-config-managed` marker so `--prune` can remove copies of deleted skills without touching `~/.codex/skills/.system` or hand-installed Codex skills.
- **`settings.json`, `statusline.sh`, `claude-powerline.json` are copies**, not symlinks, because Claude Code rewrites `settings.json` itself (via `/config` etc.) and would clobber a symlink. `install.sh` copies them only if missing (never overwrites). `sync.sh` pulls live versions back into the repo before committing.
- **Plugins are declared in `plugins.txt`, never vendored.** Each line is a marketplace (`anthropics/claude-plugins-official`, etc.) or a `plugin@marketplace`; `install.sh` replays them through the `claude plugin` CLI (`marketplace add` / `install`), which is idempotent and pulls the **latest** version. The plugin *content* lives under `~/.claude/plugins/` (untracked, auto-updated upstream) — the repo tracks only *which* plugins, so a fresh machine reproduces the set. This is why "update superpowers" is not a repo edit: it's a plugin that auto-updates from its marketplace. Sync step is skipped if `claude` isn't on PATH, or with `--no-plugins`. To add/remove a plugin, edit `plugins.txt` and re-run `./install.sh`.

```bash
./install.sh              # link skills/agents into ~/.claude, copy skills into Codex, copy settings if absent, sync plugins. Idempotent.
./install.sh --prune      # also remove dangling Claude symlinks + orphaned Codex copies for deleted skills/agents
./install.sh --no-plugins # skip the `claude plugin` sync step (e.g. offline, or claude not on PATH)
./sync.sh                 # before committing settings changes — refresh repo copies from ~/.claude
```

Run `./install.sh` after adding, renaming, **or editing** a skill if you want the change in Codex (Claude picks up edits live; Codex needs the re-copy). Use `--prune` after deletes. `install.sh` skips (with a warning) any `~/.claude` path that holds a real non-symlink entry, or any `~/.codex/skills` entry that isn't a marked copy — move it aside first.

**Gotcha — moving/renaming this checkout breaks the Claude symlinks** (they bake in the absolute repo path). After moving the repo, `cd` into the new location and re-run `./install.sh` to re-point everything.

## Secrets policy

No secrets in git, even though the repo is private:

- `sync.sh` strips the `env` block from `settings.json` (`jq 'del(.env)'`) on the way in. API keys live in `~/.claude/settings.local.json`, which Claude Code merges at runtime and which is never tracked here.
- **Never put a token in a `SKILL.md`** — it commits in plaintext. (One historically leaked in the related `claude-projects` repo's git history.)

## Authoring skills

Each skill is a directory under `skills/` with a required `SKILL.md` (YAML frontmatter + instructions) and optional `references/`, `scripts/`, `assets/` subdirs. Conventions enforced by `skills/README.md`:

- Frontmatter requires `name` (≤64 chars, `[a-z0-9-]`, **must equal the directory name** — rename both together) and `description` (≤1024 chars). `user-invocable: true` makes it a `/<name>` slash command.
- **`description` is the only text always in context** — it is the discovery surface. Triggers (the phrases/situations that should fire the skill) belong here. If a skill isn't triggering, sharpen the description, not the body.
- Keep the `SKILL.md` body under ~5k tokens. Push bulk (long protocols, schemas, reference tables) into `references/foo.md` and link by relative path — it loads only on demand.
- `scripts/` are invoked via bash from within the skill; reference them by their installed path (e.g. `.claude/skills/gtd/scripts/state.sh`), since that's where the symlink puts them.

Same format works on Claude Code, Claude.ai (zip upload), and the Claude API — but skills do **not** sync between surfaces; install each separately. See `skills/README.md` for per-surface install details.

## Authoring agents

Subagents are single markdown files in `agents/` with frontmatter: `name`, `description`, optional `tools` (comma-separated allowlist) and `model`. Invoked explicitly with `@<name>` or proactively per the description.
