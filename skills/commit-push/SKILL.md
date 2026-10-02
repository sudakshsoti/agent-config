---
name: commit-push
description: "Commit the current task's changes in the repo's style, then push."
disable-model-invocation: true
---

# Commit and push

Arguments, if any, steer the commit message.

## Commit

1. Read `git status --short`, `git diff HEAD`, and `git log --oneline -12`.
2. Stage the files this task changed, by path. Unrelated changes (other work,
   editor churn, config a harness rewrote) stay unstaged. When ownership of a
   change is unclear, ask before staging it.
3. Write the message in the style the log shows: prefix convention, mood,
   subject length. The subject says what changed; a body, when needed, says
   why. Split into several commits only when the diff holds independent
   changes.
4. The message carries its own content only: no co-author, "Generated with",
   or agent trailers.
5. Let hooks run. When a hook fails, fix the cause and commit again; stage
   files a hook rewrote or generated.

Done when `git status --short` lists only the unrelated changes from step 2.

## Push

Follow the `push` skill: `skill://push` in OMP, [`../push/SKILL.md`](../push/SKILL.md) on disk.

Report: each commit's short hash and subject, the pushed range, and any files
left unstaged.
