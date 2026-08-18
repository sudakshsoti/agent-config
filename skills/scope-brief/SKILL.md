---
name: scope-brief
description: >-
  Use once the target is roughly known but needs bounding - before build-mode
  when the task spans more than one session, has an ambiguous outcome, touches
  3+ subsystems, risks adjacent-feature creep, or the builder asks for scoping.
  For a lighter synthesis of what you have already discussed, with no interview,
  use `to-spec` instead.
user-invocable: true
---

# Scope Brief

A lightweight commitment document for work with real size or ambiguity.
Between open-ended exploration of what to build and `build-mode` (building a
known outcome): the target is already roughly decided, but its edges are not.

## When to use it

Any of these:

- expected to take more than one session
- the outcome is ambiguous
- it touches three or more subsystems
- there is meaningful risk of drifting into adjacent features
- the builder asks for scoping directly

None of these hold → skip straight to `build-mode`. A brief too heavy to
invoke gets skipped, which is the same as not existing.

## Step 0: search first

Before asking a single question, search the repo (and, if relevant, prior
plans and briefs) for an existing solution or partial implementation. Report
what you found. Do not ask the builder whether something like this already
exists — if they knew, they would not be scoping it.

## Step 1: interview

Two to three questions per turn, two rounds by default. Extend past two rounds
only if the answers are genuinely opening up new scope, not just running long.

After the interview (whether one round or several), write the draft
immediately. Mark anything still unresolved as an explicit assumption in the
draft rather than asking another round of open questions. Correcting a wrong
assumption in a written draft costs the builder far less than answering more
open-ended questions — let them edit the draft instead.

## Step 2: force the non-goals, don't ask for them

Do not ask "what should this NOT include?" open-endedly — people cannot
reliably enumerate their own non-goals. Instead, propose three plausible
adjacent features yourself (things a reasonable builder might assume are
included, or might be tempted to add mid-build) and add each to the scope
table below, forcing it to a status. The builder corrects the status, they
don't generate the list.

## Step 3: write the file

Save to `plans/YYYY-MM-DD-<slug>-brief.md`. Structure:

```markdown
# <Project> — Scope Brief

Status: Draft

## Goal

[One or two sentences: the outcome, not the implementation.]

## Scope

| ID  | Item                          | Status              |
|-----|-------------------------------|----------------------|
| S-1 | ...                           | Now                  |
| S-2 | ...                           | Later                |
| S-3 | ...                           | Dropped (reason)     |

IDs are stable once written — later amendments and downstream plan files cite
them (`S-3`, not "the third row"). Every row gets exactly one status: `Now`,
`Later`, or `Dropped (reason)`. The three proposed adjacent features from
step 2 are rows in this same table, not a separate list.

## Assumptions

[Points left unresolved after the interview, and what was assumed. Delete
once the builder confirms or corrects each one.]

## Amendments

| Date | Change | Reason |
|------|--------|--------|
```

## Step 4: lock, then batch-file what's deferred

**Locking is operational, not a heading.** A brief is locked when all three
are true:

1. The `Status:` line reads `Status: Locked <YYYY-MM-DD>`.
2. The file is committed.
3. Every plan file written from this brief carries `Source brief: <path>` in
   its header, plus a standing instruction to stop and ask before doing
   anything the brief's scope table doesn't cover.

Amending a locked brief means adding a row to the Amendments table and making
a new commit — never silently editing a `Now`/`Later`/`Dropped` value in
place. A brief with no amendment history but three unrecorded scope changes is
indistinguishable from one that was never locked.

Once locked, batch every `Later` row into one Linear issue via
`homelab-backlog`'s batched-capture handling: one parent issue titled
`Follow-ups from <project>`, each `Later` row as a checklist line, not one
issue per row. Never file a `Dropped` row — that's a deliberate rejection, and
it stays in the brief with its reason, not the backlog.

## Step 5: hand off and stop

Write the plan from the locked brief and stop. Do not reimplement planning
here — this skill produces the brief, not the task breakdown.
