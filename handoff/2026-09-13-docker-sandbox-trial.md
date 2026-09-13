# Docker Sandbox trial handoff

Date: 2026-09-13.
Current agent-config worktree: `/Users/sudakshsoti/worktrees/agent-config/crisp-feral-lynx`.
Branch: `crisp-feral-lynx`.
Status: the safety foundations and documentation exist, but the convenience checkpoint launcher is half-done and the live workflow is not activated.

## Goal and decisions

The goal is a convenient, reversible trial in which normal `pi`, `omp`, `ompgo`, and `ompcodex` commands run inside Docker Sandboxes rather than directly on the Mac.

The owner does not have Time Machine and does not plan to configure it. The resulting decisions are:

- Never mount all of `~/dev` into one sandbox. That would expose every repository to one destructive or confidentiality failure with no whole-machine recovery layer.
- Use one persistent sandbox per canonical repository strictly inside `~/dev`.
- Use a direct read-write repository mount for convenience, not clone mode. Changes therefore write through to the host repository.
- Before any agent or sandbox shell can touch that mount, create a mandatory host-side repository checkpoint outside `~/dev`; fail closed if checkpointing or containment validation fails.
- Checkpoints must include `.git`, uncommitted work, ignored files, and untracked files. On macOS they should use APFS clone copies on the same filesystem, be written atomically, and retain eight valid snapshots by default.
- Detect and refuse repository files with hard links outside the repository because direct mounting would otherwise let the sandbox alter an external host file.
- Keep SSH-agent forwarding disabled. Do not allow host-side stdio MCP servers or repository lifecycle commands to escape the VM boundary.
- Publish development ports only on host loopback. Run the dev server in the sandbox on `0.0.0.0`, then use normal host Chrome at `127.0.0.1`. Do not expose the personal Chrome profile or personal 1Password extension to the agent.
- Keep ordinary commands fail-closed: there is no automatic host fallback. Explicit `pi-host` and `omp-host` commands remain available when the owner deliberately wants host execution.
- Authentication must be verified with real requests before the pilot starts. Persisted host auth stores must not be broadly mounted. Any 1Password access should eventually use a least-privilege service account and subprocess-lifetime injection.

## What changed

### Docker Sandboxes host runtime

Docker Sandboxes CLI and daemon `0.42.1` were installed and authenticated. `sbx diagnose` passed all 12 checks. The balanced network policy was initialized.

`ssh.agentForwardingEnabled` was changed from `true` to `false`, the daemon was restarted, and the setting was verified. Disposable tests verified direct write-through, outside-home containment, persistence, loopback-only port publication, closed stdin, and zero sandbox MCP servers. A hard-link escape was demonstrated, which is why the launcher must refuse external hard links.

### Agent-config safety branch

The current worktree contains seven commits above `main`:

- `fa971819` — Pi and OMP catastrophe guards.
- `f80bb0b8` and `d5f89479` — focused guard test cleanup and coverage.
- `79a086de` — immutable sandbox bootstrap bundle.
- `febd4c9b`, `026b2726`, and `cf7de7cf` — bundle replacement and fixture hardening.

Relevant locations:

- `pi/extensions/catastrophe-guard/`
- `omp/overlays/sandbox.yml`
- `scripts/test-catastrophe-guard.mjs`
- `sandbox/bootstrap/`
- `scripts/build-agent-sandbox-bundle.sh`
- `scripts/test-build-agent-sandbox-bundle.py`

The Pi guard passed 71 focused cases. The bundle builder passed 16 focused tests. The full `scripts/check.sh` suite passed all 9 checks when those commits were completed.

The immutable bundle exports only allowlisted files from committed Git `HEAD`, defaults to `~/.local/share/agent-sandbox/bootstrap`, rejects output under `~/dev`, verifies checksums, and excludes credentials and runtime auth/session state. Its installer expects separately installed Pi `0.85.1` and OMP `18.1.19` unless run with `--config-only`.

These commits have not been merged into canonical `/Users/sudakshsoti/dev/agent-config`, whose `main` remains at `4d49eef6`.

### Dotfiles launcher

Canonical `/Users/sudakshsoti/dev/dotfiles` has committed baseline launcher commit:

- `81ed6a5` — `feat: add docker sandbox agent launcher`

It changes:

- `private_dot_local/bin/executable_agent-sandbox`
- `dot_zshrc.tmpl`
- `docs/agent-sandbox-trial.md`
- `tests/test-agent-sandbox.py`
- `.chezmoiignore`

The committed launcher maps each canonical repository strictly inside `~/dev` to its own direct sandbox, rejects `~/dev` itself and escaping Git worktrees, never silently falls back to host agents, and exposes only loopback TCP/IPv4 ports. It provides prepare, doctor, shell, status, stop, reset, port, and unport operations plus the Pi/OMP wrappers. Thirteen fake-`sbx` contract tests and shell, shellcheck, chezmoi targeting, and diff checks passed for that baseline.

### HTML guide

A detailed standalone owner guide was created at:

- `docs/agent-sandbox-guide.html`

It explains the architecture, current activation status, daily workflow, commands, web development and Chrome, credentials, checkpoints, limitations, recovery, troubleshooting, rollback, and glossary in simple terms. It includes a boundary explorer and copyable commands.

The guide was visually tested at 390×844 and 1440×1000. The design audit reported 0 failures and 0 warnings at both sizes; keyboard selection and copy feedback worked; the final browser console had zero errors; HTML diagnostics were clean; and the fresh-context critic verdict was `ship` after a mobile diagram panning cue was added.

The guide is still untracked in this worktree.

### Planning documents

These are also present and untracked under `docs/`:

- `docs/guardrails-pi-omp-catastrophic-actions.md`
- `docs/plan-docker-sandbox-agent-workflow.md`

The plan was revised after self-review and cross-lineage adversarial review. It passed Marksman, lens diagnostics, and `git diff --check` when finalized.

## Current dirty and half-done state

### Current agent-config worktree

`git status --short` before this handoff showed:

- Modified: `omp/config.yml`
- Modified: `pi/extensions/catastrophe-guard/index.js`
- Modified: `sandbox/bootstrap/install.sh`
- Modified: `scripts/build-agent-sandbox-bundle.sh`
- Modified: `scripts/test-catastrophe-guard.mjs`
- Untracked: `docs/`
- Untracked: `.playwright-cli/`

The five tracked modifications appear to be formatter-only drift left in the working tree after the commits; inspect before either reverting or preserving them. `.playwright-cli/` contains generated browser QA snapshots and can be removed. Do not accidentally discard the three untracked documentation files.

This handoff file is newly added and uncommitted.

### Canonical dotfiles repository

`/Users/sudakshsoti/dev/dotfiles` is dirty only at:

- `private_dot_local/bin/executable_agent-sandbox`

That uncommitted diff is the incomplete checkpoint implementation: roughly 578 added lines. It currently adds a `checkpoints` command and a Python-stdlib checkpoint engine with atomic staging, APFS clone-copy support, hard-link detection, metadata, safe retention, and fail-closed path checks. Standalone fixture measurements were about 0.45 seconds for 2,000 files plus 8 MiB.

It is not ready to commit or activate. Missing work includes integrating and reviewing the launcher flow end to end, adding isolated contract tests for checkpoint creation/refusal/retention/recovery behavior, updating the zsh helper and owner trial documentation as needed, and running the full narrow verification suite. Preserve this dirty file.

Commit `81ed6a5` is one commit ahead of dotfiles `origin/main` and has not been pushed.

### Live workflow

The live dotfiles have not been targeted/applied. No persistent real-project sandbox has been created. Pi and OMP sandbox authentication has not been completed or tested with real requests. No dev-server-to-host-Chrome trial has been run. The ordinary shell commands therefore still use the existing host workflow.

The broad `~/dev` sandbox remains permanently prohibited because there is no Time Machine recovery layer. That is intentional, not a blocker for the one-repository design.

Open task state:

- Task 12, build host launcher: pending and now blocked on completing the checkpoint integration.
- Task 15, verify agent authentication: pending.
- Task 16, start reversible pilot: pending.

## Single next action

Finish the checkpoint-enabled launcher in canonical `/Users/sudakshsoti/dev/dotfiles`: begin by reviewing the existing uncommitted `private_dot_local/bin/executable_agent-sandbox` diff, then add the focused fake-`sbx` checkpoint contract tests and documentation/wrapper integration, run the repository’s narrow verification suite, and commit that completed slice. Do not apply the live dotfiles or create a real sandbox until this action passes cleanly.
