# Milestone / session planning — the PM's working detail

Loaded on demand by the `backlog` skill (Mode 5). Generic across projects. The goal: turn
a flat Ready pool into a short queue of **sessions** — Linear Milestones — each one
plausibly finishable in a single sitting, each roughly the same size as the others.

## Why milestones, and why "one session" as the unit

A backlog ranked by priority alone tells you what to do first, but not how much of it
fits in front of you today. Vibecoding sessions have a natural shape: you sit down, you
want to walk away with something shipped, and open-ended lists make that hard to judge.
Batching Ready work into equal-ish, session-sized bundles turns "what's next" into "here's
your next three sittings," which is a much easier thing to commit to.

Linear's native **Milestone** (attached to a Project) is repurposed for this — no custom
field needed. One milestone = one sitting.

## Step 1 — Build the Ready pool

`list_issues` scoped to the project, not-started states only, unblocked (no open
blocked-by relation), Definition-of-Ready met (Mode 4: acceptance criteria + Effort
estimate + labels + Priority). Anything failing DoR doesn't enter the pool — fix it first
(swap into Mode 4) or leave it for a later round.

## Step 2 — Convert Estimate to points

Use the shared scale from [prioritization.md](prioritization.md):

```
XS = 1   S = 2   M = 3   L = 5
```

If an issue somehow lacks an Estimate, it fails DoR — don't guess a point value for it,
send it back to Mode 4.

## Step 3 — Pick the session capacity band

Default: **5–8 points** per milestone. That's roughly:

- one `L` alone, or
- one `M` + one `S` (+ maybe an `XS`), or
- three to four small (`XS`/`S`) items, or
- one `L` + one `XS`

This is a starting default, not a law — ask the operator whether their sessions actually
run shorter (a lunch-break sitting: cap the band at 3–5) or longer (a full free day: raise
it to 8–13). Once you have a real answer, keep using it for the rest of the planning pass
instead of re-asking per milestone.

## Step 4 — Bin-pack

This is a **bin-packing problem**, not a simple chunking of the sorted list. Greedy
best-fit works fine by hand:

1. Sort the Ready pool by priority/WSJF descending (Mode 2's ranking) — higher-value work
   should land in earlier milestones, not just whatever fits neatly.
2. Open milestone `01`. Walk the sorted pool; add each issue to the current milestone if
   it fits under the capacity band's ceiling, preferring issues that share an
   area/subsystem with what's already in the bin (minimizes context-switching inside one
   sitting).
3. When adding the next same-area issue would blow the ceiling, either swap in a smaller
   same-area issue from further down the pool (if one exists and doesn't skip too much
   priority), or close out the milestone and open the next one.
4. Repeat until the pool is empty. The last milestone may be under-filled — that's fine,
   don't force in low-priority filler just to hit the floor.

Don't over-engineer this into an actual optimal bin-packing solve — greedy-by-priority
with an area preference is good enough, and it's more legible to the operator than a
score they can't sanity-check.

## Step 5 — Name and record

- **Name each milestone as a session goal**: `01 · Auth cleanup`, `02 · Cert rotation +
  dashboard fixes` — not `Milestone 3`. The number prefix is the only ordering mechanism
  available (Linear's MCP surface doesn't expose milestone sort order), and the theme
  tells the operator what they're signing up for at a glance.
- `save_milestone(project, name, description)` — description should carry the point total
  and a one-line rationale ("priority-ranked auth work, all `area:auth`, 7 pts").
- `save_issue(id, milestone: "<name>")` for every member issue.
- Check `list_milestones`/`get_milestone` first for a same-themed milestone already open —
  extend it rather than creating a near-duplicate, same dedupe discipline as capture
  (Mode 1).

## Step 6 — Present the plan

A table, most important milestone first:

| Milestone | Theme | Issues | Points | Notes |
|---|---|---|---|---|
| 01 | Auth cleanup | ISSUE-12, ISSUE-19, ISSUE-4 | 7 | in band |
| 02 | Cert rotation + dashboard | ISSUE-31, ISSUE-8 | 6 | in band |
| 03 | Small fixes | ISSUE-2, ISSUE-15, ISSUE-16, ISSUE-22 | 4 | under band — fine, low-priority tail |

Call out anything meaningfully off-band instead of quietly leaving it lopsided (e.g. "03
only hit 4 points because nothing else same-area was Ready — pad it with an off-theme
item, or leave it short").

## Rebalancing (Mode 3 grooming, or on request)

Milestones drift: new issues land, old ones get killed, priorities shift. During grooming
or whenever asked, re-check membership vs. the point budget and move issues between
milestones with `save_issue(milestone: ...)` rather than leaving a stale session over or
under its budget. Close a milestone once every member issue is done.
