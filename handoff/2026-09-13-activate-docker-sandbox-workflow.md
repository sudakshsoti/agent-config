# Activate Docker Sandbox workflow handoff

Date: 2026-09-13
Current agent-config worktree: `/Users/sudakshsoti/worktrees/agent-config/crisp-feral-lynx`
Branch: `crisp-feral-lynx`

## Goal

Keep the existing `pi`, `omp`, `ompgo`, and `ompcodex` development workflow, but route those commands through one persistent Docker Sandbox per canonical repository under `~/dev`. The owner wants the remaining mechanical setup handled first and will complete Pi authentication/setup afterward.

## What changed

### Canonical dotfiles

Canonical `/Users/sudakshsoti/dev/dotfiles` now has a completed, committed checkpoint-enabled launcher:

- `81ed6a5` — `feat: add docker sandbox agent launcher`
- `a0446a5` — `feat: checkpoint repositories before sandbox access`

Commit `a0446a5` changed:

- `private_dot_local/bin/executable_agent-sandbox`
- `tests/test-agent-sandbox.py`
- `dot_zshrc.tmpl`
- `docs/agent-sandbox-trial.md`

The launcher now creates a mandatory host-side repository checkpoint before `sbx create` or `sbx exec` for `run` and `shell`. Checkpoints include the complete repository directory, including `.git`, dirty tracked work, ignored files, and untracked files. On macOS it requires an APFS repository and a same-filesystem checkpoint base, uses `/bin/cp -a -c`, stages atomically, verifies that the source did not change during the copy, and keeps eight valid snapshots by default. It refuses external hard links, unsafe/symlinked checkpoint paths, invalid retention settings, traversal failures, copy failures, and non-private pre-existing checkpoint bases. Retention deletes only recognized direct-child checkpoints; foreign, corrupt, symlinked, and partial entries are preserved.

The zsh integration adds `agent-checkpoints`; the trial documentation now covers checkpoint behavior, manual recovery even when the Git checkout is damaged, retention, stale checkpoint directories after repository renames, and the limits of local snapshots.

Focused verification passed in canonical dotfiles:

- `python3 -B tests/test-agent-sandbox.py` — 18 passed
- `bash -n private_dot_local/bin/executable_agent-sandbox`
- `shellcheck -S warning private_dot_local/bin/executable_agent-sandbox`
- `git diff --check`
- rendered `~/.zshrc` checked with `zsh -n`
- rendered launcher checked with `bash -n`
- chezmoi source-to-target mapping confirmed
- targeted `chezmoi diff` completed without applying anything
- Python and Markdown LSP diagnostics were clean

Canonical dotfiles is clean at `a0446a5`. Nothing was pushed in this session.

### Canonical agent-config

The seven tested Docker Sandbox safety commits were fast-forwarded from `crisp-feral-lynx` into canonical `/Users/sudakshsoti/dev/agent-config` main:

- `fa971819` — Pi and OMP catastrophe guards
- `f80bb0b8`, `d5f89479` — guard contract coverage/cleanup
- `79a086de` — immutable sandbox bootstrap bundle
- `febd4c9b`, `026b2726`, `cf7de7cf` — bundle replacement and fixture hardening

Canonical `~/dev/agent-config` is clean at `cf7de7cf`; `origin/main` remains at `4d49eef6`, so these commits have not been pushed.

Focused canonical verification passed:

- `node scripts/test-catastrophe-guard.mjs` — 71 passed
- `python3 -B scripts/test-build-agent-sandbox-bundle.py` — 16 passed
- `python3 -B scripts/test-omp-catastrophe-policy.py` — 5 passed

`./scripts/check.sh` was then started. It passed the skill-frontmatter stage (one existing non-fatal size warning), distribution zip checks, several Python suites, design contract checks, the OMP policy tests, and the 71-case catastrophe guard. The command was interrupted by the wrap request after printing four more passing dots, so it did **not** reach a confirmed clean completion and must be rerun from the beginning.

## Decisions and why

- Never mount all of `~/dev`; one sandbox gets one canonical repository mount. There is no Time Machine recovery layer.
- Direct read-write mounts remain the convenience choice, but every sandbox entry is gated by a complete host checkpoint outside `~/dev`.
- External hard links are refused because they let a sandbox mutate host files outside the mounted repository.
- SSH-agent forwarding stays disabled and sandbox MCP configuration must remain empty.
- Development ports are published only on `127.0.0.1` with TCP/IPv4.
- Host auth stores are not copied into sandboxes. The owner will complete Pi setup/authentication after the mechanical setup is ready.
- Ordinary commands must not silently fall back to host execution; explicit `pi-host` and `omp-host` remain the escape hatches.
- No live dotfiles should be applied and no real project sandbox should be created until canonical agent-config's full check completes successfully.

## Current state

### Canonical repositories

- `/Users/sudakshsoti/dev/dotfiles`: clean at `a0446a5`.
- `/Users/sudakshsoti/dev/agent-config`: clean at `cf7de7cf`; full `scripts/check.sh` verification is incomplete because it was interrupted.
- Neither repository was pushed.

### Current agent-config worktree

The current worktree still has unrelated/uncommitted state that was deliberately not discarded:

- Modified: `.pi/subagents.json` (appeared after the earlier handoff; inspect before deciding whether it is runtime drift or intentional)
- Modified formatter-style drift: `omp/config.yml`, `pi/extensions/catastrophe-guard/index.js`, `sandbox/bootstrap/install.sh`, `scripts/build-agent-sandbox-bundle.sh`, `scripts/test-catastrophe-guard.mjs`
- Staged added handoff: `handoff/2026-09-13-docker-sandbox-trial.md`
- This handoff is staged as `handoff/2026-09-13-activate-docker-sandbox-workflow.md`
- Untracked preserved docs: `docs/agent-sandbox-guide.html`, `docs/guardrails-pi-omp-catastrophic-actions.md`, `docs/plan-docker-sandbox-agent-workflow.md`
- `.playwright-cli/` contains generated browser QA artifacts and can be removed later; do not remove the documentation files with it.

The formatter drift and documentation are not needed for canonical activation and were not included in the seven safety commits.

### Live workflow

- No live dotfiles were applied.
- The immutable bootstrap bundle was not prepared in the live user data directory.
- No persistent real-project sandbox was created.
- Pi/OMP sandbox authentication was not attempted.
- Ordinary shell `pi`/`omp` commands still use the existing host workflow.

Open execution state:

- Verify canonical agent-config: in progress, blocked only by rerunning `./scripts/check.sh` to completion.
- Install launcher and wrappers with targeted chezmoi apply: pending.
- Prepare the immutable bundle and run `agent-sandbox doctor`: pending.
- Create/authenticate a pilot sandbox: intentionally left for the owner after setup.

## Single next action

From clean canonical `/Users/sudakshsoti/dev/agent-config`, rerun `./scripts/check.sh` from the beginning and require a complete zero-exit result. Do not apply live dotfiles, prepare the live bundle, or create a real sandbox until that command finishes successfully.
