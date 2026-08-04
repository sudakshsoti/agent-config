# agent-config

My agent configuration for [Claude Code](https://code.claude.com/docs) —
skills, subagents, and settings. Private: several skills carry personal
context.

## Quick start (new machine)

```bash
git clone https://github.com/sudakshsoti/agent-config.git ~/dev/agent-config
cd ~/dev/agent-config && ./install.sh
```

## What's included

- `skills/` — Skills for Claude Code and Claude.ai (see `skills/README.md`). Symlinked per skill.
- `agents/` — Subagent definitions (e.g. `design-craft`, `plan-critic`). Symlinked per file.
- `commands/` — Global slash commands (`/recall`, `/remember` for the
  `~/claude-memory` vault). Symlinked per file.
- `settings.json` — Global settings, sanitized, no API keys. Copied if missing.
- `scripts/` — Executables referenced by absolute path from `settings.json` (not
  symlinked). Includes `statusline.sh` / `test-context-size.sh` (the main status
  bar) and `subagent-statusline.sh` / `test-subagent-statusline.sh` (the agent
  panel's per-row status line). See this repo's `CLAUDE.md` for how each works.

## Day-to-day

```bash
./install.sh           # after adding/renaming a skill or agent — relinks
./install.sh --prune   # after deleting one — also clears dead symlinks
./sync.sh              # before committing — refresh the repo copy of
                       # settings.json from ~/.claude (strips API keys)
./scripts/check.sh      # run repo tests plus the live ~/dev instruction audit
```

Skills and agents are **symlinked**, so editing them in this repo is live
immediately — just commit when happy. `settings.json` is a **copy**
(Claude Code rewrites it itself, which would clobber a symlink), hence
`sync.sh`.

## Repository instructions

`config/repository-instructions.json` lists the managed repository roots and
legitimate nested instruction scopes. Shared instructions live in `AGENTS.md`;
the neighbouring regular `CLAUDE.md` starts with `@AGENTS.md` and may contain a
small Claude-only section after that import.

`./scripts/check.sh` audits the live sibling repositories locally. CI runs the
same checker's fixture suite because a GitHub runner does not have the rest of
`~/dev`. Repositories deferred because they had unrelated dirty changes are
listed as `SKIP`, never counted as compliant. To inspect or repair wrappers
directly:

```bash
python3 scripts/check-agent-instructions.py \
  --manifest config/repository-instructions.json --cohort-root ~/dev
python3 scripts/check-agent-instructions.py \
  --manifest config/repository-instructions.json --cohort-root ~/dev --skip-deferred
python3 scripts/repair-agent-instructions.py \
  --manifest config/repository-instructions.json --cohort-root ~/dev
python3 scripts/repair-agent-instructions.py \
  --manifest config/repository-instructions.json --cohort-root ~/dev --apply
```

Repair is a dry-run by default. `--apply` creates or replaces only malformed
`CLAUDE.md` wrappers; it refuses scopes without canonical `AGENTS.md` content
and never edits that content. The manifest limits discovery, so fixtures,
archives, generated distributions, and vendored skill documentation are not
treated as instruction scopes.

## Secrets policy

No secrets in this repo, even though it's private:

- `sync.sh` strips the `env` block from `settings.json` automatically, along
  with any hook commands belonging to other tools (machine state, not
  configuration).
- Machine-local config and API keys belong in `~/.claude/settings.local.json`
  (merged with `settings.json` by Claude Code, never tracked here).
- Never put a token in a `SKILL.md`.

## Related

- [`claude-projects`](https://github.com/sudakshsoti/claude-projects) —
  system prompts for Claude.ai projects (this repo's skills used to live
  there).
- Shell dotfiles are managed separately with chezmoi (`~/dev/dotfiles`).
