---
name: workstreams
description: "Use in Pi or OMP when a larger approved implementation needs multiple workstreams with dependencies, exclusive edit ownership, blockers, and an integration gate. Uses specialist-delegation for worker dispatch; not for trivial edits or a second execution loop over an execute-plan checklist."
compatibility: "Pi with the Agent subagent tool, or OMP with the task tool; no named workflow feature or external coordinator required."
---

# Workstreams

Coordinate an approved implementation as a small dependency graph. The main
session retains responsibility for requirements, technical synthesis, scope,
integration, and the final claim of completion. A workflow is a coordination
method here, not a requirement to enable a runtime feature.

## Gate: is coordination worth it?

Use this skill when there are multiple coherent deliverables and at least one
real coordination need: dependent interfaces, independent sizeable edits,
separate specialist proof, or a shared integration gate.

Do the work directly for a one-file change, tightly coupled edits, or work whose
briefings cost more than the implementation. Several independent lookups need
only `specialist-delegation` (`skill://specialist-delegation`, [on disk](../specialist-delegation/SKILL.md)). Serial
execution is a valid outcome; do not invent parallelism to justify a workflow.

Before dispatch:

1. Read project instructions, inspect the relevant implementation and tests,
   and record `git status --short`. Preserve existing dirty work.
2. Establish acceptance criteria, approved behavior changes, and exclusions.
   Ask about materially different interpretations; do not outsource a missing
   product or security decision.
3. Identify the smallest useful slices, their interfaces, write sets, and proof.
   Review the proposed plan with `self-review`; use `peer-review` when requested
   or justified by risk. These review skills retain their own contracts.
4. State the coordinator, integration owner, ownership map, and initial ready
   batch before launching writers. Do not create a permanent plan file unless
   required by the task or repository convention.

## Pick one coordinator

Normally the main session coordinates and dispatches implementation specialists
using `specialist-delegation`. Do not create a second scheduler for the same
work or let workers recursively build their own fleets.

The configured `workflow` agent is an optional owner of one disjoint approved
slice, not a mandatory orchestrator. This repository currently restricts its
children to `Plan`, `Explore` and `scout` in Pi, and to `plan`
and `scout` in OMP (its `spawns` list); its instructions
permit only discovery/planning delegation. It can implement its assigned slice
itself and return evidence, but cannot be told to dispatch `code-worker` or
`builder`. Read the active role before use; do not bypass its allowlist or edit
configuration to expand its authority.

In Pi, fan-out and sequencing run through the `workflow` tool (pi-dynamic-workflows:
`phase()`, `pipeline()`, `parallel()`); its model tiers live in
`pi/workflows/model-tiers.json`. OMP has no separate workflow runtime to enable. These are
current configuration facts, not permanent requirements; inspect active role
and tool definitions rather than assuming source paths exist in the target
project. Ordinary Agent (Pi) or task (OMP) calls
are sufficient for this method; do not enable workflow settings or assume a
workflow/DAG runtime API exists. Use available task tracking and delegation tools.

## Model deliverables and blocking edges

Keep one small ledger, in a todo list or the existing approved plan:

| ID | Deliverable and acceptance proof | Write owner / paths | Blocked by | State / result |
| --- | --- | --- | --- | --- |
| A | Shared response contract plus compatibility tests | Main: contract file, contract tests | — | Ready |
| B | Service adapter implements accepted contract | code-worker: adapter, unit tests | A accepted | Pending |
| C | Client consumes accepted contract | builder: client view, component tests | A accepted | Pending |
| D | End-to-end error and success paths pass | Main: integration tests | B and C integrated | Pending |

These are illustrative roles and paths, not a prescription for every task.
B and C may run together only once A is verified and visible to both. Docs or
read-only discovery may run earlier if their evidence does not depend on A.

For each slice record:

- Outcome, approved decisions, inputs, and explicit non-goals.
- Exactly one write owner and allowed files, including tests and reports.
- Dependencies with a release condition: “contract accepted at revision X,”
  not just “after backend.” A return alone does not release the edge.
- Worker, Agent ID, execution location/base revision, and verification commands.
- Status and evidence: pending, running, returned-awaiting-verification,
  blocked, or accepted. Map these to available todo fields; put blocked reasons
  in descriptions rather than inventing unsupported status values. If the todo
  tool allows one in-progress item, track the current coordination batch there
  and record individual worker states in its description.

Remove dependency cycles before dispatch: pull the shared contract into a
preceding slice, combine coupled work, or execute it sequentially. An uncertain
write set or interface is a blocking edge, not permission to speculate.

## Prevent conflicting edits

**Shared checkout:** one active writer per file, including the parent. Reserve
shared schemas, manifests, lockfiles, registries, generated outputs, and common
test fixtures for the integration owner. Read-only work may coexist with
writers, but record the revision/state reviewed and invalidate stale conclusions.
Workers must stop before expanding their write set. Serialize formatters,
codegen, snapshot updates, or tests that mutate shared fixtures or use the same
exclusive external resource.

**Isolated worktrees:** use only when the live delegation tool supports them and the
repository permits them. An isolated worker sees the committed base, not the
parent's uncommitted changes. Do not dispatch dependent work until its required
inputs exist in that base, or choose serial shared-checkout execution. Never
commit unrelated dirty files just to make a worktree see them.

The delegation tool may return a committed branch and remove its temporary worktree
on completion. Explain that impact before using isolation; preserve the returned
branch/commit and inspect it before integration. Isolation prevents concurrent
filesystem writes, not semantic conflicts or inconsistent shared interfaces.
Do not assume isolated output is already in the main checkout.

By default, workers do not stage, commit, push, merge, rebase, reset, or clean.
One integration owner performs authorized Git operations after writers are
quiescent, using explicit paths and preserving unrelated work. If an approved
execution mode requires commits, state that policy in every packet; never
sweep sibling changes with `git add -A` or `commit -a`.

## Dispatch and advance only ready work

Use the packet and role selection in `specialist-delegation`; add the slice
ID, accepted upstream revision, exclusive write paths, integration owner, and
stop conditions. Bound both the work and the expected return.

1. Select a small ready batch with satisfied dependencies and disjoint writes.
2. Send independent delegation calls in a single message (in OMP, one `task`
   call with several `tasks` entries); explicitly choose
   background execution when useful work remains.
3. Record IDs, then work on a non-overlapping task. Do not duplicate a worker's
   investigation or poll for background results; consume completion notices.
4. Inspect each returned artifact/diff and narrow verification evidence. Ask
   for missing proof or a scoped correction before accepting the slice.
5. Integrate accepted changes in dependency order. For isolated work, inspect
   the returned branch/commit against its base before applying it. Resolve
   semantic conflicts against the approved contract, not by blindly choosing
   either side of a merge.
6. Verify the integrated result, update the ledger immediately, and release
   newly satisfied edges. A worker-local pass is not the integration gate.

## Handle blockers without losing ownership

- **Scope/interface change:** stop dependent dispatches, decide centrally, update
  the contract and packets, and reverify affected accepted work. Ask the user if
  the decision changes requirements, authorization, or production impact.
- **Worker needs another owner's file:** have it return the proposed change;
  serialize the edit or reassign ownership only after the prior writer stops.
- **Failed check:** distinguish implementation failure from missing environment
  or credentials. Return a specific correction or report the environment
  blocker. Never weaken checks or fabricate passing evidence.
- **Repeated failed approach:** inspect the failed assumption, reduce the slice
  or escalate judgment. Do not keep resubmitting the same vague task.
- **Unresponsive/running worker:** use available steering/status semantics. Do
  not assume a steering message cancels it. Confirm it can no longer write
  before assigning its paths to a replacement or editing them yourself.
- **One stream fails:** keep independent verified work, block its dependents,
  and report partial progress honestly. Do not mark the failed slice complete.
- **Integration fails:** record the failing tree or commit and retain worker
  artifacts. Mark affected acceptance evidence stale and re-block downstream
  edges, including already accepted dependents. Repair forward within approved
  scope, or have the integration owner reverse only the failed integration
  changes with authorization, in reverse dependency order where needed. Never
  reset or clean unrelated work to recover; re-run the gate before re-accepting.

## Close the integration gate

Before reporting completion:

- Account for every worker; no active writer may mutate the reviewed result.
- Inspect the combined diff for scope, shared-contract compatibility, accidental
  files, secrets, and unrelated changes.
- Run relevant format/lint, diagnostics or type checks, unit/regression tests,
  and tests crossing stream boundaries against the final integrated tree.
  For UI, retain vibe's rendered-state and screenshot requirements.
- Use the applicable review workflow on a stable revision; address findings and
  re-run affected checks. Review is not a substitute for tests or integration.
- Mark accepted items complete only after their proof is satisfied. Report
  changed files, checks/results, unresolved blockers and uncertainty, and any
  authorized commits. Never call a partial or unverified implementation done.

## Relationship to existing workflows

`execute-plan` remains agent-agnostic and owns hands-off execution of a supplied
Markdown checklist with per-item checkpoints. Do not run its item loop and this
scheduler simultaneously. Under execute-plan, apply the ownership and dependency
checks here to its next checklist batch; do not create a separate ledger or
launch an additional coordinator. Its checklist and per-item checkpoints remain
the sole progress mechanism. When explicit cross-stream coordination is needed,
choose this skill as the execution mode and state the choice; do not silently
change an explicitly requested execute-plan or commit policy.

Both modes use specialist-delegation's acceptance verification for individual
workers. Execute-plan's delegation rule makes that verification explicit; the final
cross-stream integration gate above is additional proof, not a duplicate worker
review.

Normal implementation, `diagnosing-bugs`, and TDD still govern work inside each
slice. `vibe` owns the UI plan/build/critic sequence; `self-review`, `peer-review`,
and `code-review` retain their distinct review purposes. Do not duplicate their
loops or treat a visual Critic as an engineering reviewer. Session-continuity
notes belong to `handoff`, not to every worker dispatch.
