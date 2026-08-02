---
name: execute-plan
description: Autonomously execute a markdown checklist plan file — one fresh subagent per item, routed to the cheapest model that can do it (haiku/sonnet/opus), run in parallel where items don't overlap, verified and committed after each. Use when the user points at a PLAN.md (or any markdown checklist) and wants it run hands-off with a clean context per slice. Deliberately light — no per-item review gate, no TDD protocol inlined. For rigorous work, tell the worker to use superpowers:test-driven-development; for spec-compliance plus code-quality review after each task, use subagent-driven-development instead.
allowed-tools: Read, Edit, Bash(git*), Task, Glob, Grep
---

# Execute plan

You are the **orchestrator**. Drive a checklist plan to completion by delegating
each item to a fresh subagent. Your own context stays small — that is the point.
Do not read source files, run the builds, or write the code yourself.

Plan path is in `$ARGUMENTS`; default `PLAN.md`, else glob `*PLAN*.md` and say
which one you found.

## The loop

1. **Read the plan once.** Copy the unchecked items into a todo list and work from
   that. Do not re-read the whole file every iteration — re-read only if a worker
   reports the plan is wrong.
2. For the next unchecked item (file order), **pick a worker model** and dispatch
   **one** subagent for **that item only**.
3. On return: tick the box (`- [ ]` → `- [x]`) and commit the tick if the worker
   didn't. Next item.
4. No items left → stop, report each item with its commit hash.

**Batch trivial runs.** Consecutive items that are all mechanical and touch
disjoint files can go to a single `haiku` worker as an ordered list, committing
per item.

## Running items in parallel

Your judgment. Look ahead at the next few unchecked items and dispatch them
together — all Task calls in a **single message** — when you can see they don't
overlap. Three or four at a time; past that the returns get hard to read.

Overlap means the same file, not the same area. Also serial if: the plan states a
dependency order, a later item builds on an earlier one's output, the items share
a test fixture / port / database / snapshot file, or you simply can't tell what an
item touches. **Uncertain means serial** — a collision costs more than the
sequential run saves.

Parallel workers must stage **by explicit path**: `git commit -- <paths> -m "…"`,
never `git add -A` or `commit -a`, which would sweep a sibling's half-written
files into the wrong commit. Path-limited commits ignore the shared index, so a
lock collision is at worst one retry. Put that instruction in every packet of a
parallel batch.

Tick the whole batch's boxes in one edit when the batch returns. If one worker in
a batch fails, the others still count — re-dispatch just the failure.

## The handoff packet

The worker has not seen this conversation. Keep the packet short but complete:

- **Repo path, plan file path, and the exact item text.**
- **Scope**: this item only, then stop. Name sibling items or shared files it must
  not touch.
- **Verify command**: the exact command that produces evidence for this item.
- **Rigour**: for anything that changes behaviour, tell it to use
  `superpowers:test-driven-development` — red before green, seen not assumed. For
  mechanical items say so explicitly, so it doesn't invent tests.
- **Return**: verify output, files changed, commit hash. Not "done".
- **Stop instead of committing** if: live code contradicts the packet, verify fails
  twice, the item needs files outside scope, or it can't produce evidence.

Then commit with a message naming the item — path-limited (`git commit -- <paths>`)
whenever the item ran as part of a parallel batch.

## Choosing the worker model

Your judgment, per item, cheapest tier that will get it right:

- **`haiku`** — no judgment in it: renames, copy/config/version edits, file moves,
  formatting, boilerplate.
- **`sonnet`** — the default. Normal feature slices, straightforward refactors,
  tests for defined behaviour, wiring that follows an existing pattern.
- **`opus`** — architecture, public interfaces, tricky logic, security-sensitive
  code, or an item whose scope you can't pin down from its text.

Escalate one tier when unsure, when the plan flags an item as risky, and when a
worker fails or comes back confused (re-dispatch the same item higher). Say the
tier and a one-clause reason in your narration, so routing is auditable.

## Rules

- **Never skip verify or commit.** The commit is the recoverable checkpoint; an
  unverified commit is not one.
- **Trust returned evidence.** Read what the worker returned; don't re-open its
  files or re-run its commands. If the return has no concrete evidence, that's a
  failed item — re-dispatch, don't go investigate it yourself.
- **Don't ask for approval between items.** Keep going.
- **Stop early only** if an item is genuinely ambiguous or a verify/commit fails.
  Say which item and why, and leave the plan file reflecting real progress so a
  later run resumes from the first `- [ ]`.
- Honour any dependency order or authorisation note the plan states, and carry it
  into the packet.
