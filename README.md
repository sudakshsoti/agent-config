# agent-config

My agent configuration for **OMP** and **Pi** — shared skills, per-harness
settings, subagents, prompts, themes and model routing. Private: several skills
carry personal context.

## Quick start (new machine)

```bash
git clone https://github.com/sudakshsoti/agent-config.git ~/dev/agent-config
cd ~/dev/agent-config && ./install.sh
```

## What's included

Three destinations, and nothing else.

- `skills/` — repo-owned skills, **source only** (see `skills/README.md`). Each
  one is symlinked once into `~/.agents/skills`, the shared root that both OMP
  and Pi discover, so a skill is linked once rather than once per harness.
- `plugins.txt` — third-party skill sources that this repo does *not* vendor.
  Each `external <owner/repo>[:<subdir>] [skill ...]` line is cloned into
  `vendor/<owner>-<repo>/` (gitignored) and its skills are linked into the same
  shared root; a repo-owned skill always wins a name collision. Naming skills
  after the directive links only those. Externals are vendored by reference, so
  their files never enter this repo's history and `scripts/lint-skills.py` does
  not apply to them. Re-running `./install.sh` fast-forwards each clone.
- `global-agents.md` — harness-neutral shared preferences. Linked to
  `~/.omp/agent/AGENTS.md` and `~/.pi/agent/AGENTS.md`. Named differently from
  this repo's root `AGENTS.md` because that file is the project instructions
  for this checkout only.
- `omp/config.yml` — OMP's baseline settings: model roles (`default` plus the
  per-task worker roles), thinking level, statusline and task options. This is
  the config OMP actually loads. Plain OMP runs Claude 5 models from `anthropic`
  plus `xai-oauth` (SuperGrok) for cross-lineage review, research and discovery;
  `openai-codex`, `opencode-go` and `muse-code` are disabled.
  Symlinked to `~/.omp/agent/config.yml`, so `omp config set` and TUI toggles
  edit the repo copy directly — check `git diff` before committing. Only linked
  if `~/.omp/agent` exists.
- `omp/keybindings.yml`, `omp/lsp.yml`, `omp/themes/*.json`, `omp/agents/*.md` —
  linked individually into `~/.omp/agent/`, so machine-local entries survive.
  `adversary` is the cross-lineage plan reviewer behind `/peer-review`;
  `builder`, `code-worker`, `plan`, `critic`, `research` and `workflow` port
  Pi's roles, with models set in `task.agentModelOverrides`.
- `omp/overlays/*` — holds only `search-keys.tpl`, symlinked file by file
  into `~/.config/omp/`. It is the 1Password template behind
  `op inject -o ~/.omp/.env` — `op://` references only, never a literal key.
- `pi/settings.json` — Pi's default model, Ctrl+P model list, thinking level,
  theme and package list. Pi's per-job models live in `pi/agents/*.md`
  frontmatter; `pi/model-ladder.md` explains the tiers.
- `pi/verbosity.json`, `pi/pi-fff.json`, `pi/keybindings.json`,
  `pi/workflows/model-tiers.json` (into `~/.pi/workflows/`), `pi/prompts/`, `pi/themes/`, `pi/agents/`,
  `pi/extensions/` — each linked individually into `~/.pi/agent/`. Extensions
  are linked file by file so local runtime data
  inside the directory survives.
- `pi/web-search.json` — pi-web-access preferences. **Merged**, never linked,
  because the live file is also that extension's credential store.
- `~/.pi/agent/auth.json` is **not** tracked here, on purpose — see "Secrets
  policy" below before adding anything like it.
- `claude/` — Claude Code: `statusline.sh`, `subagent-statusline.sh` and
  `claude-powerline.json` are linked into `~/.claude/`; `settings.json` is
  **merged** (Claude Code and herdr write the live file, and it holds
  `OPENROUTER_API_KEY`, which install copies from `JEV_OPENROUTER_API_KEY` in
  `~/.omp/.env` rather than tracking it); `plugins.txt` pins the
  `claude-compact-openrouter` plugin.
  `omp/plugins.txt` does the same for OMP npm plugins. On a new box: log in
  (`claude`, `omp`), `op inject` the `.env`, run `./install.sh`.
- `snapshots/` — machine-local harness config **copied**, never linked:
  `~/.omp/agent/mcp.json` and Claude Code's user-scope `mcpServers`. A copy is
  what keeps the mcp.json leak path closed; install seeds missing servers from
  it and never edits an existing one. Refresh with
  `./scripts/snapshot-machine-config.sh`; see `snapshots/README.md`.
- `scripts/` — installer helpers and the repo's own checks, including
  `check-model-routing.py`, which fails the build on model-routing drift
  between `omp/config.yml`, `omp/agents/`, `omp/overlays/` and Pi's config.
  Not symlinked.

## Day-to-day

```bash
./install.sh             # after adding/renaming a skill — relinks
./install.sh --prune     # after deleting one — also clears dead links
./install.sh --no-external  # skip the external git fetch (offline)
./scripts/check.sh       # run the repo's tests
./scripts/snapshot-machine-config.sh  # after changing an MCP server
```

Everything is **symlinked**, so editing a skill, agent, prompt or setting in
this repo is live immediately — just commit when happy.

OMP and Pi both rewrite some of their own config, and because those files are
symlinks the writes land here. That is deliberate: there is no sync step, and a
setting changed in a TUI shows up as a plain `git diff` to review before
committing. The mirror-image hazard is that an unreviewed write can be committed
by accident, so check `git diff` before committing after changing a setting
interactively.

## Secrets policy

No secrets in this repo, even though it's private. Never put a token, API key or
auth store in a `SKILL.md` or any tracked file.

These stay machine-local and untracked. Do not "helpfully" add them:

- **`~/.omp/agent/mcp.json` is a live leak path with no guard.** OMP writes that
  file itself, so if `omp/` held a symlink to it, an `omp mcp add` for a server
  that takes an inline `env` API key would write a real credential straight into
  a git-tracked working tree. Its contents also do not transfer between
  machines: the Todoist entry points at a `credentialId` in OMP's own local
  credential store, and the Linear header shells out to a locally-authenticated
  `linear auth token`.

  It is **snapshotted** to `snapshots/omp/mcp.json` — copied, not linked. That
  is the distinction that matters: a copy is inert, so nothing OMP writes
  reaches the tree on its own, and `scripts/snapshot-machine-config.sh` refuses
  any file carrying an `env`, `headers` or token-shaped value under
  `mcpServers`. Never symlink this file. Claude Code's `mcpServers` are
  snapshotted the same way and for a second reason: they live inside
  `~/.claude.json` next to `userID`, `machineID` and `oauthAccount`, so the file
  itself can never be tracked.
- **`~/.pi/agent/auth.json`** holds OAuth tokens and provider API keys.
- **`~/.pi/agent/models-store.json`** is a refetchable provider catalog cache.
- **`~/.omp/agent/extensions/`** is written and overwritten by the tool that
  installs it; tracking it would launder someone else's executable code as
  reviewed config.

`./install.sh --prune` never touches any of these. It only removes symlinks that
point into this checkout and copies carrying this repo's own ownership marker,
and it leaves unmarked real files alone with a warning.

## Related

- [`claude-projects`](https://github.com/sudakshsoti/claude-projects) —
  system prompts for Claude.ai projects (this repo's skills used to live there).
- [`dotfiles`](https://github.com/sudakshsoti/dotfiles) — the machine: shell,
  chezmoi, launchers, Docker sandbox tooling and secrets.
