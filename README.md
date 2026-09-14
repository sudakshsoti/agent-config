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
  the config OMP actually loads; the overlays below are layered on top of it per
  invocation. Plain OMP uses only `openai-codex` and `opencode-go` providers.
  Symlinked to `~/.omp/agent/config.yml`, so `omp config set` and TUI toggles
  edit the repo copy directly — check `git diff` before committing. Only linked
  if `~/.omp/agent` exists.
- `omp/keybindings.yml`, `omp/lsp.yml`, `omp/themes/*.json`, `omp/agents/*.md` —
  linked individually into `~/.omp/agent/`, so machine-local entries survive.
  `adversary` is the cross-lineage plan reviewer behind `/peer-review`;
  `builder`, `code-worker`, `plan`, `critic`, `research` and `workflow` port
  Pi's roles, with models set in `task.agentModelOverrides`.
- `omp/overlays/*` — model-role overlays symlinked into `~/.config/omp/`.
  `ompgo` loads `go-overlay.yml`; `ompcodex` loads `codex-only-overlay.yml`.
  Both shell functions use `omp --config` for one session without changing the
  base config. `search-keys.tpl` is the 1Password template behind
  `op inject -o ~/.omp/.env` — `op://` references only, never a literal key.
- `pi/settings.json` — Pi's default model, Ctrl+P model list, thinking level,
  theme and package list. Pi's per-job models live in `pi/agents/*.md`
  frontmatter; `pi/model-ladder.md` explains the tiers.
- `pi/verbosity.json`, `pi/pi-fff.json`, `pi/keybindings.json`,
  `pi/subagents.json`, `pi/prompts/`, `pi/themes/`, `pi/agents/`,
  `pi/extensions/` — each linked individually into `~/.pi/agent/`. Extensions
  are linked file by file so local runtime data
  inside the directory survives.
- `pi/web-search.json` — pi-web-access preferences. **Merged**, never linked,
  because the live file is also that extension's credential store.
- `~/.omp/agent/mcp.json` and `~/.pi/agent/auth.json` are **not** tracked here,
  on purpose — see "Secrets policy" below before adding them.
- `scripts/` — installer helpers and the repo's own checks. Not symlinked.

## Day-to-day

```bash
./install.sh             # after adding/renaming a skill — relinks
./install.sh --prune     # after deleting one — also clears dead links
./install.sh --no-external  # skip the external git fetch (offline)
./scripts/check.sh       # run the repo's tests
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
  file itself, and `omp/` is symlinked, so an `omp mcp add` for a server that
  takes an inline `env` API key would write a real credential straight into a
  git-tracked working tree. Its contents also do not transfer between machines:
  the Todoist entry points at a `credentialId` in OMP's own local credential
  store, and the Linear header shells out to a locally-authenticated
  `linear auth token`.
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
