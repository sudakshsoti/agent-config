# Add scalable sandbox-isolated agent tasks

Status: approved direction, implementation pending.

## Goal

Add a low-friction way to run several Pi or OMP tasks concurrently without exposing a canonical checkout or shared Git metadata to those tasks. Preserve the existing host and direct-sandbox workflows.

The intended command model is:

```zsh
pi                         # host Pi
omp                        # host OMP
pw payment-report          # host linked worktree + host Pi
ompw payment-report        # host linked worktree + host OMP
pis                        # direct sandbox for the current standalone checkout
omps                       # direct sandbox for the current standalone checkout
pws payment-report         # isolated clone-mode task sandbox + Pi
ompws payment-report       # isolated clone-mode task sandbox + OMP
```

A clone-mode task becomes host-visible only through an explicit export.

## Evidence and adopted boundary

Hands-on spikes produced these decisions:

- **Adopt Docker Sandboxes clone mode.** Installed `sbx 0.42.1` successfully ran two simultaneous clone sandboxes with independent branches and files, persistent state after restart, working Git, and no host working-file changes.
- **Do not rely on Docker's generated host remote.** Creating a second sandbox replaced the first sandbox's generated remote entry. Export must use an independently verified transfer.
- **Do not migrate to Worktrunk in v1.** Worktrunk `0.77.0` passed create, execute, list, and clean-removal tests on macOS, but replacing the mature custom host-worktree lifecycle is unrelated risk. Evaluate it later as a separate project.
- **Do not adopt `devcontainer-wt` globally.** It requires repository-specific Dev Container and Compose scaffolding and deliberately mounts shared Git common metadata.
- **Do not adopt Sandcastle now.** It uses ordinary Docker rather than `sbx`, requires project-local TypeScript setup, and 10 of 44 targeted WorktreeManager tests failed locally on macOS path canonicalization and worktree reuse.

Clone mode modifies its source repository's Git configuration while managing generated remotes. It must therefore use a generated staging checkout, never the canonical checkout. Existing direct-mode `pis` and `omps` do not use clone mode or generated remotes and remain unchanged.

## Non-goals for v1

Do not include:

- Worktrunk migration or changes to `pw`, `ompw`, `wtfinish`, or related helpers;
- automatic merge, push, pull request creation, or sandbox deletion after export;
- automatic database or Docker Compose setup;
- automatic project hooks;
- shared host/sandbox authentication;
- automatic ignored-file or secret copying;
- automatic port allocation or resource pruning.

## Phase 1 — pin contracts and add staging sources

1. Require `sbx >= 0.42.1` and verify that `sbx create --clone` is available.
2. Preserve every existing host and direct-sandbox command unchanged.
3. Maintain one generated staging checkout per canonical repository:

   ```text
   ~/Library/Application Support/agent-sandbox/sources/<repo-id>/repository
   ```

4. Under a repository lock, fetch and reset staging to an exact base commit. Default to fresh `origin/main`, matching the current `pw` behavior.
5. Support `--base HEAD` in v1 for a committed local `HEAD`. Transfer that commit to staging through Git, without mounting or cloning from the canonical checkout.
6. Refuse dirty-host inheritance. Print a clear inventory stating that dirty, untracked, and ignored host files are absent.
7. Record remote URL, default branch, selected base, and exact commit. Handle repositories without `origin/main` with an explicit `--base`; never guess a different base silently.

## Phase 2 — add task identity and state

Extend `private_dot_local/bin/executable_agent-sandbox` with:

```text
task run <pi|omp> <task> [agent arguments...]
task list [--all] [--json]
task stop <task>
task export <task> [--update]
task copy <task> <path>
task remove <task>
task discard <task>
task rescue <task>
task doctor
```

Add thin shell entry points:

```zsh
pws <task>                # shorthand for pws run <task>
pws run <task>
pws list
pws export <task>
ompws <task>              # same engine, OMP selected
```

Reserve subcommand names so they cannot also be task slugs. Add completion from the task registry.

Task identity is SHA-256 of the canonical repository path and original task name. Use a normalized, bounded slug only for human-readable branch and sandbox names; the slug is not the identity. Reject case and Unicode ambiguity before creating anything.

Store schema-versioned task records atomically under:

```text
~/.local/state/agent-sandbox/tasks/
```

Use directory mode `0700` and record mode `0600`. Each record contains canonical and staging paths, task identity, sandbox name, base commit, task branch, lifecycle state, bootstrap version, latest exported commit, and timestamps. Validate paths with `lstat`, reject symlinks and escapes, and verify sandbox mode, source, and guest identity on every reuse.

Use fixed lock order: repository, then task. Hold one task lock for the entire interactive agent session. A second writable attachment to the same task refuses. Out-of-band `sbx` attachment is unsupported and reported by `task doctor` when detectable.

## Phase 3 — create and resume task sandboxes

Create with:

```sh
sbx create --clone shell --name <derived-name> <staging-checkout>
```

Then:

1. install the existing pinned configuration bundle;
2. create `task/<slug>` from the recorded base commit;
3. write a guest identity marker containing the full task ID and schema version;
4. launch Pi or OMP with arguments preserved exactly;
5. release the session lock when the process exits, leaving the sandbox persistent.

Authentication remains per sandbox. Never mount or copy host Pi/OMP auth stores. Cache only integrity-verified installers and configuration bundles. First use may require authentication; resuming the same task reuses its guest-local authentication until removal.

Build a versioned Docker kit or equivalent preinstalled base only as a later performance optimization. It must not contain credentials.

## Phase 4 — export committed work

Implement export without Docker's generated remote:

1. Require no active task session. Do not stop and restart the sandbox merely to export.
2. Capture guest branch, `HEAD`, and porcelain-v2 status.
3. Refuse if tracked, staged, or untracked changes exist. Report ignored paths separately as sandbox-only data.
4. Create a Git bundle for the task branch inside the guest.
5. Copy it with `sbx cp` into a private temporary host file.
6. Capture branch, `HEAD`, and status again; refuse and discard the temporary transfer if anything changed.
7. Run `git bundle verify` and require `list-heads` to contain the captured commit.
8. Atomically retain the verified bundle under the task's recovery directory, named by commit SHA. Never replace the previous valid generation before the new one verifies.
9. Fetch the bundle into a namespaced host ref such as `refs/agent-sandbox/<task-id>/<commit>`.
10. Create a host review branch and worktree from that ref using a narrow helper compatible with the existing worktree path and lifecycle.

Export never merges, pushes, force-updates, or deletes the sandbox. Re-export requires `--update`; it refuses if the host review worktree is dirty, checked out unexpectedly, or points to unrelated history.

## Phase 5 — handle host files and dirty guest work honestly

Do not copy `.env`, credentials, ignored files, dependencies, or build output automatically.

Provide an explicit copy command for a user-selected path. It must:

- resolve the source beneath the canonical repository;
- reject symlinks and path escapes;
- show whether the source is ignored;
- request confirmation for ignored files;
- copy into the task guest only, never the shared staging checkout;
- avoid logging contents or values.

`task stop` is always allowed because stopping preserves guest state.

`task remove` requires:

- no active session;
- clean tracked, staged, and untracked state;
- current guest `HEAD` present in a verified retained export;
- matching registry and guest identity;
- a warning that ignored files, authentication, and agent session history will be destroyed.

`task discard` reports all dirty, untracked, and ignored paths and requires typing the exact sandbox name. It never claims the work is recoverable.

`task rescue` is the explicit dirty-work escape hatch. With no active session, create and checksum a private full-repository archive including `.git` and ignored files. Store it under the existing checkpoint/recovery boundary in `~/Library/Application Support/agent-sandbox/`, mode `0700`. Warn that it may contain secrets. Never extract it automatically; document containment, symlink, hard-link, and traversal validation for manual recovery.

## Phase 6 — observability and interrupted operations

Reuse `~/.local/state/agent-sandbox/audit.log` for task commands. Preserve its current privacy contract: timestamp, action, sandbox, repository, and result only—no argv, prompts, environment variables, task contents, or secrets.

Represent external transitions explicitly in the atomic task record: preparing source, creating, bootstrapping, ready, running, exporting, exported, removing, and removed. Commands must be idempotent at each state and fail closed when the registry, Docker state, or guest marker disagree.

`task doctor` reports but never automatically deletes or repairs:

- unsupported Docker Sandbox versions;
- stale locks;
- missing staging checkouts;
- registry/sandbox/guest-marker mismatches;
- orphaned task sandboxes;
- unexported commits;
- incomplete transfers and interrupted removals.

`task list` defaults to the current canonical repository, supports `--all` and `--json`, and labels status as live or cached with a timestamp.

Rollback must first inventory every task and identify dirty or unexported sandboxes. Removing aliases or dispatch code must not strand task data without printed recovery commands.

## Phase 7 — tests and staged rollout

Extend `tests/test-agent-sandbox.py` with fake-`sbx` contract coverage for:

- task identity, normalization collisions, path canonicalization, and non-`main` repositories;
- committed `--base HEAD` and dirty-host refusal;
- staging isolation and canonical Git-config preservation;
- two and three tasks from one source in arbitrary creation/removal order;
- clone/source/guest-marker mismatch;
- registry atomicity, permissions, schema rejection, stale locks, and interrupted states;
- same-task double launch and exact agent-argument preservation;
- bundle copy, before/after race detection, verification, retention, and disk exhaustion;
- repeated export and dirty host review worktrees;
- dirty, untracked, and ignored removal/discard behavior;
- explicit copy containment and secret-safe audit output;
- rescue archive permissions and path/link validation;
- orphan and rollback inventory.

Add opt-in integration tests that use installed `sbx` and disposable repositories only. Cover concurrent sandboxes, generated-remote replacement, stop/resume persistence, export, dirty refusal, rescue, arbitrary removal order, and complete cleanup. Never run these tests against a production repository.

Verify each implementation slice with:

```sh
zsh -n <rendered helper block>
shellcheck private_dot_local/bin/executable_agent-sandbox
python3 -B tests/test-agent-sandbox.py
chezmoi diff ~/.zshrc
```

Apply only the intended chezmoi target after reviewing the diff.

Roll out in this order:

1. disposable repository;
2. read-only finance task;
3. small real finance task;
4. two simultaneous finance tasks;
5. a larger repository;
6. OMP parity.

## Acceptance criteria

- Existing `pi`, `omp`, `pw`, `ompw`, `pis`, and `omps` behavior is unchanged.
- Two task sandboxes from one repository can run concurrently without sharing writable files, Git metadata, credentials, or lifecycle state.
- Clone creation does not alter the canonical checkout's files or Git configuration.
- A clean committed guest branch exports to a host worktree with the exact verified commit.
- Dirty or unexported work cannot be removed through the normal removal command.
- Stop preserves guest state and resume returns to the same branch, files, tools, and sandbox-local authentication.
- Every destructive operation is explicit, scoped to one task, audited without secrets, and recoverable or clearly labeled irreversible.
- Current commands remain the rollback path throughout the pilot.
