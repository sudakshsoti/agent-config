---
name: push
description: |
  Push the current branch safely. Use when the user types /push or says "push",
  "push my changes", "push to remote", "push it up". Sets upstream on the first
  push, shows the outgoing commits before sending, refuses a bare --force (uses
  --force-with-lease instead), and warns before pushing straight to main/master.
  Offers to open a PR afterward when on a feature branch.
user-invocable: true
---

# Push

Send the current branch to the remote — with the guard rails on.

## 1. Know where you are

Run `git branch --show-current` and `git status -sb`. If there are uncommitted
changes the user clearly meant to send, point them at `/commit` first rather
than pushing a half-done branch.

## 2. Show what's going out

Before pushing, show the commits that will travel:

- With an upstream: `git log @{u}..HEAD --oneline`.
- No upstream yet: `git log <base>..HEAD --oneline` (base = the default branch).

If that list is empty, there is nothing to push — say so and stop.

## 3. Push

- **First push (no upstream):** `git push -u origin <branch>` to set tracking.
- **Subsequent pushes:** plain `git push`.
- **On `main`/`master` (or the default branch):** this user works via feature
  branches and PRs. Before pushing directly to the default branch, warn and get
  an explicit go-ahead — offer to create a branch instead.

## 4. Never bare --force

If the branch has diverged (after a rebase or `--amend`), a force is sometimes
needed. Use `git push --force-with-lease --force-if-includes`, never plain
`git push --force`, and confirm with the user first — force-with-lease refuses
to clobber commits you haven't seen.

## 5. Offer the next step

After a successful push on a feature branch with no PR yet, offer `/pr`. If a PR
already exists, mention it's updated.
