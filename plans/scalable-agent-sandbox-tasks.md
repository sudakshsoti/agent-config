# Add scalable sandbox-isolated agent tasks

Status: approved direction, revised after staging spike; implementation pending.

## Goal

Add a small, low-friction v1 for running several Pi or OMP tasks concurrently without exposing a canonical checkout or shared Git metadata. Preserve the existing host and direct-sandbox workflows.

```zsh
pi                         # host Pi
omp                        # host OMP
pw payment-report          # host linked worktree + host Pi
ompw payment-report        # host linked worktree + host OMP
pis                        # direct sandbox for the current standalone checkout
omps                       # direct sandbox for the current standalone checkout
pws payment-report         # isolated local clone sandbox + Pi
ompws payment-report       # isolated local clone sandbox + OMP
```

A clone task becomes host-visible only through an explicit export.

## Repository ownership and sequencing

This plan is stored in `agent-config/plans/` because that is the planning repository. **Implementation belongs to `/Users/sudakshsoti/dev/dotfiles`**, where the launcher, shell aliases, tests, and live documentation reside. Do not run an implementation workflow from `agent-config` or interpret paths below relative to this plan.

Before task-mode implementation, finish or explicitly defer the existing bundle auto-reconcile work recorded in the uncommitted `agent-config/TODO.md`. If it proceeds, implement, verify, commit, and apply that direct-mode change in dotfiles first. Then rebase task-mode work on the settled launcher contract. Do not modify the direct `run` path and add task mode concurrently.

## Evidence and adopted boundary

Hands-on spikes produced these decisions:

- **Adopt local Docker Sandboxes clone mode.** Installed `sbx 0.42.1` ran simultaneous private clones with independent branches/files, persistent state after restart, working Git, and no canonical working-file changes.
- **Use one immutable source checkout per live task.** A focused follow-up proved the guest's `origin` is `/run/sandbox/source`, a live read-only mount of the host source. Resetting a shared source immediately changes what an existing task sees as `origin/main`. A bare repository is rejected as a clone source, and `sbx --clone` rejects a linked worktree. Therefore neither one shared checkout nor per-task linked worktrees are valid.
- **Stream export independently of generated remotes.** Generated host remotes depend on sandbox git-daemon ports and have shown inconsistent multi-sandbox retention across spikes. `sbx exec SANDBOX git bundle create - BRANCH > host.bundle` was tested successfully, and the resulting bundle verified with the expected head.
- **Do not migrate to Worktrunk in v1.** Worktrunk `0.77.0` passed macOS lifecycle tests, but changing the mature custom host-worktree lifecycle is unrelated risk.
- **Do not adopt `devcontainer-wt` globally.** It requires repository Dev Container/Compose scaffolding and shares common `.git` metadata.
- **Do not adopt Sandcastle now.** It uses ordinary Docker rather than `sbx`, requires project-local TypeScript setup, and 10 of 44 targeted WorktreeManager tests failed locally on macOS path canonicalization/reuse.

Existing direct-mode `pis` and `omps` do not use clone mode or generated remotes and remain unchanged.

## V1 scope

Implement only:

```text
run <pi|omp> <task>
list [--all] [--json]
stop <task>
export <task>
remove <task>
discard <task>
```

Also implement a local-mode and minimum-version check.

Defer to v2:

- `copy`, `rescue`, `doctor`, and `export --update`;
- Worktrunk migration;
- automatic ports, databases, hooks, quotas, or pruning;
- shared authentication;
- automatic merge, push, pull request creation, or removal after export.

Dirty work in v1 must be committed, including as a WIP commit, before export. `stop` remains available for dirty tasks. There is no claim that v1 rescues dirty or ignored files after destructive removal.

## Language and component boundary

Do not add the task state machine to the existing 1,319-line Bash launcher.

Add a separate Python 3 executable in dotfiles, for example:

```text
private_dot_local/bin/executable_agent-sandbox-task
```

It owns task-mode parsing, state, locking, Git transfer, and `sbx` calls. Keep `private_dot_local/bin/executable_agent-sandbox` focused on current direct mode. `dot_zshrc.tmpl` adds only thin `pws` and `ompws` wrappers. Add focused Python tests in a separate file such as `tests/test-agent-sandbox-task.py`.

Use the Python standard library only. Do not add a package dependency.

## Phase 1 — pin source and identity contracts

1. Require local `sbx >= 0.42.1` and verify `create --clone`, `exec`, `stop`, and `rm` features. The Python engine constructs every `sbx` argv itself with the subcommand first and never forwards global options. Reject user-supplied `--cloud`, registry or CLI identifiers beginning `sbx_`, and inventory records whose ID has the documented cloud prefix. Query inventory only with plain `sbx ls --json`, then require the workspace to equal the per-task source. The fake must model both accepted local UUID records and rejected cloud-prefixed records.
2. Never pass the canonical checkout to `sbx create --clone`.
3. Maintain a generated bare mirror per canonical repository:

   ```text
   ~/Library/Application Support/agent-sandbox/task-sources/<repo-id>/mirror.git
   ```

4. Maintain a **standalone, self-contained source checkout per task**:

   ```text
   ~/Library/Application Support/agent-sandbox/task-sources/<repo-id>/<task-id>/source
   ```

   Create it from the mirror with local hard-link optimization disabled. It must have its own complete `.git` directory, not a `.git` pointer or alternates path. Keep it immutable while the sandbox exists because Docker holds it mounted read-only for that lifetime.
5. Default the source to fresh `origin/main`, matching `pw`. Repositories without that ref require explicit `--base` rather than silently selecting another branch.
6. Support committed `--base HEAD` in v1 by fetching the canonical repository's `HEAD` into a persistent task-specific mirror ref such as `refs/heads/agent-sandbox-base/<task-id>`. Create the standalone source from that ref and verify its `HEAD` before sandbox creation. Keep the mirror ref until the sandbox and source are removed. Reading with `git fetch <canonical-path> HEAD:<task-ref>` is allowed; passing the canonical path to `sbx create --clone` is forbidden. Test an unpushed local commit end to end through mirror, source, and guest.
7. Refuse task creation when the canonical checkout has tracked, staged, or untracked changes. Ignored files do not block creation, but print that they are absent from the task. The user must commit, stash, or remove non-ignored changes before retrying.
8. Remove a task source and its task-specific mirror ref only after its sandbox has been removed. Never reset, move, or garbage-collect a source still referenced by a live or stopped sandbox.

Task identity is SHA-256 of canonical repository path plus original task name. Use a normalized slug only for display and branch names. Sandbox names follow the existing convention with a collision-resistant suffix, for example `agent-task-<repo>-<task>-<digest>`.

The guest branch is `task/<slug>`. The exported host review branch is the **plain slug**, because existing host helpers expect branch and path names without a slash.

## Phase 2 — state and task creation

Store schema-versioned task records atomically under:

```text
~/.local/state/agent-sandbox/tasks/
```

Use directory mode `0700`, record mode `0600`, `lstat` containment checks, and atomic replacement. Record canonical repository, mirror/source paths, task identity, sandbox name, base commit, guest branch, host review branch, lifecycle state, bootstrap version, latest exported commit, and timestamps.

Use lock order: repository, then task. Hold the task lock for the entire interactive session. A second writable attachment to the same task refuses.

Create locally with:

```sh
sbx create --clone shell --name <sandbox> <per-task-source>
```

Then install the existing pinned configuration bundle, create `task/<slug>` from the recorded base, write a full task-ID guest marker, and launch Pi or OMP with arguments preserved exactly.

Authentication remains per sandbox. Never mount or copy host Pi/OMP auth stores. Resume reuses guest-local tools, files, sessions, and authentication until task removal.

**Task mode skips direct-mode repository checkpoints.** The canonical checkout is never mounted or writable, and the generated task source is reproducible committed state. This exception must be explicit in code and documentation rather than silently bypassing the direct-mode guard.

## Phase 3 — export once to a host worktree

V1 export is one-shot. After export, continue review and development in the host worktree; do not resume the sandbox expecting a second export. Updating an existing review worktree is v2.

1. Require no active task session.
2. Capture the guest branch and `HEAD`; require a clean tracked, staged, and untracked status.
3. Stream a bundle directly to a private host temporary file:

   ```sh
   sbx exec <sandbox> git bundle create - task/<slug> > <temporary-bundle>
   ```

   Keep stderr separate so diagnostics cannot corrupt bundle bytes.
4. Verify the bundle and require `git bundle list-heads` to map the guest branch to the captured commit. No second guest-state capture is needed: the verified bundle is exactly the captured commit even if the guest later changes.
5. Atomically retain the verified bundle under the task recovery directory, named by commit SHA. Never replace the previous valid file before verification succeeds.
6. Fetch it into a namespaced host ref.
7. Create a plain-slug host branch and `~/worktrees/<repo>/<slug>` worktree from that exact ref. Refuse branch/path collisions, checked-out branches, or unrelated existing refs; never force or invent a different name.
8. Record the exported commit only after the host ref and worktree verify at that SHA.

Export never merges, pushes, deletes the sandbox, or copies ignored files, credentials, and agent session history.

## Phase 4 — stop and deletion safety

`stop` is always allowed, including for dirty tasks, because it preserves sandbox state. It invokes local `sbx stop` only.

`remove` requires:

- no active task session;
- clean tracked, staged, and untracked guest state;
- current guest `HEAD` equal to the verified exported commit;
- matching registry, source path, and guest identity;
- explicit warning that ignored files, authentication, sessions, and guest-installed tools will be destroyed.

Remove in this order: sandbox, per-task source checkout, then mark the registry removed. Retain the verified bundle according to a documented bounded policy. On partial failure, stop and print the exact surviving paths; do not continue deleting.

`discard` reports dirty, untracked, and ignored paths and requires typing the exact hashed sandbox name. It is the only v1 path that permits deleting unexported work and must state that recovery is not provided.

Task commands operate only on names matching task registry records and the `agent-task-...-<digest>` convention. Existing direct-mode `agent-stop`, `agent-reset`, and `agent-doctor` must continue to address only the per-repository direct sandbox. Direct commands ignore task sandboxes; task commands ignore direct sandboxes.

All task operations are local. Never pass `--cloud`. Warn prominently that direct `sbx prune`, `sbx reset`, or `sbx rm` bypasses task safety and can destroy stopped tasks.

## Phase 5 — observability and rollback

Reuse `~/.local/state/agent-sandbox/audit.log`. Preserve its privacy contract: UTC timestamp, action, sandbox, canonical repository, and result only—never argv, prompts, environment variables, status contents, or secrets.

Keep the v1 lifecycle small: creating, ready, running, exporting, exported, removing, removed. Make transitions idempotent and fail closed when registry, local Docker state, source path, or guest marker disagree. `list` surfaces interrupted or mismatched records without attempting repair.

Before rollback or upgrade, `list --all` must inventory active, stopped, dirty/unknown, and unexported tasks and print recovery guidance. Removing aliases or task dispatch must not imply that managed sandboxes are safe to prune.

## Phase 6 — tests and rollout

In dotfiles, add `tests/test-agent-sandbox-task.py`. Its fake `sbx` must maintain a real temporary directory per sandbox name and emulate:

- local `create --clone` by cloning the supplied standalone source;
- `exec` by running the requested command in that real guest repository, including binary bundle output;
- `stop`, `rm`, and JSON inventory;
- guest identity and persistence across stop/resume.

Do not fake Git output with canned strings. Export tests must exercise real temporary Git repositories and real `git bundle verify`.

Cover:

- version gates, locally constructed `sbx` argv, local UUID inventory, and rejection of `--cloud` or `sbx_` identifiers;
- identity, slug collisions, and hashed sandbox names;
- per-task standalone sources and absence of `.git` pointers/alternates;
- immutable source enforcement and source deletion only after sandbox removal;
- an unpushed committed `--base HEAD` surviving mirror, source, and guest; non-`main` behavior; tracked/untracked host refusal; and ignored-file warning;
- two and three concurrent tasks from one repository;
- direct/task command isolation;
- task lock contention and exact Pi/OMP argument preservation;
- streamed bundle bytes, stderr separation, verification, disk exhaustion, and interrupted export;
- plain-slug host branch/path collisions;
- dirty stop, removal refusal, exact-confirm discard, and partial deletion;
- secret-safe audit output and rollback inventory.

Add an opt-in integration test using installed local `sbx` and disposable repositories only. It must verify the focused spike result: Task A's source remains fixed while Task B is created from a different per-task source. Also cover stop/resume, stream export, arbitrary removal order, and cleanup. Never run against a production repository.

Verify with the narrowest relevant checks:

```sh
python3 -B tests/test-agent-sandbox.py
python3 -B tests/test-agent-sandbox-task.py
zsh -n <rendered helper block>
shellcheck private_dot_local/bin/executable_agent-sandbox
chezmoi diff ~/.zshrc
```

Apply only the intended chezmoi target after reviewing the diff.

Roll out: disposable repository, read-only finance task, one small finance task, two simultaneous finance tasks, one larger repository, then OMP parity.

## Acceptance criteria

- Existing `pi`, `omp`, `pw`, `ompw`, `pis`, `omps`, and direct lifecycle commands are unchanged and cannot target task sandboxes.
- Task commands cannot target direct-mode sandboxes.
- Two tasks from one repository use different immutable standalone source checkouts and do not share writable files, Git metadata, credentials, or lifecycle state.
- Creating Task B cannot change Task A's mounted source or its `origin/main`.
- Clone creation does not alter the canonical checkout's files or Git configuration and creates no direct-mode checkpoint.
- A clean committed guest branch streams to a verified bundle and produces a plain-slug host branch/worktree at the exact commit.
- Normal removal cannot delete dirty, unexported, mismatched, or active work.
- `stop` preserves guest state; `discard` is explicit and clearly irreversible.
- Local-only enforcement and warnings prevent the wrapper from silently entering cloud mode or endorsing unsafe direct `sbx` cleanup.
