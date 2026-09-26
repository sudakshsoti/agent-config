---
name: merge
description: "Merge the current branch's pull request once checks pass, then sync the base branch."
disable-model-invocation: true
---

# Merge

Merge the PR for the current branch, or the PR number given as an argument.

1. `gh pr view [<n>] --json number,url,state,isDraft,mergeable,reviewDecision,baseRefName,headRefName`.
   Stop and report when it is closed, a draft, conflicting, or has changes
   requested.
2. `gh pr checks [<n>] --watch`. Stop and report any failing check by name. A
   PR with no checks proceeds.
3. Pick the method the repo allows
   (`gh repo view --json squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed`);
   squash when several are allowed. Run
   `gh pr merge <n> --<method> --delete-branch`. A branch-protection refusal
   ends the run with a report; use `--admin` or `--auto` only when I ask.
4. On the base branch, `git pull --ff-only`. Delete the local head branch if
   it survived, with `git branch -D` (squash merges make `-d` refuse).

Done when the PR state is `MERGED` and the local base matches its upstream.

Report: PR URL, merge method, merge commit, current branch.
