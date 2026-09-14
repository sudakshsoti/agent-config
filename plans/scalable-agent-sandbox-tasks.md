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
- **Pass the canonical checkout directly to Docker clone mode.** `sbx create/run --clone` requires the main Git checkout (not a linked worktree) and Docker creates the private writable clone inside the sandbox. Clone mode follows the canonical checkout's currently checked-out ref at creation time; no custom mirror or per-task source checkout is needed. The canonical checkout remains outside the guest's writable clone.
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

1. Require local `sbx >= 0.42.1` and verify `create --clone`, `run --clone`, `exec`, `stop`, and `rm` features. The Python engine constructs every `sbx` argv itself with the subcommand first and never forwards global options. Reject user-supplied `--cloud`, registry or CLI identifiers beginning `sbx_`, and inventory records whose ID has the documented cloud prefix. Query inventory only with plain `sbx ls --json`, then require the workspace to equal the recorded canonical checkout. The fake must model both accepted local UUID records and rejected cloud-prefixed records.
2. Pass the canonical main checkout directly as the source argument to `sbx create --clone` or `sbx run --clone`; never pre-copy it into a custom mirror or task source.
3. Require the canonical checkout to be a main Git checkout, not a linked worktree, and refuse task creation when it has tracked, staged, or untracked changes. Docker's clone operation captures the canonical checkout's currently checked-out committed ref at creation time. Ignored files do not block creation, but print that they are absent from the task. The user must commit, stash, or remove non-ignored changes before retrying.
4. Record and verify the clone base as the canonical checkout's `HEAD` at creation. V1 has no independent base selector: do not synthesize mirror refs, temporarily switch the canonical checkout, or claim that `origin/main` is selected independently of the checked-out ref. To choose another committed base, the user must check it out in the canonical main checkout before creating the task. Warn that this changes the ref visible to other host work until it is switched back, so it must not be done while direct or host work is relying on that checkout.
5. After Docker creates the private clone, verify its recorded base and create `task/<slug>` inside the guest. The guest clone must have private writable files and Git metadata, while the canonical checkout is never writable through task mode. Test an unpushed committed canonical `HEAD` end to end through Docker's clone.
6. Remove only the sandbox during normal task removal, then mark the registry removed. There is no task source or mirror to clean up. On partial failure, stop and print the exact surviving sandbox and recovery paths; never reset or garbage-collect a live or stopped sandbox.

Task identity is SHA-256 of canonical repository path plus original task name. Use a normalized slug only for display and branch names. Sandbox names follow the existing convention with a collision-resistant suffix, for example `agent-task-<repo>-<task>-<digest>`.

The guest branch is `task/<slug>`. The exported host review branch is the **plain slug**, because existing host helpers expect branch and path names without a slash.

## Phase 2 — state and task creation

Store schema-versioned task records atomically under:

```text
~/.local/state/agent-sandbox/tasks/
```

Use directory mode `0700`, record mode `0600`, `lstat` containment checks, and atomic replacement. Record the canonical repository path, task identity, sandbox name, clone base commit, guest branch, host review branch, lifecycle state, bootstrap version, latest exported commit, and timestamps. Do not record or create mirror/source paths.

Use lock order: repository, then task. Hold the task lock for the entire interactive session. A second writable attachment to the same task refuses.

Create locally with the canonical main checkout as the clone source:

```sh
sbx create --clone shell --name <sandbox> <canonical-checkout>
```

The foreground equivalent is `sbx run --clone <agent> <canonical-checkout>`. Docker owns creation of the private writable clone; the task engine must not stage an intermediate source.

Then install the existing pinned configuration bundle, create `task/<slug>` from the recorded base, write a full task-ID guest marker, and launch Pi or OMP with arguments preserved exactly.

Authentication remains per sandbox. Never mount or copy host Pi/OMP auth stores. Resume reuses guest-local tools, files, sessions, and authentication until task removal.

**Task mode skips direct-mode repository checkpoints.** The canonical checkout is passed to Docker as a read-only clone input; Docker creates the private writable clone, and task edits never write through to the canonical checkout. This exception must be explicit in code and documentation rather than silently bypassing the direct-mode guard.

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
- matching registry, canonical checkout path, and guest identity; if the canonical path is missing or has moved, refuse removal and report the path that must be restored;
- explicit warning that ignored files, authentication, sessions, and guest-installed tools will be destroyed.

Remove in this order: sandbox, then mark the registry removed. Retain the verified bundle according to a documented bounded policy. On partial failure, stop and print the exact surviving paths; do not continue deleting.

`discard` reports dirty, untracked, and ignored paths and requires typing the exact hashed sandbox name. It is the only v1 path that permits deleting unexported work and must state that recovery is not provided.

Task commands operate only on names matching task registry records and the `agent-task-...-<digest>` convention. Existing direct-mode `agent-stop`, `agent-reset`, and `agent-doctor` must continue to address only the per-repository direct sandbox. Direct commands ignore task sandboxes; task commands ignore direct sandboxes.

All task operations are local. Never pass `--cloud`. Warn prominently that direct `sbx prune`, `sbx reset`, or `sbx rm` bypasses task safety and can destroy stopped tasks.

## Phase 5 — observability and rollback

Reuse `~/.local/state/agent-sandbox/audit.log`. Preserve its privacy contract: UTC timestamp, action, sandbox, canonical repository, and result only—never argv, prompts, environment variables, status contents, or secrets.

Keep the v1 lifecycle small: creating, ready, running, exporting, exported, removing, removed. Make transitions idempotent and fail closed when registry, local Docker state, canonical checkout path, or guest marker disagree. If the canonical checkout is missing or has moved, `list` surfaces the mismatch and task commands refuse repair or deletion until the recorded path is restored. `list` surfaces interrupted or mismatched records without attempting repair.

Before rollback or upgrade, `list --all` must inventory active, stopped, dirty/unknown, and unexported tasks and print recovery guidance. Removing aliases or task dispatch must not imply that managed sandboxes are safe to prune.

## Phase 6 — tests and rollout

In dotfiles, add `tests/test-agent-sandbox-task.py`. Its fake `sbx` must maintain a real temporary directory per sandbox name and emulate:

- local `create --clone` by cloning the supplied canonical checkout into a private temporary guest directory;
- `exec` by running the requested command in that real guest repository, including binary bundle output;
- `stop`, `rm`, and JSON inventory;
- guest identity and persistence across stop/resume.

Do not fake Git output with canned strings. Export tests must exercise real temporary Git repositories and real `git bundle verify`.

Cover:

- version gates, locally constructed `sbx` argv, local UUID inventory, and rejection of `--cloud` or `sbx_` identifiers;
- identity, slug collisions, and hashed sandbox names;
- direct canonical-checkout argv, main-checkout enforcement, private guest clone state, and absence of host `.git` write-through;
- an unpushed committed canonical `HEAD` surviving Docker clone creation; checked-out-ref/base validation; tracked/untracked host refusal; ignored-file warning; and canonical-path mismatch refusal;
- two and three concurrent tasks from one repository;
- direct/task command isolation;
- task lock contention and exact Pi/OMP argument preservation;
- streamed bundle bytes, stderr separation, verification, disk exhaustion, and interrupted export;
- plain-slug host branch/path collisions;
- dirty stop, removal refusal, exact-confirm discard, and partial deletion;
- secret-safe audit output and rollback inventory.

Add an opt-in integration test using installed local `sbx` and disposable repositories only. It must verify that Task A's Docker-managed private clone remains fixed while Task B is created directly from the canonical checkout after a new committed base is selected. Also cover stop/resume, stream export, arbitrary removal order, and cleanup. Never run against a production repository.

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
- Two tasks from one repository use different Docker-managed private writable clones and do not share writable files, Git metadata, credentials, or lifecycle state.
- Creating Task B cannot change Task A's clone, files, Git metadata, or recorded base.
- Clone creation passes the canonical main checkout directly, does not create a custom mirror/source, does not alter the canonical checkout's files or Git configuration, and creates no direct-mode checkpoint.
- A clean committed guest branch streams to a verified bundle and produces a plain-slug host branch/worktree at the exact commit.
- Normal removal cannot delete dirty, unexported, mismatched, or active work.
- `stop` preserves guest state; `discard` is explicit and clearly irreversible.
- Local-only enforcement and warnings prevent the wrapper from silently entering cloud mode or endorsing unsafe direct `sbx` cleanup.
