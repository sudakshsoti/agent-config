# Archived skills

Skills kept here for reference. They are **not installed to any surface** —
`install.sh` and `scripts/build-zip.sh` both glob `skills/*/` and require a
`SKILL.md` at that level, so this directory (which has none) is skipped and the
nested `skills/_archive/<name>/SKILL.md` files are never matched.

Why they were retired: each was already switched off for Claude via
`skillOverrides: "off"` in `settings.json`, but Codex has no per-skill
equivalent — `~/.codex/config.toml` only carries `[plugins.<name>] enabled`
toggles. So they still loaded on Codex and ate its skills context budget (capped
at 2% of context, after which every skill's description gets truncated) for zero
benefit.

To restore one: `git mv skills/_archive/<name> skills/<name>`, then run
`./install.sh` from the real checkout. Re-run `./scripts/build-zip.sh <name>` if
it needs a `dist/` zip again.
