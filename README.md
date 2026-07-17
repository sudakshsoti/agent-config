# agent-config

My agent configuration for [Claude Code](https://code.claude.com/docs) —
skills, subagents, settings, and statusline. Private: several skills carry
personal context.

## Quick start (new machine)

```bash
git clone https://github.com/sudakshsoti/agent-config.git ~/dev/agent-config
cd ~/dev/agent-config && ./install.sh
```

## What's included

- `skills/` — Skills for Claude Code and Claude.ai (see `skills/README.md`). Symlinked per skill.
- `agents/` — Subagent definitions (`design-craft`). Symlinked per file.
- `settings.json` — Global settings, sanitized, no API keys. Copied if missing.
- `statusline.sh` — Minimal custom statusline (context bar + model). Copied if missing.
- `claude-powerline.json` — Config for the claude-powerline statusline. Copied if missing.

## Day-to-day

```bash
./install.sh           # after adding/renaming a skill or agent — relinks
./install.sh --prune   # after deleting one — also clears dead symlinks
./sync.sh              # before committing — refresh repo copies of the
                       # settings files from ~/.claude (strips API keys)
```

Skills and agents are **symlinked**, so editing them in this repo is live
immediately — just commit when happy. The settings files are **copies**
(Claude Code rewrites `settings.json` itself, which would clobber a
symlink), hence `sync.sh`.

## Secrets policy

No secrets in this repo, even though it's private:

- `sync.sh` strips the `env` block from `settings.json` automatically.
- Machine-local config and API keys belong in `~/.claude/settings.local.json`
  (merged with `settings.json` by Claude Code, never tracked here).
- Never put a token in a `SKILL.md`.

## Related

- [`claude-projects`](https://github.com/sudakshsoti/claude-projects) —
  system prompts for Claude.ai projects (this repo's skills used to live
  there).
- Shell dotfiles are managed separately with chezmoi (`~/dev/dotfiles`).
