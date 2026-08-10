# Handoff — Apply agent-config to the homelab box

Date: 2026-08-10
Repo: `~/dev/agent-config` (`/home/sudaksh/dev/agent-config`), branch `main`, clean and in sync with `origin/main`.

## Context

Running **on the homelab box itself** as `sudaksh`. The box had been provisioned
long ago **as `root` from `/root/dev/agent-config`**. After the `sudaksh` user
migration the repo moved to `/home/sudaksh/dev/agent-config`, so every
`~/.claude` config symlink was left dangling at the dead `/root/dev/...` path and
the Claude Code plugin state was pinned to `/root` paths. Task was to re-apply the
config from the new location so the box matches the Mac's committed config.

## What changed and where

All changes are to `~/.claude` / `~/.agents` / Claude Code plugin state — **no
tracked repo files changed** (repo tree is clean; the only repo-level side effect
was `git config core.hooksPath .githooks`, local git config).

- **`./install.sh --prune`** re-linked everything from the new path:
  - 35 skills → `~/.claude/skills` + mirrored to `~/.agents/skills` (Codex).
    `skills/_archive/` is correctly excluded (no `SKILL.md`) — 35 is the full set.
  - 2 agents (`frontend-craft`, `plan-critic`), 2 commands (`/recall`,
    `/remember`), 4 hooks re-linked.
  - `codex/config.toml` merged; `core.hooksPath` wired to `.githooks`.
- **Manual cleanup of 12 stale links** the prune step could not catch: its prune
  only matches links whose target starts with the *current* `$REPO`, but the
  dead links pointed at the old `/root/dev/agent-config/...` path. Removed 11
  skill links (clinical-reasoning, composition-patterns, cross-post, design-craft,
  explain-this, gtd, homelab-triage, reading-companion, torbox-ops, value-connect,
  web-design-guidelines) + 1 agent link (design-craft.md) — all for skills since
  deleted from the repo. **Zero dangling links remain anywhere.**
- **Plugins repaired.** `known_marketplaces.json` had `installLocation` at
  `/root/...`, so every plugin showed `failed to load: cache-miss`.
  `claude plugin marketplace update` rewrote all paths to `/home/sudaksh/...`;
  then reinstalled `frontend-design`, `claude-code-setup`, `humanizer`.
  Final: `frontend-design`, `vercel`, `claude-code-setup`, `humanizer`,
  `i-have-adhd` **enabled** (matches `plugins.txt`); `superpowers` **disabled**
  (manifest deliberately excludes it — vendored skills + costly SessionStart hook;
  the path fix had revived it). No `plugin uninstall` in the CLI, so superpowers
  stays recorded-but-disabled rather than fully removed.
- **`~/.claude/claude-powerline.json` converted to a symlink** → repo copy.
  Live file backed up to `~/.claude/claude-powerline.json.bak-20260810-165103`.
  Note: this was a real behaviour change, not a cosmetic sync — the box's live
  config was a hand-tuned `style:"tui"` layout (theme dark, opus context 200K);
  the repo/Mac version is `style:"minimal"` (theme custom, opus 1M). The box
  statusline now matches the Mac. Backup restores the old TUI layout if wanted.

## Decisions and why

- **Did not clobber `~/.claude/CLAUDE.md`** — it is the box's on-box homelab
  rules (a real file, starts `# YOU ARE RUNNING ON THE HOMELAB SERVER ITSELF`).
  `install.sh` skips it by design (real file, not a symlink); `global-CLAUDE.md`
  was removed from the repo anyway, so nothing tried to overwrite it. Left as-is.
- **`settings.json` not copied** — already present; `install.sh` only copies when
  missing. Posture check passed ("not permissive"). Left as-is.
- **Disabled rather than removed superpowers** — no CLI uninstall exists; disable
  stops its SessionStart hook, which is the entire reason `plugins.txt` excludes it.

## Follow-up session, same day — the statusline was still not applied

The section above was wrong to call the statusline done. Symlinking
`claude-powerline.json` set up the *config* but never the *command*: the live
`settings.json` still had `statusLine.command = "ccline"` (a different tool at
`/usr/bin/ccline`), so the powerline config was dead — nothing read it.
`install.sh` cannot fix this by design, since it only copies `settings.json`
when the file is missing, and it was not.

Fixed by patching `~/.claude/settings.json` in place (backup:
`settings.json.bak-20260810-195844`):

- `statusLine` and `subagentStatusLine` now point at the repo's scripts, with
  the tracked `/Users/sudakshsoti/...` prefix rewritten to `/home/sudaksh/...`.
  The tracked value is a macOS absolute path, so it can never be copied to this
  box verbatim — any future re-apply has to relocate it too.
- `permissions.allow` +17, `skillOverrides` +42, `tui: fullscreen`, and the
  `trim-tool-output.py` PostToolUse hook wired.

Deliberately **not** applied, each for a reason:

- `cbm-code-discovery-gate` and `cbm-session-reminder` — referenced by the
  tracked `settings.json` but absent from the repo's `hooks/` directory. They
  are Mac-local files; wiring them here would create broken hook references.
- `autoMode.environment` — the tracked copy describes the Mac ("a personal
  Mac", "SSH into it"). The live copy is the box-specific rewrite ("runs
  directly on the homelab box", "no SSH hop needed"). Overwriting it would
  mislead every future session on this box.
- `model: sonnet` and `effortLevel: medium` — user chose to stay on Opus 5 and
  effort `high`. The tracked `sonnet` pin is a Mac-side cost choice.
- Machine-local hooks (supacode, superset, herdr) left intact. `sync.sh` treats
  other tools' hooks as machine state, so a wholesale copy would break them.

## Current state

Verified: `install.sh --prune` re-runs clean (44 linked, 35 skills mirrored, 0
pruned, 0 dangling). The `SKIP CLAUDE.md` warning is expected — that file is the
box's on-box homelab rules, and `global-CLAUDE.md` was removed from the repo in
`a0e1df5`.

## Known fragility

`scripts/statusline.sh` invokes `claude-powerline` bare, and on this box the
binary exists only at `~/.nvm/versions/node/<version>/bin/`. It resolves because
Claude Code inherits the interactive `PATH`, but under a clean environment the
wrapper renders **empty** rather than degrading: its fallback prints `$raw`,
which is unassigned when the `claude-powerline` call fails. A Node version bump
would blank the statusline silently. Fix by hardening the wrapper or pinning a
stable symlink at `/usr/local/bin/claude-powerline`.

## Single next action

None required. Optionally harden the wrapper against the `PATH` fragility above.
If the old TUI layout is ever preferred, restore
`~/.claude/claude-powerline.json.bak-20260810-165103` over the symlink and set
`statusLine.command` back to `ccline`.
