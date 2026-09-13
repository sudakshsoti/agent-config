# User manual: parallel Pi and OMP tasks

> **Planned v1:** This manual describes the workflow after `plans/scalable-agent-sandbox-tasks.md` is implemented in the **dotfiles repository**. `pws` and `ompws` do not exist yet. Current commands remain authoritative until rollout is complete.

## Choose the right workflow

| Need | Command | Files and Git | Authentication |
| --- | --- | --- | --- |
| Work normally in the current checkout | `pi` or `omp` | Current host checkout | Host |
| Parallel branch with immediate host/editor visibility | `pw TASK` or `ompw TASK` | Host linked worktree; shared host Git metadata | Host |
| Sandbox edits one standalone host checkout directly | `pis` or `omps` | Direct host mount; repository checkpoint first | Sandbox-local |
| Isolate one task from host files and Git metadata | `pws TASK` or `ompws TASK` | Private local sandbox clone | Sandbox-local per task |

Practical rule:

- Use `pi` for ordinary work.
- Use `pw` when immediate host visibility matters more than containment.
- Use `pis` only when a sandbox should deliberately edit the current standalone checkout.
- Use `pws` for risky, concurrent, or long-running work that should not write to host files or shared Git metadata.

A linked worktree created by `pw` cannot be used with direct-mode `pis`. Choose one lane for each task.

## Existing commands

```zsh
pi                         # host Pi
omp                        # host OMP
pw payment-report          # host worktree + Pi
ompw payment-report        # host worktree + OMP
pis                        # direct repository sandbox + Pi
omps                       # direct repository sandbox + OMP
```

Direct-sandbox management remains unchanged:

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

Those direct commands ignore isolated task sandboxes. Task commands likewise ignore direct sandboxes.

## Planned v1 task commands

```zsh
pws TASK                    # create or resume TASK with Pi
pws run TASK                # expanded form
ompws TASK                  # create or resume TASK with OMP
pws list                    # current repository's tasks
pws list --all              # tasks across repositories
pws list --json             # machine-readable inventory
pws stop TASK               # stop and preserve TASK
pws export TASK             # one-time export to a host worktree
pws remove TASK             # remove after verified export
pws discard TASK            # explicitly destroy unexported state
```

Task names matching reserved subcommands are rejected.

The following are deliberately deferred until v2: `copy`, `rescue`, `doctor`, repeated export/update, automatic ports, project hooks, and shared authentication.

## Start an isolated task

Run from the canonical standalone repository:

```zsh
cd ~/dev/finance
pws payment-report
```

The system creates:

1. a private, immutable source checkout for this task;
2. a local clone-mode Docker Sandbox;
3. guest branch `task/payment-report`;
4. pinned Pi configuration inside the guest.

The task's source mount is never shared with another task. The canonical `finance` checkout is not mounted, edited, reconfigured, or checkpointed.

Task sandboxes are always local. The wrapper rejects `--cloud` and cloud sandbox identifiers; cloud sandboxes are outside v1.

### Select the base

The default is fresh `origin/main`, matching `pw`.

To include commits on the current local branch:

```zsh
pws run payment-report --base HEAD
```

Only committed history is included. An unpushed `HEAD` is pinned to a task-specific internal ref and verified through the private source and guest clone.

Task creation refuses while the canonical checkout has tracked, staged, or untracked changes:

```zsh
git status --short --ignored
```

Commit, stash, or remove those non-ignored changes before retrying. Ignored files do not block creation, but they are absent from the task. V1 cannot copy host-only `.env` or ignored files through `pws`; arrange required non-secret configuration manually during the pilot.

A repository without `origin/main` requires an explicit supported base. The tool does not guess.

## First launch and authentication

A new task may install pinned tools and ask you to authenticate Pi or OMP. Authentication belongs only to that sandbox.

It persists across exit, stop, and resume. It is destroyed by `remove` or `discard`. Host Pi/OMP authentication is never mounted or copied.

## Resume a task

Use the same repository and task name:

```zsh
cd ~/dev/finance
pws payment-report
```

Resume returns to the same sandbox, guest branch, files, installed tools, sessions, and sandbox-local authentication.

Only one writable session may own a task. A second launch refuses instead of opening two agents against the same checkout.

## Run tasks concurrently

Use a distinct name for each objective:

```zsh
# Terminal 1
cd ~/dev/finance
pws payment-report

# Terminal 2
cd ~/dev/finance
pws reconcile-imports

# Terminal 3
cd ~/dev/finance
ompws investigate-tax-rounding
```

Each task has its own immutable host source and private guest repository. Tasks in different repositories may reuse the same display name because their full identity also includes the canonical repository.

Inspect tasks with:

```zsh
pws list
pws list --all
```

## Pause work

```zsh
pws stop payment-report
```

Stopping is always allowed, including when the guest is dirty. It preserves sandbox state for later resume:

```zsh
pws payment-report
```

Do not use `discard` just to release resources.

## Protect work during the v1 pilot

V1 export handles committed Git history only. It has no dirty-file rescue command.

Before pausing important work for a long period:

1. inspect `git status` inside the guest;
2. create a normal or WIP commit;
3. push it to an approved remote if you need off-sandbox durability.

A stopped sandbox is persistent but is not a backup. Running `sbx prune`, `sbx reset`, or `sbx rm` outside `pws` can destroy it and bypass all safety checks.

## Export for host review

Inside the sandbox, commit the final source changes and make the working tree clean:

```zsh
git status --short
```

Then, from the host:

```zsh
cd ~/dev/finance
pws export payment-report
```

Export:

1. refuses if the task is active or dirty;
2. streams a Git bundle from the guest;
3. verifies the branch and exact commit;
4. retains the verified bundle privately on the host;
5. creates plain host branch `payment-report`;
6. creates `~/worktrees/finance/payment-report` at that commit.

It does not merge, push, open a pull request, remove the sandbox, or export ignored files, authentication, and agent sessions.

### Export is one-time in v1

After export, continue work in the host review worktree:

```zsh
cd ~/worktrees/finance/payment-report
git status
git log --oneline --decorate -10
```

Use normal host testing, review, push, and existing finish commands there.

Do not resume the sandbox expecting to export another revision. Updating an existing review worktree is deferred to v2. If the host branch or path already exists, export refuses instead of overwriting it or inventing another name.

## Deal with dirty guest work

Export and normal removal refuse when tracked, staged, or untracked changes exist.

In v1, choose one:

1. commit the work, including as a clearly labeled WIP commit;
2. inspect and delete disposable files inside the guest;
3. stop the task and return later;
4. intentionally discard the task after reviewing the reported paths.

Ignored files are not exported. There is no v1 rescue archive, so do not discard if anything may matter.

## Remove a completed task

After exporting and verifying the host worktree:

```zsh
pws remove payment-report
```

Removal refuses unless:

- no session is active;
- tracked, staged, and untracked state is clean;
- guest `HEAD` equals the verified exported commit;
- task registry, immutable source, sandbox, and guest identity agree.

The tool removes the sandbox before its immutable source checkout. If either step fails, it stops and reports the surviving paths.

Removal destroys sandbox-local authentication, agent sessions, ignored files, and installed guest tools. The verified source bundle is retained according to its documented retention policy.

## Discard intentionally

Use discard only when task contents are not needed:

```zsh
pws discard abandoned-experiment
```

The tool reports dirty, untracked, and ignored paths and requires the exact hashed sandbox name. It states that v1 provides no recovery.

When uncertain, stop instead.

## Inspect health and rollback readiness

V1 has no task `doctor`. Use:

```zsh
pws list --all
pws list --all --json
```

The inventory shows active, stopped, interrupted, mismatched, and unexported tasks when known. Run it before:

- upgrading Docker Sandboxes;
- changing or removing the `pws` aliases;
- rolling back the pilot;
- any manual Docker Sandbox cleanup.

Do not run `sbx prune`, `sbx reset`, or `sbx rm` against managed task sandboxes. Their hashed names begin with the task-specific `agent-task-` convention.

## Common use cases

### Ordinary change

```zsh
cd ~/dev/finance
pi
```

### Parallel work with host editor access

```zsh
cd ~/dev/finance
pw update-dashboard
```

### Sandboxed agent editing the current standalone checkout

```zsh
cd ~/dev/finance
pis
```

Direct mode changes host files immediately and creates a full repository checkpoint first. Do not run it from a linked worktree.

### Risky isolated experiment

```zsh
cd ~/dev/finance
pws try-new-migration
```

The experiment cannot write to the canonical checkout or sibling task Git metadata.

### Multi-day task

```zsh
pws multi-currency-report
# create a WIP commit before a long pause
pws stop multi-currency-report
# later
pws multi-currency-report
```

### Finish and review on the host

```zsh
# Commit and clean the guest first
pws export multi-currency-report
cd ~/worktrees/finance/multi-currency-report
# Review, test, and continue only on the host
```

### Abandon safely

```zsh
pws stop failed-experiment
# Resume and inspect if uncertain
pws failed-experiment
# Only then, if nothing matters:
pws discard failed-experiment
```

## Safety rules

1. Use `pw` when continuous host visibility is required.
2. Use `pws` when task-level filesystem and Git isolation is required.
3. Stop when pausing; remove only after verified export.
4. Commit important guest work, even as WIP, because v1 has no rescue command.
5. Treat export as a one-time handoff to host development.
6. Never use direct `sbx prune`, `reset`, or `rm` for managed tasks.
7. Do not assume dirty, untracked, ignored, authentication, or session data is exported.
8. Keep one task name per independent objective.
9. Never share host authentication directories with a task sandbox.
10. Run `pws list --all` before rollback or manual cleanup.

## V1 lifecycle

```text
create/resume
    pws TASK
        |
        +--> stop and resume
        |       pws stop TASK
        |       pws TASK
        |
        +--> commit and export once
        |       pws export TASK
        |       continue in the host worktree
        |       pws remove TASK
        |
        +--> irreversible abandonment
                pws discard TASK
```
