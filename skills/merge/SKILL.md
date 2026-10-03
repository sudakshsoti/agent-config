---
name: merge
description: "Merge the current branch's pull request once checks pass, then sync the base branch."
disable-model-invocation: true
---

# Merge

Merge the PR for the current branch, or the PR number given as an argument.

1. `gh pr view [<n>] --json number,url,state,isDraft,mergeable,reviewDecision,baseRefName,headRefName,headRefOid`.
   Stop and report when it is closed, a draft, conflicting, or has changes
   requested. `mergeable: UNKNOWN` means GitHub is still computing it: re-run
   once after 5 s.
2. `gh pr checks [<n>] --watch`. Stop and report any failing check by name. A
   PR with no checks proceeds. Wait as long as checks run.
3. Pick the method the repo allows
   (`gh repo view --json squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed`).
   The PR is stacked when `baseRefName` is not the default branch
   (`gh repo view --json defaultBranchRef -q .defaultBranchRef.name`) or when
   `gh pr list --state open --base <headRefName> --json number` is not empty.
   A stacked PR merges with `--merge` or `--rebase` (a squash forces conflicts
   in the PRs above it) and without `--delete-branch` (deleting the head
   retargets or closes the child PRs); report that the head branch was kept.
   Otherwise squash when several methods are allowed and add `--delete-branch`.
   Run `gh pr merge <n> --<method> [--delete-branch]`. A branch-protection
   refusal ends the run with a report; use `--admin` or `--auto` only when I
   ask.
4. Sync the base. Never delete a head branch that another open PR targets.
   1. If another worktree has `<baseRefName>` checked out
      (`git worktree list --porcelain`), git refuses both `switch` and
      `git fetch origin <baseRefName>:<baseRefName>`. Run
      `git fetch origin <baseRefName>`, leave that worktree's base alone, and
      report that the local base was not synced. Then
      `git switch --detach origin/<baseRefName>` so the head branch is free to
      delete.
   2. Otherwise `git switch <baseRefName>`, then `git pull --ff-only`.
   3. If the local head branch survived and no open PR targets it, delete it
      with `git branch -D <headRefName>` only when the PR state is `MERGED`
      and `git rev-parse <headRefName>` equals `headRefOid` (squash merges
      make `-d` refuse). Otherwise keep the branch and report why.
5. Watch what the merge commit triggers: deploys report there, after the PR's
   checks have passed. Get the SHA with
   `gh pr view <n> --json mergeCommit --jq .mergeCommit.oid`, then read
   `gh api 'repos/{owner}/{repo}/commits/<sha>/status' --jq '{state, total_count, statuses: [.statuses[] | {context, state, description}]}'`
   and `gh api 'repos/{owner}/{repo}/commits/<sha>/check-runs' --jq '[.check_runs[] | {name, status, conclusion}]'`.
   Repeat every 30 s while any `statuses[].state` is `pending` or any
   `check_runs[].status` is not `completed`, for up to 10 minutes. Ignore the
   top-level `state`: it reads `pending` when nothing reports. Both arrays
   empty after the first minute means the merge triggers nothing. Report each failure by name with its description (e.g.
   "Deployment rate limited"): the code merged but is not live.

Done when the PR state is `MERGED`, the local base matches its upstream, and
the merge commit has no pending status or check.

Report: PR URL, merge method, merge commit, current branch, and post-merge
status/check results (passed, failed with description, or still pending at the
time limit).
