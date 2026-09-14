# Docker clone-mode task decision

Date: 2026-09-14
Status: planning decision; implementation remains pending in `/Users/sudakshsoti/dev/dotfiles`.

## Decision

Use Docker's recommended clone mode directly from the canonical main Git checkout:

```sh
sbx create --clone shell --name <sandbox> <canonical-checkout>
# or
sbx run --clone <agent> <canonical-checkout>
```

Docker, not the task engine, creates the private writable Git clone inside the sandbox. The task engine must not create a per-repository mirror, a per-task standalone source checkout, or any other intermediate source artifact. The source must be the main checkout, not a linked worktree.

This follows Docker's clone-mode contract: the clone uses the ref currently checked out in the canonical repository at creation time, and clone mode is fixed for the sandbox lifetime. The task engine records and verifies that base commit, then creates its `task/<slug>` branch inside the guest. It does not temporarily switch the canonical checkout or independently select `origin/main`.

## Preserved v1 boundaries

- Task state remains schema-versioned, private, atomically written, and protected by repository/task locks.
- Lifecycle checks remain fail-closed: active sessions, dirty guest state, identity mismatches, unsafe removal, explicit discard confirmation, and partial-failure reporting are retained.
- Task sandboxes remain local-only; cloud flags and cloud-prefixed identities remain rejected.
- The canonical checkout is never writable through the guest clone, and direct-mode checkpoints are not added to task mode.
- Export remains a one-shot, streamed `git bundle` handoff. Docker-generated remotes are not used for v1 because the spike found their retention unreliable across multiple sandboxes.
- Real temporary Git repositories, real guest Git operations, and real `git bundle verify` remain required in the fake-`sbx` and integration tests.
- Direct `pis`/`omps` behavior and direct lifecycle command ownership remain unchanged.

## Consequences

The old `origin/main` default and internal `--base HEAD` mirror-ref flow are removed from the plan. To choose a base, the operator must check out the desired committed ref in the canonical main checkout before creating the task; the checkout must be clean. An unpushed committed `HEAD` is supported because Docker clones the canonical checkout's current commit directly. Ignored files remain outside the clone and are not exported.

Task records contain the canonical checkout path and clone base commit, but no mirror or source-checkout paths. If the canonical checkout is moved or deleted, inventory reports the mismatch and task commands refuse repair or deletion until the recorded path is restored. Removal then deletes only the Docker-managed sandbox before marking the task removed; the verified bundle remains under the documented bounded retention policy.

## Documentation updated

- `plans/scalable-agent-sandbox-tasks.md`
- `plans/scalable-agent-sandbox-user-manual.md`

Reference: Docker [sandbox usage](https://docs.docker.com/ai/sandboxes/usage/) and [Git workflows](https://docs.docker.com/ai/sandboxes/workflows/git/).
