---
name: build-mode
description: >-
  Implement a known outcome autonomously, in the smallest complete change, and
  prove it works against the real thing rather than the diff. Use when the user
  already knows what they want and has said so ("add X", "make Y do Z", "wire
  this up", "ship it"), or types /build-mode. Bounds the scope, forces
  verification of actual behaviour for UI, config, deployment and automation
  work, and ends the session cleanly when the objective drifts. Skip it when the
  request is vague or exploratory (shape the scope first), when something is
  broken and the cause is unknown (diagnose first), or for a one-line edit.
user-invocable: true
---

# Build Mode

The outcome is known. Your job is to reach it in the smallest complete change,
verify it against reality, and stop.

This is the second half of the loop. Scoping runs when the user does not yet
know what they want. This one runs when they do.

## Recognise the trigger

Enter build mode when the request names the change: "add a settings toggle",
"make the digest run at 7am", "put the Kohra greys in the tmux status bar".

Stay out of it when:

- the request is a feeling, not a change → scope it before building
- something is failing and you do not know why → diagnose before editing
- the edit is one obvious line → just make it

## Preflight: check for active work

Before the first edit, check what else is already in flight. Gate on evidence
of *active* work, not on branch age or unmerged-branch status — an unmerged
branch may be deliberately kept around, already shipped via a squashed PR, or
just ahead of a stale local base, so an old-or-unmerged signal alone fires
constantly and gets ignored.

Run `git worktree list --porcelain` and check the Linear issue state for the
task at hand, then match what you find against this table:

| Signal | Response |
|---|---|
| The current worktree is dirty and the ask is a different objective from that work | Stop. Resolve the existing work — finish, park, or explicitly abandon it — before starting the new one |
| Another linked worktree is dirty | Report it once, then continue |
| A different Linear issue is already "In Progress" | Ask: finish it, park it, or switch explicitly |
| A branch is merely unmerged, nothing else fires | Not a signal on its own — do not interrupt |
| A worktree or branch is old but clean | Report only during grooming, not mid-build |

Overrides are allowed. When a stop or a question gets overridden, record it:
append one line to `~/.claude/logs/build-mode-gate.log` (create the file and
its directory if they don't exist) with the timestamp, which signal fired,
what was chosen, and the override reason in the builder's own words. That
reason is the only place this is asked, at the moment it matters — do not
paraphrase it into something tidier.

## The pass

**1. Inspect before editing.** Read the files you are about to change, and the
ones that call them. Follow the repository's own instructions (`AGENTS.md`,
`CLAUDE.md`) and any skill they point at. An edit made on an assumption about
code you have not opened is the most expensive kind.

**2. Make the smallest complete change.** Smallest and complete are both
binding. Do not ship half the outcome, and do not widen the diff with adjacent
cleanups, renames, or "while I'm here" refactors. If you spot something genuinely
worth fixing outside the scope, say so in one line at the end and leave it.

**3. Preserve unrelated work.** Other people's changes, live state, uncommitted
edits, intentional experiments in config files. When a file may have been edited
outside the repository, diff before you overwrite.

**4. Verify the real behaviour, not the source text.** This is the step that
gets skipped. A change is not verified because the code looks right.

| Kind of work | What counts as verification |
|---|---|
| Logic, data transforms | Run the focused test, or exercise the function |
| UI | Look at it rendered, in the state the change affects |
| Configuration | Reload the consumer and confirm it took effect |
| Deployment, automation, scheduled jobs | Check the live result where access permits |
| Anything with a CLI | Run the command and read the output |

Narrow beats broad. One test that would have caught the bug is worth more than
a full suite run.

**5. Commit when the repository rules say to.** Follow the project's convention.
Do not batch several completed steps into one commit at the end.

## Ending the session

Small, coherent work stays in the current session. Write a short handoff and
tell the user to start a fresh one when any of these becomes true:

- the objective has changed from the one you started with
- the work has widened into a second unrelated area
- context is approaching the point where re-reading it dominates the cost

The handoff records the goal, what changed, what is still uncertain, and the one
next action. Nothing else.

## Report

Lead with what changed and where. Then, in this order and no longer than four
lines: what you verified and how, what remains uncertain, whether the objective
is done, and the single next action if there is one.

If it is done, say so and stop. Do not keep improving work that already meets
the stated outcome.

## Common mistakes

- Reporting "implemented and tested" when the test run was never executed, or
  when it passed for a reason unrelated to the change.
- Verifying the diff instead of the behaviour. Reading your own patch back is
  not evidence.
- Scope creep dressed as thoroughness: the fix plus three refactors, so the
  review cannot separate them.
- Continuing past "done" because there is always one more polish available.
- Carrying a drifted objective in the same session rather than handing off.
