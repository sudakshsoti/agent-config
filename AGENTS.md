# AGENTS.md

This is a Codex-specific overlay, not a standalone guide. **Read `CLAUDE.md` in
this directory first** — it is the full, accurate guide to this repo, and it
holds for Codex too except where this file says otherwise. Codex auto-loads
`AGENTS.md` and never reads `CLAUDE.md` on its own, which is the only reason
this file exists.

## What actually reaches Codex

Only skills, and only as symlinks in `~/.agents/skills` (the shared
cross-agent root). Editing a `SKILL.md` in this repo is live for Codex
immediately — no `./install.sh` re-run needed. A re-run is only needed for
adding, renaming, or deleting a skill.

**Never install skills into `~/.codex/skills`.** Codex scans both
`~/.codex/skills` and `~/.agents/skills`, so a skill present in both is listed
twice. That's not cosmetic: Codex caps skills at 2% of context and truncates
every skill's description once that budget fills, so the duplication degrades
discovery across the whole set, not just the doubled skill. `install.sh` step
1b (lines 136-150) actively deletes leftover `~/.codex/skills` copies that
carry the `.agent-config-managed` marker.

Verify with `codex exec "list skill names"` — each name must appear exactly
once.

## No `skillOverrides` in Codex

`skillOverrides` is a Claude Code `settings.json` key; Codex has nothing
equivalent. `~/.codex/config.toml` only has `[plugins.<name>] enabled =
true/false` toggles for plugins, nothing per-skill for filesystem skills.
Consequence: a skill sitting in `skills/` counts against Codex's 2% budget
even if it's switched off for Claude via `skillOverrides`.

## Claude-only — do not edit these as Codex

`agents/`, `settings.json`, `claude-powerline.json`, `hooks/`, `plugins.txt`,
`dist/`. These configure Claude Code specifically (subagents, its settings
file, its statusline, its hooks, its plugin list, its skill zips) and Codex
has no equivalent for any of them.
