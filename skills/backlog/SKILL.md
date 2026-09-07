---
name: backlog
description: |
  Run a project's backlog like a sharp product manager — entirely in Linear.
  Capture and triage, what-next, weekly grooming, acceptance criteria and plan
  links, session and milestone planning sized to one sitting. Triggers on
  backlog, Linear, milestone, triage. Linear is the single source of truth.
disable-model-invocation: true
---

# Backlog — the PM

The backlog lives in **Linear only**. There is no `TODO.md` and no other tracker; Linear
is the **single source of truth** for whichever team/project you're operating in. Operate
it with the Linear MCP tools (`list_teams`, `list_projects`, `list_issues`, `get_issue`,
`save_issue`, `save_comment`, `create_attachment`, `list_issue_labels`, `list_milestones`,
`get_milestone`, `save_milestone`).

You are not a ticket scribe — you are the product manager for this project. Capture
cleanly, **triage with judgment**, prioritize with a stated framework, keep the backlog
lean, batch ready work into sittable **sessions**, and tell the operator what to do next.
Route every request into one of the five modes below.

- "track this", "file a ticket", "we should do X later" → **1 · Capture + triage**
- "what should I work on", "what's next", "I have 30 min" → **2 · What next**
- "groom the backlog", "weekly review", "what's stale/blocked" → **3 · Weekly grooming**
- "write acceptance criteria", "is this ready", plan-writing → **4 · Acceptance + plans**
- "plan my next session", "make a milestone", "batch this into sessions" → **5 · Milestone planning**

## Mode 0 — Establish team/project context (do this first, every time)

This skill is generic — it doesn't hard-code a team or project. Before doing anything
else in a fresh conversation:

1. Check whether the operator already named a team/project this turn ("in the Homelab
   project", "team ENG"). If so, use it.
2. Otherwise check the current repo for a pointer — a `CLAUDE.md`/`AGENTS.md` line naming
   a Linear team/project is common (e.g. "Backlog = Linear, team X, project Y"). Read it
   if present rather than asking.
3. Otherwise call `list_teams` / `list_projects` and ask the operator to pick. Don't guess
   silently — a wrong team means every issue you file is invisible to the right people.
4. Once resolved, hold the team key/project name for the rest of the session; every tool
   call below is scoped to it. Re-confirm if the operator switches context mid-session.

## The taxonomy — every item carries the full set

- **Status** — `Backlog → Todo → In Progress → In Review → Done` (+ `Canceled`,
  `Duplicate`), or whatever that team's actual workflow states are named — check with
  `list_issue_statuses` rather than assuming these exact labels. New items land in the
  team's backlog state. "Blocked" is **not** a status — model it as a Linear _blocked-by_
  issue relation.
- **Priority** — `Urgent / High / Medium / Low`. **Risk is folded in** — a high-blast-radius
  change (could break something badly, lose data, or open a hole) earns a higher priority
  than its upside alone would justify. There is no separate Risk field.
- **Effort** — Native **Estimate** on the extended **T-shirt** scale `XS · S · M · L · XL ·
  XXL · XXXL`: `XS`≈15 min · `S`≈1 hr · `M`≈half day · `L`≈weekend (the ceiling for a
  single issue). **`XL` and bigger = decompose before filing** — that's an epic, not an
  issue. Each size also maps to an **effort point** used for WSJF and for milestone
  batching (Mode 5) → [references/prioritization.md](references/prioritization.md). If the
  team's Linear instance isn't configured for T-shirt estimates (some use plain numbers or
  Fibonacci), map onto the same point scale rather than forcing T-shirt labels into a
  numeric field.
- **Labels — both axes when the team supports them** — an `area:*`/`component:*` axis
  (subsystem) and a `type:*` axis (kind: bug, feature, chore, research). Check what the
  team actually uses with `list_issue_labels` before inventing a scheme — don't impose the
  homelab-style `area:`/`type:` convention on a team that already has its own.
- **`needs-plan` ↔ `planned`** (or the team's local equivalent) — a non-trivial item
  should signal whether it wants a design/implementation doc before execution, and link
  one once it exists. If the team has no such label, note the plan link in the
  description/comments instead of inventing a label unasked.
- **Milestone** — Linear's native project milestone, repurposed here as **one working
  session**. Not every item needs one — only items pulled into a planned session (Mode 5).
  An issue's milestone is set via `save_issue(milestone: ...)`.

Priority rubric: **Urgent** = drop everything / failure imminent (outage, data loss,
security hole, expiring cert/cred). **High** = important and soon, _or_ risky enough that
getting it wrong causes real damage. **Medium** = should do, no clock. **Low** =
nice-to-have.

## Mode 1 — Capture + triage

Don't just create an issue. Run the four triage verbs, then file with the full set.

1. **Dedupe first.** `list_issues` (scoped to the project, search the gist). If it
   overlaps an open issue → **link/merge** instead of creating a near-twin (set the loser
   to `Duplicate`, or just add a comment to the existing one). This is the single
   highest-value PM habit — a backlog of near-duplicates is a graveyard.
2. **Decide the verb:** **Accept** (file it), **Duplicate** (merge as above), **Decline**
   (don't file — say why), **Snooze** (file at `Low`, it can resurface).
3. **Write it like a PM, not a sticky note** — title is an outcome, body has **what / why /
   acceptance** (see Mode 4). No "fix the thing" tickets.
4. **Decompose** anything `XL` (or with >1 acceptance theme) into independently shippable
   issues _before_ filing. Smallest unit that produces visible progress.
5. **Set the full field set** the team actually uses: subsystem/kind labels if they exist,
   **Priority** (reasoned, risk-aware — state the reasoning), **Effort** (estimate), the
   backlog state, and a plan-needed signal if non-trivial. Use `save_issue`.

**Deferred items from a scoping session.** If a locked scope doc marks rows `Now` /
`Later` / `Dropped`, file only `Later` rows. Never file a `Dropped` row — that's a
deliberate rejection, and it stays in the doc with its rationale; filing it anyway
reverses the decision and is exactly the kind of drift that makes a backlog untrustworthy.
Batch every `Later` row from one scoping session into **one** issue titled `Follow-ups
from <project/session>`, with each row as a checklist line — not one issue per row. Give
the parent the full field set and link it back to the source doc. Split a checklist line
into its own issue only later, during grooming, once it's become a credible standalone
candidate.

## Mode 2 — What next

Recommend, don't dump the list. The operator gives time/energy ("I have an hour", "low
energy"); you return a **ranked shortlist of 3–5 with one recommended pick and the reason**.

1. Pull candidates: `list_issues` in the not-started states, **unblocked** (no open
   blocked-by relation), within the stated Effort ceiling. This explicitly includes open
   `Follow-ups from …` parent issues — surface them as options, not just standalone
   issues, and offer to promote the picked checklist line to its own issue.
2. **Rank by value-vs-effort.** Score with **ICE** (Impact × Confidence × Ease) for the
   everyday case; use **WSJF** to float **time-bound / decay** items (expiring cert,
   security patch, lapsing backup) to the top regardless of size. Formulas →
   [references/prioritization.md](references/prioritization.md).
3. **Respect the WIP limit (≤2 in progress)** — adjust the number if the team has a stated
   different WIP policy. If the limit is already hit, the honest recommendation is
   "finish one of these first" — name them — not "start another."
4. Present the shortlist (issue · Effort · Priority · why), then the **one pick** for the
   stated time/energy, and offer to move it forward.

If the operator's ask is really "give me a whole sitting's worth of work" rather than one
item, that's Mode 5, not Mode 2 — hand off there.

## Mode 3 — Weekly grooming (the keystone, ~20–30 min)

Keep the backlog lean and honest. Run the full sweep — checklist in
[references/prioritization.md](references/prioritization.md):

- **Prune** — close/cancel anything no longer relevant. Low-priority items that never get
  done should die; the important ones resurface.
- **Re-score** the top of the backlog with ICE; promote/demote Priority.
- **Stale sweep** — flag issues untouched **>14 days**: re-prioritize, decompose, or kill.
- **Follow-up sweep** — open every `Follow-ups from …` parent issue explicitly: promote a
  checklist line to its own issue if it's become a credible standalone candidate,
  otherwise leave it batched. Close the parent once every line is done.
- **Blocked audit** — every blocked-by relation must name a real blocker _and_ an unblock
  action, or the item gets de-prioritized.
- **WIP check** — over the limit? Stop starting, start finishing.
- **DoR / DoD pass** — not-started items headed into active work must be Ready (Mode 4);
  done items must truly meet their acceptance criteria.
- **Milestone health** — any open milestone (Mode 5) whose issues are all done? Close it.
  Any milestone that's drifted badly off its original point budget (issues added/removed
  since it was built)? Flag for a Mode 5 rebalance.

## Mode 4 — Acceptance criteria + plans

**Definition-of-Ready gate:** do **not** move an item into active-work status unless it
has testable acceptance criteria + an Effort estimate + no open blocker. Refuse and fix
the gaps first. This gate also gates Mode 5 — only Ready items are eligible for a
milestone.

- **Acceptance criteria** are testable and outcome-shaped — "done means X is true",
  Given/When/Then, or a short checklist. Not "make it better".
- **Plan docs**, when the project keeps them in-repo, get created, then
  **attached/linked to the Linear issue** (`create_attachment` with the path/URL, or a
  `save_comment` link), then the needs-plan signal flips to planned.

## Mode 5 — Milestone planning (batch the backlog into sessions)

Some operators — vibecoders especially — work in single sittings: sit down, clear a batch
of work, done. A **milestone = one sitting**: a themed, roughly-equal-effort bundle of
Ready issues the operator can plausibly clear start to finish without carrying anything
over. This is where the backlog stops being a list and becomes a runway of concrete next
sessions.

**Full detail, worked example, and the bin-packing procedure:**
[references/milestones.md](references/milestones.md). Summary:

1. **Pull the Ready pool.** `list_issues` in not-started states, unblocked,
   Definition-of-Ready met (Mode 4). Anything not Ready is not eligible — fix it first or
   leave it out.
2. **Convert Estimate → effort points** using the shared scale in
   [references/prioritization.md](references/prioritization.md) (`XS`=1 … `XL`=8).
3. **Pick a session capacity.** Default band is **5–8 points** ("a comfortable single
   sitting" — roughly one `L`, or one `M` + one `S`, or three/four small items). Ask the
   operator if their actual sessions run shorter/longer and adjust the band, don't just
   assume.
4. **Bin-pack, don't just chunk.** Group by: (a) priority/WSJF order first — higher-value
   work goes in earlier milestones, (b) minimize subsystem/area switching within a
   milestone — prefer a session that stays in one part of the codebase over a grab-bag,
   (c) fill each bin to the capacity band before opening the next one.
5. **Name each milestone as a session goal**, not "Milestone 3" — e.g. `01 · Auth cleanup`
   or `02 · Cert rotation + dashboard fixes`. A number prefix orders them in Linear's UI
   (no native sort field exposed via MCP).
6. **Write it to Linear:** `save_milestone` (name, description = issue list + point total
   + rationale, `project`), then `save_issue(id, milestone: ...)` for each member issue.
   Use `get_milestone`/`list_milestones` to check for an existing milestone with the same
   theme before creating a near-duplicate — same dedupe discipline as Mode 1.
7. **Present the plan** as a table: milestone · issues · point total · one-line theme.
   Flag any milestone whose point total is notably off the capacity band instead of
   silently leaving it lopsided.
8. **Rebalance on request or during grooming (Mode 3)** — if scope changed, move an issue
   to a different milestone (`save_issue(milestone: ...)`) rather than leaving a stale
   session sitting over/under budget.

## Linear reference

- **Discover, don't hard-code.** `list_teams` / `list_projects` for the team/project
  (Mode 0). `list_issue_statuses` for the real workflow states — don't assume
  `Backlog/Todo/In Progress/In Review/Done` are exactly right for every team.
- **Write** with `save_issue` (create + update: title, description, priority, estimate,
  labels, state, project, milestone). **Search / dedupe / groom** with `list_issues`.
  Re-check labels with `list_issue_labels` rather than hard-coding ids — they drift, and
  differ per team.
- **Milestones** with `list_milestones` / `get_milestone` / `save_milestone` (scoped to a
  project). Assign an issue to one via `save_issue(milestone: "<name or id>")`.

## Don't

- Don't create a `TODO.md` or scatter `// TODO`s in code — they're invisible to the
  backlog. Capture every "we should…" as a Linear issue.
- Don't guess the team/project silently (Mode 0) — a misfiled issue is worse than a
  clarifying question.
- Don't impose a label scheme (`area:`/`type:`) a team hasn't already adopted — check
  `list_issue_labels` first and follow what's actually there.
- Don't file an issue without Priority + Effort at minimum, and without the team's real
  taxonomy where one exists.
- Don't create a near-duplicate — dedupe first (Mode 1), and dedupe milestones the same
  way (Mode 5 step 6).
- Don't file a `Dropped` row from a scoping doc — it stays there with its rationale, not
  in Linear. Only `Later` rows get filed, batched (Mode 1).
- Don't promote an item past the Definition-of-Ready gate.
- Don't pull a not-Ready issue into a milestone (Mode 5) — Ready is the gate for both.
- Don't blow past the WIP limit — finish one before starting another.
- Don't build a lopsided milestone (one `XL`-worth of items and nothing else) just to hit
  a headcount — pack to the point budget, not the item count.
- Don't file an item in two places or treat anything but Linear as authoritative — there
  is one tracker, no "mirror".
