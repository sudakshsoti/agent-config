# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Personal Claude Code configuration — skills, subagents, and settings — version-controlled here and wired into `~/.claude` by `install.sh`. Mostly there is no build, lint, or test step; "developing" here means editing skills/agents and committing. Several skills carry personal context, hence the repo is private.

The exception is the handful of executable files — `hooks/` and the statusline widget under `scripts/`. Those are the only things here that can be *wrong* rather than merely badly worded, and they all fail silently on purpose (a hook must never block a prompt, a status line must never print a traceback), so a broken one looks exactly like a quiet one. `./scripts/test-ctx-flag.sh` covers that pair, plus the statusline layout's own command string; run it after touching any of the three.

## The install/sync model (the one non-obvious thing)

Two different mechanisms, chosen per file type — get this wrong and you either lose live edits or clobber Claude Code's own writes:

- **Skills and agents are symlinked into `~/.claude`** (`skills/<name>/` → `~/.claude/skills/<name>`, `agents/<name>.md` → `~/.claude/agents/<name>.md`). For Claude the repo is the live source of truth — editing a `SKILL.md` here takes effect immediately; just commit when happy. Agents are Claude-only and are not mirrored.
- **Skills are also mirrored into `~/.codex/skills` as copies** (not symlinks) when Codex is installed, so a `/<name>` slash command works in both surfaces from one source. Codex's skill scanner **ignores symlinked directories** — a symlinked skill silently never appears in Codex — so the mirror must be a real copy. The trade-off: a Codex copy is a snapshot, so **editing a `SKILL.md` does NOT reach Codex until you re-run `./install.sh`** (Claude still updates live). Each copy carries a `.agent-config-managed` marker so `--prune` can remove copies of deleted skills without touching `~/.codex/skills/.system` or hand-installed Codex skills.
- **Grok Build needs no mirror step at all.** It reads `~/.claude/skills/` directly (same priority tier as its own `~/.grok/skills/`, per `grok inspect`) and follows the symlinks fine — so anything linked for Claude shows up in Grok automatically, live, the moment `install.sh` runs. No separate copy, no separate re-sync on edits.
- **`global-CLAUDE.md` is symlinked to `~/.claude/CLAUDE.md`** — the user-level memory file loaded in every project, regardless of cwd. Symlinked rather than copied because Claude Code only ever _appends_ to it (the `#` quick-capture shortcut), and an append writes through to the target. It is the one file here whose audience is Claude in _other_ repos, so keep it to standing habits that hold everywhere; project facts belong in that project's own `CLAUDE.md`. Note the tiers are **concatenated, not overridden** — a rule here that a project might contradict must defer explicitly, or the conflict resolves arbitrarily. Do not confuse it with this repo's own `CLAUDE.md`, which is about maintaining this repo.
- **`settings.json` is a copy**, not a symlink, because Claude Code rewrites it itself (via `/config` etc.) and would clobber a symlink. `install.sh` copies it only if missing (never overwrites). `sync.sh` pulls the live version back into the repo before committing.
- **`ccstatusline-settings.json` is a copy too**, and for the same reason: it is the statusline layout, installed to `~/.config/ccstatusline/settings.json`, and the `ccstatusline` TUI rewrites that file in place. Copy-if-missing on install, pulled back by `sync.sh`. The statusline binary itself is a global npm package (`npm i -g ccstatusline`), not a plugin, so `settings.json` just invokes `ccstatusline`. To change the layout, run `ccstatusline` for its TUI, then `./sync.sh`; or edit the repo copy and run `./install.sh --force-statusline` to push it out live (plain `install.sh` won't touch the live file once it exists). Widget `type` ids and their `metadata` options are not documented upstream — read them off `src/widgets/` in `sirmalloc/ccstatusline`, or probe by rendering: `CCSTATUSLINE_WIDTH=150 ccstatusline --config <file> < <sample-status.json>` (or use `./scripts/preview-statusline.sh [width] [config]` for the same thing with less typing). `type` is a plain string, not an enum — a wrong widget id fails silently, rendering nothing, so probing by rendering is the only real check. A `separator` scans backward only, hiding when everything before it is empty; one that *leads* a hideable group can never collapse with it — the collapsing separator always goes after the group, never before.
- **Anything on the status line that depends on a _value_ needs a `custom-command` widget.** ccstatusline has no conditional or threshold colouring at all — its gradients are positional, painted across a widget's own characters, never mapped to the number. So a widget that must change with what it reports has to shell out. Line 2's `ctx` label is the one instance: `scripts/ctx-flag.py`, wired in with `preserveColors: true` (the flag that stops ccstatusline stripping the script's own ANSI). Its threshold and token-counting live in `hooks/context_size.py`, shared with the `context-budget.py` hook so the line and the hook can never disagree. Two constraints on any script wired in this way: it must exit 0 and print nothing on error (ccstatusline renders the failure into the status line itself — `[Exit: N]` for a non-zero exit, so an uncaught Python traceback shows as `[Exit: 1]`, plus `[Cmd not found]`, `[Permission denied]` and `[Error]` for the rest), and it must finish inside 1000ms or the line shows `[Timeout]`. Do not set `maxWidth` on a `preserveColors` widget — the truncation counts raw string length and will cut mid-escape-sequence. Because a command failure renders straight into the line, `commandPath` itself now carries a `|| printf` fallback so an unrunnable script degrades to the plain label instead of `[Exit: N]` — the sharp edge is that a fallback indistinguishable from success can't be seen failing, so `./scripts/test-ctx-flag.sh`'s layout tests are what actually catches it going stale.
- **Plugins are declared in `plugins.txt`, never vendored.** Each line is a marketplace (`anthropics/claude-plugins-official`, etc.) or a `plugin@marketplace`; `install.sh` replays them through the `claude plugin` CLI (`marketplace add` / `install`), which is idempotent and pulls the **latest** version. The plugin _content_ lives under `~/.claude/plugins/` (untracked, auto-updated upstream) — the repo tracks only _which_ plugins, so a fresh machine reproduces the set. This is why "update superpowers" is not a repo edit: it's a plugin that auto-updates from its marketplace. Sync step is skipped if `claude` isn't on PATH, or with `--no-plugins`. To add/remove a plugin, edit `plugins.txt` and re-run `./install.sh`.

```bash
./install.sh                    # link skills/agents into ~/.claude, copy skills into Codex, copy settings if absent, sync plugins. Idempotent.
./install.sh --prune            # also remove dangling Claude symlinks + orphaned Codex copies for deleted skills/agents
./install.sh --no-plugins       # skip the `claude plugin` sync step (e.g. offline, or claude not on PATH)
./install.sh --force-statusline # overwrite the live ccstatusline settings.json from the repo copy, even if it already exists
./sync.sh                       # before committing settings changes — refresh repo copies from ~/.claude and ~/.config/ccstatusline
```

Run `./install.sh` after adding, renaming, **or editing** a skill if you want the change in Codex (Claude picks up edits live; Codex needs the re-copy). Use `--prune` after deletes. `install.sh` skips (with a warning) any `~/.claude` path that holds a real non-symlink entry, or any `~/.codex/skills` entry that isn't a marked copy — move it aside first.

**Gotcha — moving/renaming this checkout breaks the Claude symlinks** (they bake in the absolute repo path). After moving the repo, `cd` into the new location and re-run `./install.sh` to re-point everything.

That now applies to the live statusline too, and it is the worse half: `ccstatusline-settings.json` holds a `commandPath` with this checkout's absolute path baked in, and it is a **copy**, so `install.sh` alone will not fix it — you need `./install.sh --force-statusline`. The failure used to be quiet; now it is invisible: `commandPath`'s `|| printf` fallback means a moved checkout renders a normal-looking grey `ctx` instead of erroring, so `CLEAR` silently never fires again at any context size, with nothing on the line to notice. `./scripts/test-ctx-flag.sh`'s three layout tests, which run that exact commandPath, are the only thing left that catches it.

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

## Distributable zips

`dist/<skill-name>.zip` — one zip per skill, committed to the repo — is the upload artifact for claude.ai and the Claude API, which install a skill from a zip rather than a symlink. Built by `./scripts/build-zip.sh` (all skills) or `./scripts/build-zip.sh <name>` (one skill); each archive holds a single top-level `<name>/` folder with `SKILL.md` at its root, which is what claude.ai expects.

These zips are snapshots, not symlinks — **editing a `SKILL.md` does not update its zip.** After adding, renaming, or editing a skill, re-run `./scripts/build-zip.sh` and commit the changed `dist/*.zip` files alongside the skill edit, or the committed zip silently drifts from the source.

## Authoring agents

Subagents are single markdown files in `agents/` with frontmatter: `name`, `description`, optional `tools` (comma-separated allowlist) and `model`. Invoked explicitly with `@<name>` or proactively per the description.
