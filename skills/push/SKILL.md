---
name: push
description: "Push the current branch: fetch, rebase if behind, never force."
disable-model-invocation: true
---

# Push

Push the current branch. Arguments, if any, name the remote or branch.

1. With no upstream, run `git push -u origin HEAD` and skip to the report.
2. `git fetch` the upstream. If it holds commits the branch lacks, run
   `git rebase --autostash @{u}` so uncommitted work survives. On conflict,
   `git rebase --abort` and report the conflicting files.
3. `git push`. A rejected push means history diverged: report it. Force only
   when I ask, and then as `--force-with-lease`.

Done when `git status -sb` shows the branch level with its upstream, or the
report names why it is not.

Report: branch, remote, pushed commit range (or "already up to date").
