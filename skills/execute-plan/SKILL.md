---
name: execute-plan
description: Autonomously execute a multi-step checklist plan file item by item — dispatching one fresh subagent per item, routing each item to the cheapest capable model (Haiku/Sonnet/Opus) by complexity, and committing after each. Use when the user points at a PLAN.md (or any markdown checklist) and wants it run hands-off, one slice at a time with a clean context per slice. No per-item review gate — for low-risk, mechanical checklists. When you want spec-compliance + code-quality review after each task, use subagent-driven-development instead.
allowed-tools: Read, Edit, Bash(git*), Task, Glob, Grep
---

# Execute plan

You are the **orchestrator** for a checklist-style plan file. Your job is to drive
the plan to completion one item at a time, keeping your own context small by
delegating each item's real work to a fresh subagent.

## Which plan file

The plan path is in the invocation arguments: `$ARGUMENTS`.
If empty, default to `PLAN.md` in the current directory (glob for `*PLAN*.md` if
that's missing, and confirm which one you found).

## The loop

Repeat until every checkbox is ticked:

1. **Read** the plan file. Find the **first unchecked** item (`- [ ]`).
2. If **no unchecked items remain** → stop. Report a summary: every item done and
   its commit hash (`git log --oneline`).
3. **Pick the model tier** for this item (see *Choosing the model per item* below),
   then **dispatch ONE subagent** (Task tool) with that `model` to implement
   **just that single item**:
   - Pass it the exact item text plus the plan file path for surrounding context.
   - Instruct it to: implement the change, verify it (test / serve / inspect as
     appropriate), then `git commit` with a descriptive message naming the item.
   - It must do **only this one item** and then stop.
4. When the subagent returns, **tick that item's box** in the plan file
   (`- [ ]` → `- [x]`) and commit that tick if it isn't already in the item's commit.
5. Go back to step 1.

## Choosing the model per item

You (the orchestrator) run on the strong model; the *worker* model is a per-item
decision. Read the item, then pick the **cheapest tier that can do it correctly**:

- **`haiku`** — trivial, mechanical, no judgment: renames, string/copy edits,
  bumping a version or config value, moving/deleting files, formatting,
  boilerplate, single-line changes with an obvious answer.
- **`sonnet`** — standard, well-specified work: a normal feature slice, a
  straightforward refactor, writing tests for defined behavior, wiring that
  follows an existing pattern in the repo.
- **`opus`** — ambiguous, cross-cutting, or high-stakes: anything touching
  architecture or public interfaces, tricky logic or concurrency,
  security-sensitive code, or an item whose scope you can't pin down from the text.

Rules of thumb:
- **When unsure, escalate one tier.** A wrong cheap answer costs more than a
  right expensive one.
- **Honor the plan's own signals.** If the plan flags an item as risky, complex,
  or dependency-laden, floor it at `sonnet` (or `opus` for architecture).
- **Retry up a tier on failure.** If a Haiku/Sonnet worker's verify fails or it
  returns confused/incomplete, re-dispatch the *same* item one tier higher before
  giving up. Note the escalation when you report.
- **State your pick.** In your per-item narration, say which tier you routed to
  and why (one clause), so the routing is auditable.

## Rules

- **One item at a time, in file order.** Never run items in parallel — sibling
  items often share files and would collide.
- **Route by cost, verify regardless.** The model tier changes per item, but the
  verify + commit checkpoint does not — a Haiku item is still verified and committed
  like any other.
- **Never skip** the verify or the commit. The commit is the checkpoint that makes
  each step recoverable.
- **Do not ask for approval between items.** Keep going autonomously.
- **Stop early only** if an item is genuinely ambiguous, a verification fails, or a
  commit fails. When you stop, say exactly which item and why, and leave the plan
  file reflecting real progress so a later run can resume from the first `- [ ]`.
- If the plan notes a dependency order or an authorisation requirement for an item,
  honour it and carry it into the subagent's instructions (e.g. commit-message notes).
