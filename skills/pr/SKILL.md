---
name: pr
description: "Branch, commit, push, and open a GitHub pull request for the current work."
disable-model-invocation: true
---

# Pull request

Arguments may say `draft`, name a base branch, or add notes for the
description.

1. Find the base: the argument, else
   `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`.
2. If `gh pr view --json url,state` finds an open PR for this branch, commit
   and push new work (step 4) and report that PR's URL.
3. On the base branch, create a branch named for the change, following the
   pattern in `git branch -r` when there is one; on another feature branch,
   skip this. Local commits the base holds beyond `origin/<base>` travel with
   the new branch; after switching, run `git branch -f <base> origin/<base>`
   so the base stays clean. If git refuses because another worktree has the
   base checked out (`git worktree list`), leave the base as it is and report
   it.
4. Commit uncommitted task changes per the Commit section of the `commit-push`
   skill (`skill://commit-push`), then push per the `push` skill
   (`skill://push`).
5. Stop and report when the branch has no commits ahead of `origin/<base>`
   (`git rev-list --count origin/<base>..HEAD` is 0).
6. `gh pr create --base <base> --title <title> --body-file -` (add `--draft`
   when asked). The title follows the commit style; one commit reuses its
   subject. Fill `.github/pull_request_template.md` when it exists; otherwise
   the body covers what changed and why, verification actually run with its
   result, and risks. Title and body carry only task content.

Done when `gh pr view --json url,state` returns an open PR for the branch.

Report: the PR URL, branch, and base.
