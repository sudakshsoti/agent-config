---
name: execute-plan
description: "Use when the user points to a markdown checklist plan and wants hands-off execution: delegate independent items, choose suitable agents, verify each slice, and commit it. It orchestrates plan files; use orchestration for general worker coordination without a checklist."
allowed-tools: Read, Edit, Bash(git*), Task, Glob, Grep
---

# Execute plan

You are the **orchestrator**. Drive a checklist plan to completion by delegating
each item to a fresh subagent. Your own context stays small — that is the point.
Don't read source files, run the builds, or write the code yourself.

Plan path is in `$ARGUMENTS`; default `PLAN.md`, else glob `*PLAN*.md` and say
which one you found.

Most of what follows is calibration, not procedure. Three things are not yours to
decide: evidence before you tick a box, a commit per item, and path-limited
commits in a parallel batch. Everything else is your judgment.

## The loop

1. **Read the plan once.** Copy the unchecked items into a todo list and work from
   that. Re-read only if a worker reports the plan is wrong.
2. Dispatch the next unchecked item (file order) to a worker, or a batch of items
   that don't overlap.
3. On return: tick the boxes and commit the ticks if the workers didn't.
4. Nothing left → stop, report each item with its commit hash.

## Running in parallel

Look ahead a few items and dispatch the ones that don't touch the same files
together, as Task calls in a **single message**. Keep the fan-out small enough
that you can actually read the returns.

Serial when they'd collide, when the plan states an order, when one item consumes
another's output, or when you can't tell what an item touches. Uncertain means
serial — a collision costs more than the sequential run saves.

Parallel workers stage **by explicit path**: `git commit -- <paths> -m "…"`, never
`git add -A` or `commit -a`, which would sweep a sibling's half-written files into
the wrong commit. Path-limited commits ignore the shared index, so a lock
collision costs one retry. This one goes in every packet of a batch.

If one worker in a batch fails, the others still count — re-dispatch the failure.

Consecutive mechanical items are also worth handing to a single `haiku` worker as
an ordered list, committing per item.

## The handoff packet

The worker hasn't seen this conversation, so the packet carries everything: repo
path, plan file path, the exact item text, and what's out of scope (sibling items
or shared files it must not touch — this item only, then stop).

Say how you want the work proved and what to return: the verify output, files
changed, commit hash. Not "done". Whether that proof is a test, an existing suite
staying green, or a clean build and a read of the diff is your call, item by item
— a plan of renames doesn't need tests and a plan of behaviour changes isn't
served by a build check. If you want a test written, say which and why; a worker
here shouldn't be inventing test strategy on its own.

Tell it to stop and report rather than commit a guess: when live code contradicts
the packet, when verify keeps failing, when the item needs files outside its
scope, or when it can't produce evidence.

## Choosing the worker

Your judgment, per item: the cheapest worker that will get it right, using
whichever lever your surface gives you.

- **OMP** — the `task` role already pins the worker (GPT-5.6-Luna at `xhigh`),
  so effort is the lever, not model: drop to `smol` for mechanical items.
- **Pi** — per-job models are in each agent's frontmatter, and a dispatch can
  override both model and thinking. Use the configured lower-cost default for
  mechanical items and bounded research; reserve stronger models and higher
  effort for architecture, security and difficult implementation decisions.

If your surface won't let you set either per subagent, dispatch anyway. A fresh
context scoped to one item is most of the win; the routing is the saving on top.

Escalate when you're unsure, when the plan flags an item as risky, and when a
worker fails or comes back confused. Name what you routed to and why in a clause,
so the routing is auditable.

## Rules

- **Evidence, then the tick.** The commit is what makes each step recoverable, and
  an unverified commit isn't a checkpoint. A return with no concrete evidence is a
  failed item — re-dispatch it.
- **Trust what comes back.** Read the return; don't re-open the worker's files or
  re-run its commands. Investigating for yourself is how this skill's context
  bloats and stops being worth running.
- **Don't ask for approval between items.** Keep going.
- Stop early if an item is genuinely ambiguous or a commit fails. Say which item
  and why, and leave the plan file reflecting real progress so a later run resumes
  from the first `- [ ]`.
- Honour any dependency order or authorisation note the plan states.
