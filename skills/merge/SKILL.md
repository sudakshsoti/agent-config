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
5. Watch what the merge commit triggers: deploys report there, after the PR's
   checks have passed. Get the SHA with
   `gh pr view <n> --json mergeCommit --jq .mergeCommit.oid`, then read
   `gh api 'repos/{owner}/{repo}/commits/<sha>/status' --jq '{state, total_count, statuses: [.statuses[] | {context, state, description}]}'`
   and `gh api 'repos/{owner}/{repo}/commits/<sha>/check-runs' --jq '[.check_runs[] | {name, status, conclusion}]'`.
   Repeat every 30 s while any entry is pending or in progress, for up to
   10 minutes. Nothing reported after the first minute means the merge
   triggers nothing. Report each failure by name with its description (e.g.
   "Deployment rate limited"): the code merged but is not live.

Done when the PR state is `MERGED`, the local base matches its upstream, and
the merge commit has no pending status or check.

Report: PR URL, merge method, merge commit, current branch, and the merge
commit's statuses and checks (passed, failed with description, or still
pending at the time limit).
