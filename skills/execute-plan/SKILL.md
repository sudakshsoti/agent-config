---
name: execute-plan
description: Autonomously execute a multi-step checklist plan file item by item — dispatching one fresh subagent per item, routing each item to the cheapest capable model (Haiku/Sonnet/Opus) by complexity, verifying each item (test-first when it changes behavior), and committing after each. Use when the user points at a PLAN.md (or any markdown checklist) and wants it run hands-off, one slice at a time with a clean context per slice. No per-item review gate — for low-risk, mechanical checklists. When you want spec-compliance + code-quality review after each task, use subagent-driven-development instead.
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
3. **Pick the model tier** for this item (see _Choosing the model per item_ below),
   then **dispatch ONE subagent** (Task tool) with that `model` to implement
   **just that single item**. Write the dispatch as a **self-contained handoff
   packet** — assume the worker has never seen this conversation, so everything it
   needs is in the prompt:
   - **Context**: the repo path, the exact item text, and the plan file path (so it
     can read surrounding items for context, not act on them).
   - **Scope and out-of-scope**: do **only this one item**, then stop. Name the
     sibling items or shared files it must _not_ touch, so it doesn't wander.
   - **What to do**: implement the item **test-first when it changes behavior**
     (follow test-driven-development — write the failing test, watch it fail for the
     right reason, write minimal code, watch it pass; see _Verifying each item_
     below), verify, then `git commit` with a descriptive message naming the item.
   - **Verify command(s)**: the exact command to run for this item's evidence.
   - **Return format**: the observed verify evidence — the red→green test transcript,
     or the clean build/inspection result — plus the files changed and the commit
     message/hash. Not just "done".
   - **Stop conditions**: the bail-out triggers below.
4. When the subagent returns, **tick that item's box** in the plan file
   (`- [ ]` → `- [x]`) and commit that tick if it isn't already in the item's commit.
5. Go back to step 1.

### Stop conditions for the worker

Carry these into every handoff packet. The worker **stops and reports what it
found rather than committing** if:

- the live code does not match an assumption in the handoff,
- a verification command fails twice after a reasonable retry or fix,
- the item turns out to need files outside its stated scope,
- it cannot produce concrete evidence for its claim.

A worker that stops here isn't a failure — it's a worker refusing to commit a
guess. When one comes back stopped, you decide: re-dispatch one tier higher (see
_Retry up a tier on failure_), amend the item, or halt the run (see _Stop early
only_ under Rules). Do not tick the box.

## Choosing the model per item

You (the orchestrator) run on the strong model; the _worker_ model is a per-item
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
  returns confused/incomplete, re-dispatch the _same_ item one tier higher before
  giving up. Note the escalation when you report.
- **State your pick.** In your per-item narration, say which tier you routed to
  and why (one clause), so the routing is auditable.

## Verifying each item

Borrowed from **test-driven-development**: "verify" is not "it looks right" — it is
_observed evidence_ that the item does what it should. What that takes scales with the
item, along the same line as the model tiers:

- **Behavior change** (new logic, a feature slice, a bug fix — usually your `sonnet`
  / `opus` items): the subagent follows **test-driven-development**. Write the failing
  test first, watch it fail _for the right reason_ (feature missing, not a typo), write
  the minimal code, watch it pass, and keep the rest of the suite green. A test written
  after the code that passes on its first run proves nothing — the subagent must have
  _seen_ red before green.
- **No behavior change** (renames, config/version bumps, file moves, formatting, copy
  edits — usually your `haiku` items): there is no behavior to test. Verify by the fitting
  observation — the build succeeds, the app/serve still starts, and the diff is exactly
  the intended change and nothing else.

Either path, the output must be **pristine** — no stray errors or warnings — and the
subagent **returns its evidence** (the red→green transcript, or the build/inspection
result). You tick the box and trust the commit only once that evidence is in hand: a
commit without observed evidence is not a checkpoint, it's a guess.

Don't force a test onto a mechanical item, and don't wave a behavior item through on
"I inspected it" — match the discipline to the item.

## Rules

- **One item at a time, in file order.** Never run items in parallel — sibling
  items often share files and would collide.
- **Route by cost, verify regardless.** The model tier changes per item, but the
  verify + commit checkpoint does not — and verify means _observed evidence_ (a test
  seen failing then passing for behavior changes; a clean build/inspection for
  mechanical ones), not a glance. A Haiku item is still verified and committed like
  any other.
- **Never skip** the verify or the commit. The commit is the checkpoint that makes
  each step recoverable — and an _unverified_ commit is not a checkpoint.
- **Inspect the evidence, don't just forward it.** What the worker returns is
  evidence to check, not a verdict to trust. Scale the check to the item's risk:
  for a high-stakes `opus`/`sonnet` item, reopen a cited file, skim the diff, or
  re-run the verify that matters before you tick the box; a mechanical `haiku` item
  can be trusted on its returned evidence. Same principle as _match the discipline
  to the item_ — a glance at the transcript is not a review.
- **Do not ask for approval between items.** Keep going autonomously.
- **Stop early only** if an item is genuinely ambiguous, a verification fails, or a
  commit fails. When you stop, say exactly which item and why, and leave the plan
  file reflecting real progress so a later run can resume from the first `- [ ]`.
- If the plan notes a dependency order or an authorisation requirement for an item,
  honour it and carry it into the subagent's instructions (e.g. commit-message notes).
