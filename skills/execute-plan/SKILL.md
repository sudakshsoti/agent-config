---
name: execute-plan
description: Autonomously execute a multi-step checklist plan file item by item — dispatching one fresh subagent per item and committing after each. Use when the user points at a PLAN.md (or any markdown checklist) and wants it run hands-off, one slice at a time with a clean context per slice.
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
3. **Dispatch ONE subagent** (Task tool) to implement **just that single item**:
   - Pass it the exact item text plus the plan file path for surrounding context.
   - Instruct it to: implement the change, verify it (test / serve / inspect as
     appropriate), then `git commit` with a descriptive message naming the item.
   - It must do **only this one item** and then stop.
4. When the subagent returns, **tick that item's box** in the plan file
   (`- [ ]` → `- [x]`) and commit that tick if it isn't already in the item's commit.
5. Go back to step 1.

## Rules

- **One item at a time, in file order.** Never run items in parallel — sibling
  items often share files and would collide.
- **Never skip** the verify or the commit. The commit is the checkpoint that makes
  each step recoverable.
- **Do not ask for approval between items.** Keep going autonomously.
- **Stop early only** if an item is genuinely ambiguous, a verification fails, or a
  commit fails. When you stop, say exactly which item and why, and leave the plan
  file reflecting real progress so a later run can resume from the first `- [ ]`.
- If the plan notes a dependency order or an authorisation requirement for an item,
  honour it and carry it into the subagent's instructions (e.g. commit-message notes).
