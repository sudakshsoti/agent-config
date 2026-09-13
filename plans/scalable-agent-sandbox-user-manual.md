# User manual: parallel Pi and OMP tasks

> **Planned system:** This manual describes the workflow after `plans/scalable-agent-sandbox-tasks.md` is implemented. The `pws` and `ompws` commands documented here do not exist yet. Current `pi`, `omp`, `pw`, `ompw`, `pis`, and `omps` behavior remains authoritative until rollout is complete.

## Choose the right workflow

Use the lightest isolation that fits the task.

| Need | Command | Where files live | Git | Authentication |
| --- | --- | --- | --- | --- |
| Work normally in the current checkout | `pi` or `omp` | Current host checkout | Host | Host |
| Work on a parallel branch with immediate host/editor visibility | `pw TASK` or `ompw TASK` | Host linked worktree | Shared host repository metadata | Host |
| Give an agent sandbox access to the current standalone checkout | `pis` or `omps` | Host checkout, directly mounted | Host checkout | Sandbox-local |
| Isolate a task's files and Git metadata from the host | `pws TASK` or `ompws TASK` | Private sandbox clone | Private guest repository | Sandbox-local per task |

### Practical rule

- Start with `pi` for ordinary work.
- Use `pw` when the main problem is branch or file separation and you want live access from host tools.
- Use `pis` when you deliberately want a sandbox to edit one existing standalone checkout directly.
- Use `pws` when the task is risky, long-running, concurrent with other tasks, or should not have writable access to host files or Git metadata.

A linked worktree created by `pw` is not accepted by direct-mode `pis`. Choose either the host-worktree lane or the isolated-task lane for that task.

## Command model

### Existing commands

```zsh
pi                         # Pi on the host
omp                        # OMP on the host
pw payment-report          # create/reuse a host worktree and launch Pi
ompw payment-report        # create/reuse a host worktree and launch OMP
pis                        # Pi in the direct sandbox for this standalone repo
omps                       # OMP in the direct sandbox for this standalone repo
```

Current direct-sandbox management remains available:

```zsh
agent-status
agent-shell
agent-checkpoints
agent-port 3000:3000
agent-unport 3000:3000
agent-stop
agent-reset
agent-doctor
```

See the installed dotfiles documentation at `docs/agent-sandbox-trial.md` in the dotfiles repository for direct-mode recovery details.

### Planned isolated-task commands

```zsh
pws TASK                    # shorthand for: pws run TASK
pws run TASK                # create or resume TASK with Pi
ompws TASK                  # create or resume TASK with OMP
pws list                    # tasks for the current repository
pws list --all              # tasks across repositories
pws list --json             # machine-readable inventory
pws stop TASK               # stop while preserving the task
pws export TASK             # create a host review worktree
pws export TASK --update    # update an existing clean review worktree
pws copy TASK PATH          # explicitly copy one host path into the guest
pws remove TASK             # safe removal after verified export
pws rescue TASK             # archive the complete guest repository
pws discard TASK            # explicitly destroy unexported state
pws doctor                  # inspect task-system health
```

Task names matching reserved subcommands such as `list`, `run`, `export`, or `remove` are rejected.

## Start an isolated task

Run the command from the canonical standalone repository, not from `~/dev`, a linked worktree, or an arbitrary subdirectory outside a repository.

```zsh
cd ~/dev/finance
pws payment-report
```

On first use, the system will:

1. identify the canonical repository;
2. prepare a private committed-source staging checkout;
3. select fresh `origin/main` as the default base;
4. create a private clone-mode Docker Sandbox;
5. create `task/payment-report` inside it;
6. install the pinned agent configuration;
7. launch Pi.

The host `finance` checkout is not edited or reconfigured. The task's files, Git metadata, tools, authentication, and agent sessions remain inside its sandbox.

### Start from the current committed `HEAD`

If the task must include local commits that are not on `origin/main`:

```zsh
pws run payment-report --base HEAD
```

Only committed history is transferred. Dirty tracked files, untracked files, and ignored files are not inherited.

Before starting, inspect host state:

```zsh
git status --short --ignored
```

Commit appropriate source changes first, or copy a specific required file after task creation.

### Pass arguments to the agent

Arguments following the task options are passed to Pi or OMP without reinterpretation. Use the command's `--help` output for the final delimiter syntax implemented during rollout.

## Resume a task

Use the same repository and task name:

```zsh
cd ~/dev/finance
pws payment-report
```

Resume reuses:

- the same sandbox;
- the same guest branch and files;
- installed guest tools;
- sandbox-local authentication;
- retained Pi or OMP state.

Only one writable agent session may own a task at a time. A second launch refuses instead of opening two agents against the same checkout.

## Run several tasks concurrently

Give every task a distinct, descriptive name:

```zsh
cd ~/dev/finance
pws payment-report

# In another terminal
cd ~/dev/finance
pws reconcile-imports

# OMP can own another independent task
cd ~/dev/finance
ompws investigate-tax-rounding
```

Each task receives its own sandbox and Git repository. Tasks from different repositories may use the same human-readable name because their full identities include the canonical repository.

Inspect everything with:

```zsh
pws list --all
```

The list distinguishes live status from cached status and shows when cached information was last observed.

## Work with host-only files

Ignored files and secrets are not copied automatically. If a task needs one host file:

```zsh
pws copy payment-report .env.development
```

The command shows whether the file is ignored and asks for confirmation when appropriate. The file is copied only into that task sandbox—not into shared staging and not into another task.

Use this sparingly:

- Prefer test fixtures or non-secret development configuration.
- Never copy the host Pi/OMP auth stores.
- Do not copy an entire home directory, credential directory, or parent directory.
- Remember that copied files are destroyed with the sandbox unless rescued separately.

## Authentication

Every isolated task is a separate login boundary. The first Pi or OMP launch in a new task may require authentication.

Authentication persists when you exit or stop the task. It is destroyed when you remove or discard the sandbox. Exporting source code does not export credentials or agent session history.

This is deliberate: tasks do not share mutable credential stores.

## Stop without finishing

To preserve a task but release its running sandbox resources:

```zsh
pws stop payment-report
```

Stopping is always allowed, including when the working tree is dirty. Resume with:

```zsh
pws payment-report
```

Do not use `discard` merely to stop work for the day.

## Export work for host review

Commit the task's source changes inside the sandbox, then make sure its working tree is clean:

```zsh
git status --short
```

From the host:

```zsh
cd ~/dev/finance
pws export payment-report
```

Export will:

1. refuse if the task is active or dirty;
2. transfer and verify the exact committed branch;
3. retain a private recovery bundle on the host;
4. import the commit under a namespaced host reference;
5. create a normal host review branch and worktree.

Export does **not** merge, push, open a pull request, or remove the sandbox.

Use normal host tools in the resulting review worktree:

```zsh
git status
git log --oneline --decorate -10
# run tests, amend commits, review, push, or use the existing finish workflow
```

### Continue after exporting

The task sandbox remains available:

```zsh
pws payment-report
```

After committing more work, explicitly update the host review worktree:

```zsh
pws export payment-report --update
```

Update refuses if the host review worktree is dirty or no longer points to the expected exported history. Resolve host changes before retrying; the command never overwrites them.

## Handle dirty or untracked guest work

Normal export and removal refuse when tracked, staged, or untracked changes exist.

Choose one of these actions:

1. **Keep working:** resume and commit the files.
2. **Delete disposable files manually:** inspect them inside the guest, then remove them.
3. **Preserve everything:** run `pws rescue TASK`.
4. **Intentionally lose it:** run `pws discard TASK` and confirm the exact sandbox name.

Ignored files are reported separately. They are not part of Git export.

## Rescue a task

Use rescue when a dirty task cannot be cleaned or committed safely:

```zsh
pws rescue payment-report
```

Rescue creates a private, checksummed archive containing the complete guest repository, including `.git`, dirty files, untracked files, and ignored files.

Treat the archive as sensitive because it may contain credentials or `.env` files. The tool reports its location but never extracts it automatically. Preserve the archive until recovery is verified.

Rescue is a local recovery copy, not an off-device backup.

## Remove a completed task

After exporting the current task commit and verifying the host worktree:

```zsh
pws remove payment-report
```

Normal removal refuses unless:

- no task session is active;
- tracked, staged, and untracked state is clean;
- the current commit exists in a verified host export;
- the registry and guest identity agree.

Before removal, review the warning: guest-local authentication, agent sessions, installed tools, and ignored files will be destroyed. Verified export bundles remain subject to the documented retention policy.

## Discard a task intentionally

Use discard only when the task's contents are not needed:

```zsh
pws discard abandoned-experiment
```

The command lists dirty, untracked, and ignored paths and requires the exact sandbox name as confirmation. This operation is intentionally difficult to perform accidentally.

If uncertain, stop or rescue instead.

## Diagnose problems

Start with:

```zsh
pws doctor
pws list --all
```

Doctor reports, but does not automatically delete or repair:

- unsupported `sbx` versions;
- stale task locks;
- missing staging checkouts;
- task registry and sandbox mismatches;
- orphan sandboxes;
- unexported commits;
- incomplete exports or removals.

For machine-readable inventory:

```zsh
pws list --all --json
```

Do not run `sbx rm` directly on a managed task. Doing so bypasses export and deletion checks.

## Common use cases

### Quick change in the current checkout

```zsh
cd ~/dev/finance
pi
```

Use this when isolation is unnecessary.

### Parallel task with host editor access

```zsh
cd ~/dev/finance
pw update-dashboard
```

Use a host worktree when immediate file visibility and host tooling matter more than containment.

### Agent edits the current standalone checkout inside a sandbox

```zsh
cd ~/dev/finance
pis
```

Use direct mode deliberately. The host checkout changes immediately, and repository checkpoints protect recovery. Do not run it from a linked worktree.

### Risky dependency or migration experiment

```zsh
cd ~/dev/finance
pws try-new-migration
```

The experiment cannot write to the canonical checkout or sibling task Git metadata. Export only if the result is worth retaining.

### Long-running task over several days

```zsh
pws multi-currency-report
# exit the agent
pws stop multi-currency-report
# later
pws multi-currency-report
```

Use stop rather than removal so tools, authentication, files, and sessions persist.

### Review sandbox work on the host

```zsh
pws export multi-currency-report
# inspect the reported host worktree
```

The sandbox remains intact while review proceeds.

### Abandon an experiment safely

```zsh
pws stop failed-experiment
pws rescue failed-experiment   # if anything might matter
pws discard failed-experiment
```

## Safety rules

1. Do not use `sbx rm` directly for managed tasks.
2. Do not assume export includes dirty, untracked, or ignored files.
3. Stop when pausing; remove only after verified export.
4. Rescue before destructive cleanup whenever uncertain.
5. Keep one task name per independent objective.
6. Do not share authentication directories between task sandboxes.
7. Inspect `pws doctor` before rollback, manual cleanup, or upgrading Docker Sandboxes.
8. Use `pw`, not `pws`, when continuous host visibility is required.
9. Use `pws`, not `pis`, when task-level Git and filesystem isolation is required.
10. Treat local recovery archives as sensitive and not as off-device backups.

## Lifecycle summary

```text
create/resume
    pws TASK
        |
        +--> stop and resume later
        |       pws stop TASK
        |       pws TASK
        |
        +--> commit and export
        |       pws export TASK
        |       pws export TASK --update   # after later commits
        |
        +--> rescue dirty state
        |       pws rescue TASK
        |
        +--> safe cleanup after export
        |       pws remove TASK
        |
        +--> intentional destructive cleanup
                pws discard TASK
```
