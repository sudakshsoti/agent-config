# Build Loop Repair Plan (v2)

**Date:** 2026-08-06
**Repo:** `~/dev/agent-config` (branch `dazzling-mellow-drift`)
**Status:** Proposal. One prerequisite landed (section 4). v1 received an
external adversarial review with verdict "fix before shipping"; this version
incorporates it. Section 7 lists what changed and what I pushed back on.

> **For a reviewing model:** written to be read cold, no repo access needed.
> Section 7 tells you what the previous review already caught, so you can spend
> your attention elsewhere. Open questions are in section 9.

---

## 1. Context

**Who.** A solo builder. Senior UX designer, not a professional engineer. Ships
side projects and homelab tooling through Claude Code and Codex. Has ADHD, which
matters for one reason: anything not on screen is forgotten, and an idea with no
safe place to go tends to get acted on immediately.

**What this repo is.** A configuration repo for AI coding agents. Its main
contents are *skills*: directories holding a `SKILL.md` of markdown with YAML
frontmatter (`name`, `description`). The agent reads every installed skill's
description each turn and decides which bodies to load. A skill is therefore both
an instruction and a routing target competing for the same triggers.

**Install.** `install.sh` symlinks `skills/<name>/` into `~/.claude/skills/` and
`~/.agents/skills/`. The repo is the live source, so editing a `SKILL.md` takes
effect immediately on both surfaces. Consequence for any retirement: moving a
skill directory leaves a dangling symlink until `install.sh` runs again, and
edits made inside a git worktree are not live because the symlinks resolve to
the main checkout.

**Two surfaces, asymmetric controls.** Claude Code supports a `skillOverrides`
map in `settings.json` to switch a skill off. Codex has no per-skill disable,
caps total skill content at 2% of context, and truncates all descriptions once
that fills. An unused skill is therefore not free on Codex. The repo's real
retirement mechanism is moving a directory to `skills/_archive/`, which is not
installed but stays in git.

**Hygiene.** A pre-commit hook validates frontmatter and checks `dist/<name>.zip`
freshness. Plans live in a tracked `plans/` at the repo root.

**Inventory.** 39 installed skills, 13 vendored from the "superpowers"
collection and adopted wholesale rather than written for this setup.

---

## 2. The pain point

In the builder's own words:

> "I'm too confused and run it too many directions then I find myself building
> 5 features at once which all break."

They believed a PRD-writing skill was the fix.

### 2.1 Two distinct failures, not one

**Failure A: concurrency.** Too many active objectives at once.

**Failure B: isolation.** Large uncommitted changes, no checkpoints, no
verification between slices, unclear test boundaries.

These are independent. Five projects in five clean worktrees, each committed at
green, do not produce ambiguous breakage. One project with five interleaved
uncommitted changes does. A fix that only limits concurrency can be fully
complied with while still accumulating one large inseparable change, and the
"everything breaks" symptom survives.

v1 of this plan collapsed B into A and treated it as a downstream symptom. That
was wrong. Both need a mechanism.

**Failure C: scope size.** A project started without a defined edge, so a
two-day task becomes twenty. This is the one a scoping document actually fixes,
and it is the least of the three by cost.

### 2.2 The cause of task switching is a hypothesis, not a finding

The working hypothesis is: *an idea arriving mid-build has nowhere safe to go, so
it gets built rather than written down, because writing it down feels like
losing it.*

Plausible, unproven, and not the only candidate. Alternatives:

- boredom once implementation turns tedious
- uncertainty about the next step
- escape from a failing test or a hard decision
- novelty seeking
- tasks too large to produce frequent completion signals
- the agent itself proposing adjacent improvements mid-build

A backlog handoff helps the first explanation and nothing else. If the real
driver is escape-from-difficulty, capture solves nothing and the WIP gate
becomes an obstacle to route around.

**This plan therefore ships an instrumented experiment, not a settled fix.** The
instrumentation is described in section 6 and is designed to require no
journaling, because a two-week manual diary is exactly the kind of high-friction
ritual this plan exists to avoid.

---

## 3. Current state of the build loop

| Stage | Skills claiming it |
|---|---|
| Capture an idea | `homelab-backlog` (Linear) |
| Pick what to work on | `homelab-backlog` |
| Decide what the thing is | `brainstorming` (V) |
| Break into steps | `writing-plans` (V) |
| Check the plan | `self-review`, `peer-review` |
| Build | `build-mode`, `execute-plan`, `executing-plans` (V), `subagent-driven-development` (V), `dispatching-parallel-agents` (V), `using-git-worktrees` (V) |
| Prove it works | `test-driven-development` (V), `verification-before-completion` (V), `systematic-debugging` (V), `requesting-code-review` (V), `receiving-code-review` (V), `maintainability-review` |
| Ship | `commit`, `push`, `pr`, `merge`, `finishing-a-development-branch` (V) |
| Return later | `orient`, `handoff`, `explain-this` |

`(V)` = vendored.

Two structural gaps, both absent from every skill above:

- **No work-in-progress limit.** Nothing checks whether unfinished work exists
  before starting new work.
- **No connection between scoping and capture.** Nothing turns "we decided not
  to do this" into a backlog item, so deferral equals deletion.

A third observation, **held as unproven**: several stages have multiple
claimants, so routing may be nondeterministic. Trigger overlap on paper is not
evidence of an actual routing failure. See section 5.7.

---

## 4. Already done

Commit `4771b20` deleted `discovery-first`. It existed to stop Codex jumping
straight to solutions and overlapped the scoping stage introduced here.
References in `build-mode` and the skills README were removed. It stays live on
both surfaces until this branch merges into the main checkout and `install.sh`
re-runs.

---

## 5. Proposal

Seven changes. 5.1 to 5.5 are the experiment. 5.6 is required plumbing. 5.7 is
the one place I did not accept the review in full.

### 5.1 A global WIP invariant

`build-mode` is bypassable: work can start without invoking any skill. So the
invariant goes into the global agent instructions where it is always loaded, and
the detailed procedure stays in `build-mode`.

> Before editing, check the current worktree and the active issue. Do not begin
> a second objective without explicitly parking or finishing the first.

Nothing short of a git hook or wrapper is genuinely unbypassable. This is the
most reliable placement available without one.

**Effort:** 5 minutes.

### 5.2 A `build-mode` preflight on the right signals

v1 proposed gating on unmerged local branches and branch age. That signal is
wrong. An unmerged branch may be deliberately retained, abandoned, already
merged via a squashed PR, checked out elsewhere, or merely ahead of a stale local
base. A useful old branch and a dead one look identical.

Gate on evidence of *active* work instead, via `git worktree list --porcelain`
plus Linear state:

| Signal | Response |
|---|---|
| Current worktree dirty, and the ask is a different objective | Stop and resolve |
| Another linked worktree is dirty | Report once, allow continuation |
| A different Linear issue is already `In Progress` | Ask: finish, park, or switch explicitly |
| Branch merely unmerged | Do not interrupt |
| Old but clean worktree or branch | Report only during grooming |

Overrides are allowed and **recorded** (see 6.1). If most sessions override, the
threshold is wrong and the gate gets retuned or removed.

**Effort:** 20 minutes.

### 5.3 Checkpoint and verification expectations

The mechanism for failure B, missing from v1 entirely.

Added to `build-mode`: each slice ends at a committed, verified state before the
next begins. Concretely, commit at every green point rather than batching a
multi-step change into one commit at the end, and run the actual verification
for the surface being changed before moving on, not a reading of the diff. This
already exists as a stated preference in the global instructions but has no
enforcement point in any skill.

**Effort:** 15 minutes.

### 5.4 A tiered `scope-brief` skill

Renamed from `prd-builder`. The full apparatus (goals, non-goals, success,
definition of done, constraints, tripwire, amendments, open questions) is
right for a multi-session project and absurd for a small known change. A skill
too heavy to invoke gets skipped, which is the same as not existing.

**Activation criteria.** Use the brief when any of these hold:

- expected to take more than one session
- the outcome is ambiguous
- it touches three or more subsystems
- there is meaningful adjacent-feature risk
- the builder asks for scoping

Otherwise go straight to `build-mode`.

**Workflow.**

- **Step 0.** Search for an existing solution first, then report. Do not ask the
  builder whether something already exists; they would not be scoping it if they
  knew.
- **Step 1.** Interview, two to three questions per turn, **two rounds by
  default**, extendable if the answers are genuinely opening up. Then write the
  draft with unresolved points marked as assumptions and let the builder correct
  the document. Correcting a wrong draft costs far less activation energy than
  answering open questions.
- **Step 2.** Non-goals are not asked open-endedly. The skill proposes three
  plausible adjacent features itself and forces each to a status. People cannot
  reliably enumerate their own non-goals.
- **Step 3.** Write to `plans/YYYY-MM-DD-<slug>-brief.md`.
- **Step 4.** Lock (defined below), then batch-file the deferred items (5.5).
- **Step 5.** Hand off to `writing-plans` and stop. Do not reimplement planning.

**Scope table.** One status column, not three boolean ones, and stable IDs so
amendments and plan files can cite `S-3` or `L-2`:

| ID | Item | Status |
|---|---|---|
| S-1 | ... | Now |
| S-2 | ... | Later |
| S-3 | ... | Dropped (reason) |

**Description field.** When-to-use only, no workflow summary, under 40 words.
The repo's own skill-authoring guidance documents that a description summarising
the workflow becomes a shortcut agents take instead of reading the body. Codex
also truncates long descriptions, degrading the whole catalogue.

**What "locked" means operationally.** A heading does not create a lock. Locked
means: `Status: Locked <date>` in the file, the file committed, and the plan file
produced by `writing-plans` carrying `Source brief: <path>` in its header plus a
standing instruction to stop and ask when out-of-scope work appears. Amending
requires a new row in the amendments table and a new commit. That gives a
checkable definition and a visible drift record, because three individually
reasonable amendments are what a twenty-day spiral is made of.

**Effort:** 30 minutes.

### 5.5 Capture only what was deferred, batched, with a retrieval path

Three corrections to v1's design:

**File `Later` only, never `Dropped`.** Dropped means deliberately rejected.
Filing rejections reverses the decision and gradually makes the backlog
untrustworthy. Rejections stay in the brief with their rationale, which is where
they are useful.

**Batch into one parent issue.** Four cuts must not cost four round trips.
Create one Linear issue, `Follow-ups from <project>`, with a checklist. Split
individual items out during grooming only when one becomes a credible candidate.

**Guarantee resurfacing.** Capture without retrieval is a graveyard, not a
promise, and the builder will learn that within a month. `homelab-backlog`
already runs weekly grooming and a "what should I work on" query; both must
include follow-up parent issues explicitly.

**Effort:** 20 minutes, mostly in `homelab-backlog`.

### 5.6 Correct the plan path

`writing-plans` writes to `docs/superpowers/plans/`. The repo convention and the
global instructions say `plans/` at the repo root. Folded in here because the
`scope-brief` handoff depends on it.

**Effort:** 5 minutes.

### 5.7 Narrow `brainstorming`'s description. Do not retire anything.

v1 proposed retiring seven skills. The review's objection is correct: trigger
overlap on paper is not evidence of a routing failure, and several of the pairs
I called duplicates are plausibly distinct (`requesting-` and
`receiving-code-review` are opposite sides; `finishing-a-development-branch` is
an integration decision, not implementation; `execute-plan` and
`subagent-driven-development` may differ in review rigour). The retirement
campaign is deferred until there is observed evidence, and any retirement will
need a named replacement plus a check for dangling symlinks.

**The one exception.** `brainstorming` opens with "You MUST use this before any
creative work" and gates all implementation behind a verbally approved design.
`scope-brief` fires on the same trigger with a weaker imperative and will lose,
which is not a speculative collision. Rather than archive it, narrow its
description now so the two do not compete: `brainstorming` for exploring
possible designs, `scope-brief` for committing to one outcome. That is the
review's own "narrow conflicting descriptions" remedy, applied to the single
case where the collision is certain rather than theoretical.

**Effort:** 10 minutes.

**Net inventory:** 39 skills to 40. One added, none retired in this pass.

---

## 6. Instrumentation and falsification

The hypothesis in 2.2 needs testing, but a manual two-week diary will not be
kept. Everything below is a by-product of the mechanisms themselves.

### 6.1 What gets recorded for free

- **The gate log.** Each preflight appends one line to a local log: what fired,
  what was chosen (finish / park / override), and the override reason. This
  yields gate frequency and override rate directly.
- **The override reason is the experiment.** It is the only place the builder is
  asked *why* they are switching, at the exact moment they switch. Fear of
  losing an idea, boredom, and escape-from-failure look different in that field.
  That field, not a diary, distinguishes the competing explanations in 2.2.
- **Concurrency.** Count of dirty worktrees, sampled in the same log line.
- **Capture volume.** Checklist length on `Follow-ups from <project>` issues.
- **Retrieval rate.** How many follow-up items get promoted during grooming.
  Linear timestamps this already.
- **Scope drift.** Rows in each brief's amendments table.

### 6.2 Evidence that would falsify this plan

- Ideas get captured reliably and switching continues anyway. The hypothesis in
  2.2 is wrong; look at 5.3 and task size instead.
- Most switches follow an error or a hard implementation step. The driver is
  escape, not capture. Smaller slices and better failure recovery matter more
  than any of this.
- Follow-up items are never promoted. Capture is a graveyard; stop filing.
- The gate is overridden in most sessions. The threshold is wrong, or the
  invariant does not match how the builder actually works.
- The brief is skipped. Activation cost is still too high even tiered; cut it
  further or drop it.

Review after two weeks of real use, not on a calendar date.

---

## 7. What changed from v1, and what I did not accept

**Accepted in full:**

1. Isolation split out as a separate failure with its own mechanism (5.3). This
   was the strongest catch; v1 treated it as a symptom.
2. Task-switching cause demoted from finding to hypothesis, with alternatives
   named (2.2) and an instrumented test (6).
3. Branch-age and unmerged-branch signals replaced with dirty-worktree and
   active-issue signals (5.2). v1's signal would have fired constantly in a repo
   that uses worktrees routinely, and alarm fatigue would have killed it.
4. Overrides recorded rather than merely permitted (5.2, 6.1).
5. Invariant moved to global instructions since `build-mode` is bypassable (5.1).
6. `Dropped` items no longer filed (5.5).
7. Deferred items batched into one parent issue (5.5).
8. Explicit retrieval path required (5.5).
9. Tiered activation criteria; the brief is not for every change (5.4).
10. Renamed `prd-builder` to `scope-brief`.
11. Step 0 searches instead of asking (5.4).
12. Two interview rounds as default, not hard cap (5.4).
13. One status column with stable IDs instead of three columns (5.4).
14. Operational definition of "locked" (5.4).
15. Retirement campaign deferred pending evidence (5.7).
16. Dangling-symlink check noted as a precondition of any future archiving (1, 5.7).

**Pushed back on, with reasons:**

1. **The two-week measurement protocol.** The review proposes recording seven
   metrics for two weeks. For this builder that is precisely the high-friction
   ritual the review criticises in its own section 4, and it will not be kept.
   Replaced with automatic instrumentation (6.1), where the gate's override
   reason field doubles as the instrument for the competing explanations. Same
   evidence, no diary.
2. **"Do not touch the other skills at all."** Accepted for all but one.
   `brainstorming`'s collision with `scope-brief` is certain, not hypothetical,
   because it asserts a MUST gate over the identical trigger and saves no
   artefact. Narrowing its description is the review's own recommended remedy;
   waiting for the collision to be observed just means the first few briefs
   never get written.

---

## 8. Non-goals

- Not rewriting the vendored skills that are kept.
- Not retiring any skill in this pass.
- Not introducing hooks, wrappers, or automation running outside the agent,
  while acknowledging that only those would make the invariant unbypassable.
- Not touching craft skills (frontend, motion, UX writing, design strategy) or
  homelab operations skills.
- Not adding a project-management layer beyond the existing Linear backlog.

---

## 9. Open questions

1. What dirty-worktree threshold survives daily use without being reflexively
   dismissed? 5.2 is a guess.
2. Should the gate fire on the *first* edit of a session or on the first edit
   that belongs to a different objective than the last one? The second is more
   correct and harder to detect reliably.
3. If the override-reason field turns out to be answered carelessly, the
   experiment has no instrument. Is there a better passive signal for *why* a
   switch happened?
4. Does 5.3 belong in `build-mode` at all, given that
   `verification-before-completion` already exists and is not being invoked? The
   real problem may be that it never routes, not that the expectation is absent.

---

## Implementation order

1. Global WIP invariant (5.1)
2. `build-mode` preflight on worktree and issue signals (5.2)
3. Checkpoint and verification expectations (5.3)
4. `scope-brief` skill, tiered (5.4)
5. Batched `Later`-only capture plus retrieval path (5.5)
6. Plan-path correction (5.6)
7. Narrow `brainstorming`'s description (5.7)
8. Use for two weeks, then read the gate log
9. Revisit retirement only against observed routing failures
