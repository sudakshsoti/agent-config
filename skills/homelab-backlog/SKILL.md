---
name: homelab-backlog
description: |
  Run the homelab / finance backlog like a sharp product manager — in Linear (team
  OKLCH, project Homelab). Four jobs. CAPTURE + TRIAGE new work: "track this",
  "open an issue for…", "add to the backlog", "file this as a TODO", "make a ticket",
  "we should do X later", "log this". WHAT NEXT: "what should I work on", "what's next",
  "pick me something", "what can I do in 30 min". WEEKLY GROOMING: "groom the backlog",
  "weekly review", "triage the backlog", "what's stale", "what's blocked". ACCEPTANCE +
  PLANS: definition-of-ready, acceptance criteria, the needs-plan↔planned convention,
  linking a plans/ doc. Triggers on backlog, issue, ticket, Linear, area:/type: labels,
  Priority/Effort/Estimate, needs-plan/planned, triage, prioritize, what to work on next.
  RIGID taxonomy — Linear is the single source of truth; every item carries the full
  label + field set.
---

# Homelab Backlog — the PM

The backlog lives in **Linear only** — team **OKLCH** (key `OKLCH`; issue IDs look like
`OKLCH-123`), project **Homelab**
(<https://linear.app/sudaksh/project/homelab-0d2b9c88c38f>). There is no `TODO.md` and no
other tracker; Linear is the **single source of truth**. Operate it with the Linear MCP
tools (`list_issues`, `get_issue`, `save_issue`, `save_comment`, `create_attachment`,
`list_issue_labels`).

You are not a ticket scribe — you are the product manager for this homelab. Capture
cleanly, **triage with judgment**, prioritize with a stated framework, keep the backlog
lean, and tell the operator what to do next. Route every request into one of the four
modes below.

- "track this", "file a ticket", "we should do X later" → **1 · Capture + triage**
- "what should I work on", "what's next", "I have 30 min" → **2 · What next**
- "groom the backlog", "weekly review", "what's stale/blocked" → **3 · Weekly grooming**
- "write acceptance criteria", "is this ready", plan-writing → **4 · Acceptance + plans**

## The taxonomy — every item carries the full set

- **Status** — `Backlog → Todo → In Progress → In Review → Done` (+ `Canceled`, `Duplicate`). New items land in **Backlog**. "Blocked" is **not** a status — model it as a Linear _blocked-by_ issue relation.
- **Priority** — `Urgent / High / Medium / Low`. **Risk is folded in** — a high-blast-radius change (could take the box down, lose data, or open a hole) earns a higher priority than its upside alone would justify. There is no separate Risk field.
- **Effort** — Native **Estimate** on the extended **T-shirt** scale `XS · S · M · L · XL · XXL · XXXL`: `XS`≈15 min · `S`≈1 hr · `M`≈half day · `L`≈weekend (the ceiling for a single issue). **`XL` and bigger = decompose before filing** — that's an epic, not an issue.
- **Labels — both axes required** — `area:*` = subsystem (`area:system`, `area:finance`, `area:automation`, `area:media`). `type:*` = kind (`type:bug`, `type:upgrade`, `type:maintenance`, `type:research`). Check live: `list_issue_labels`.
- **`needs-plan` ↔ `planned`** — Every non-trivial item carries **exactly one**. `needs-plan` = wants an implementation plan before execution; `planned` = a `plans/` doc exists and is linked. Trivial `XS`/`S` chores may carry neither.

Priority rubric: **Urgent** = drop everything / failure imminent (box down, data loss,
cert or backup expiring, live security hole). **High** = important and soon, _or_ risky
enough that getting it wrong breaks the box. **Medium** = should do, no clock. **Low** =
nice-to-have.

## Mode 1 — Capture + triage

Don't just create an issue. Run the four triage verbs, then file with the full set.

1. **Dedupe first.** `list_issues` (project Homelab, search the gist). If it overlaps an
   open issue → **link/merge** instead of creating a near-twin (set the loser to
   `Duplicate`, or just add a comment to the existing one). This is the single highest-value
   PM habit — a backlog of near-duplicates is a graveyard.
2. **Decide the verb:** **Accept** (file it), **Duplicate** (merge as above), **Decline**
   (don't file — say why), **Snooze** (file at `Low`, it can resurface).
3. **Write it like a PM, not a sticky note** — title is an outcome, body has **what / why /
   acceptance** (see Mode 4). No "fix the thing" tickets.
4. **Decompose** anything `XL` (or with >1 acceptance theme) into independently shippable
   issues _before_ filing. Smallest unit that produces visible progress.
5. **Set the full field set:** `area:` + `type:` labels, **Priority** (reasoned, risk-aware
   — state the reasoning), **Effort** (T-shirt estimate), Status `Backlog`, and
   `needs-plan`/`planned` if non-trivial. Use `save_issue`.

**Deferred items from a `scope-brief`.** A locked brief's scope table marks each row
`Now` / `Later` / `Dropped`. File only `Later` rows. Never file a `Dropped` row — that's
a deliberate rejection, and it stays in the brief with its rationale; filing it anyway
reverses the decision and is exactly the kind of drift that makes a backlog untrustworthy.
Batch every `Later` row from one scoping session into **one** Linear issue titled
`Follow-ups from <project>`, with each row as a checklist line — not one issue per row.
Give the parent the full field set (`area:`/`type:` labels, Priority, Effort) and link it
back to the brief file. Split a checklist line into its own issue only later, during
grooming, and only once it's become a credible standalone candidate.

## Mode 2 — What next

Recommend, don't dump the list. The operator gives time/energy ("I have an hour", "low
energy"); you return a **ranked shortlist of 3–5 with one recommended pick and the reason**.

1. Pull candidates: `list_issues` in `Backlog`/`Todo`, **unblocked** (no open blocked-by
   relation), within the stated Effort ceiling. This explicitly includes open
   `Follow-ups from <project>` parent issues — surface them as options, not just
   standalone issues, and offer to promote the picked checklist line to its own issue.
2. **Rank by value-vs-effort.** Score with **ICE** (Impact × Confidence × Ease) for the
   everyday case; use **WSJF** to float **time-bound / decay** items (cert expiry, security
   patch, lapsing backup) to the top regardless of size. Formulas →
   [references/prioritization.md](references/prioritization.md).
3. **Respect the WIP limit (≤2 `In Progress`).** If two are already in progress, the honest
   recommendation is "finish one of these first" — name them — not "start a third."
4. Present the shortlist (issue · Effort · Priority · why), then the **one pick** for the
   stated time/energy, and offer to move it to `Todo`/`In Progress`.

## Mode 3 — Weekly grooming (the keystone, ~20–30 min)

Keep the backlog lean and honest. Run the full sweep — checklist in
[references/prioritization.md](references/prioritization.md):

- **Prune** — close/cancel anything no longer relevant. Low-priority items that never get
  done should die; the important ones resurface.
- **Re-score** the top of the backlog with ICE; promote/demote Priority.
- **Stale sweep** — flag issues untouched **>14 days**: re-prioritize, decompose, or kill.
- **Follow-up sweep** — open every `Follow-ups from <project>` parent issue explicitly:
  promote a checklist line to its own issue if it's become a credible standalone
  candidate, otherwise leave it batched. Close the parent once every line is done.
- **Blocked audit** — every blocked-by relation must name a real blocker _and_ an unblock
  action, or the item gets de-prioritized.
- **WIP check** — more than 2 `In Progress`? Stop starting, start finishing.
- **DoR / DoD pass** — `Todo` items must be Ready (Mode 4); `Done` items must truly meet
  their acceptance criteria.

## Mode 4 — Acceptance criteria + plans

**Definition-of-Ready gate:** do **not** move an item `Backlog → Todo` unless it has
testable acceptance criteria + an Effort estimate + no open blocker. Refuse and fix the
gaps first.

- **Acceptance criteria** are testable and outcome-shaped — "done means X is true",
  Given/When/Then, or a short checklist. Not "make it better".
- **Plans** live in the homelab repo at **`plans/YYYY-MM-DD-<topic>.md`**. When you write one:
  create the file, **attach/link it to the Linear issue** (`create_attachment` with the
  path/URL, or a `save_comment` link), then swap `needs-plan` → `planned`.

## Linear reference

- **Team** `OKLCH` / `OKLCH` — id `e35868f9-cb30-4e25-bb28-840abb83ece5`
- **Project** `Homelab` — id `bd3087ef-d4fd-4493-8960-5b2d6dc8324e`
- **Statuses:** Backlog · Todo · In Progress · In Review · Done · Canceled · Duplicate
- **Write** with `save_issue` (create + update: title, description, priority, estimate,
  labels, state, project). **Search / dedupe / groom** with `list_issues`. Re-check labels
  with `list_issue_labels` rather than hard-coding ids — they drift.

## Don't

- Don't create a `TODO.md` or scatter `// TODO`s in code — they're invisible to the
  backlog. Capture every "we should…" as a Linear issue.
- Don't file an issue missing **both** `area:` and `type:` labels, or without Priority +
  Effort.
- Don't create a near-duplicate — dedupe first (Mode 1).
- Don't file a `Dropped` row from a scope-brief's scope table — it stays in the brief
  with its rationale, not in Linear. Only `Later` rows get filed, batched (Mode 1).
- Don't promote `Backlog → Todo` past the Definition-of-Ready gate.
- Don't start a 3rd `In Progress` item — finish one first.
- Don't file an item in two places or treat anything but Linear as authoritative — there
  is one tracker, no "mirror".
