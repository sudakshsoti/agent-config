# Prioritization & grooming — the PM's working detail

Loaded on demand by the `backlog` skill (Modes 2 and 3). Keep the math light; this is
almost always a small team or a solo project, not a product org — the frameworks are for
_honest, fast_ ranking, not ceremony. Generic across projects — none of this assumes any
particular team or codebase.

## The mental model: value vs effort (2×2)

Plot every candidate on **value (≈ Priority, risk folded in)** against **Effort (T-shirt)**:

|                | Low effort                      | High effort                         |
| -------------- | -------------------------------- | ------------------------------------ |
| **High value** | **Quick wins** — do first       | **Big bets** — plan, then a full session |
| **Low value**  | **Fill-ins** — batch when bored | **Money pits** — decline or snooze  |

This is the default lens. The scores below are tie-breakers when the 2×2 is crowded.

## Effort points — the shared scale (used by WSJF and by Mode 5 milestone batching)

```
XS = 1   S = 2   M = 3   L = 5
```

Fibonacci-ish on purpose — the gap between sizes should feel real. `XL` has no points: decompose
it before filing, and treat one in the Ready pool as a smell.

## ICE — the everyday scorer (Mode 2)

```
ICE = Impact × Confidence × Ease     (each 1–10, higher = better)
```

- **Impact** — how much does finishing this improve the project (reliability, time saved,
  capability, user value)?
- **Confidence** — how sure are you it'll work and is worth it? (Low confidence = a
  research spike first.)
- **Ease** — inverse of Effort points: `XS`≈10, `S`≈8, `M`≈6, `L`≈4
  (and those should be decomposed, not scored).

Score the top of the backlog, rank descending, sanity-check against the 2×2. Re-score
periodically — ICE drifts and inflates if you don't.

## WSJF — the override for time-bound items (Mode 2)

When **delay itself causes harm** (a cert expires, a security patch ages, a dependency
goes EOL, a backup window lapses), ICE under-rates it. Float these up with:

```
WSJF = Cost of Delay ÷ Job size
Cost of Delay = Value + Time-criticality + Risk-reduction   (each 1–10)
Job size = Effort points (see scale above)
```

A small job that gets much worse if ignored wins. Use WSJF as a **promotion override**, not
the everyday ranker.

## Skip these (noted so you don't reach for them)

- **RICE** — "Reach" is meaningless below team scale; the Effort divisor duplicates ICE's
  Ease. Only reach for it once there's a real multi-user audience to reach.
- **Kano** — needs a user base to survey.
- **MoSCoW** — useful only as _language_ when scoping a single session ("Must/Should/Could
  this sitting"), never as a ranker.

## Weekly grooming checklist (Mode 3)

Run top to bottom. Write findings back to Linear as you go.

1. **Prune.** `list_issues` across the project. Close/`Cancel` anything no longer relevant.
   Don't hoard — important items resurface; dead ones just rot. A lean backlog is the goal.
2. **Re-score the top.** ICE the not-started candidates. Promote/demote Priority to match.
   State the reasoning in a comment if a priority changes meaningfully.
3. **Stale sweep.** Find issues with no update in **>14 days**. For each: re-prioritize,
   decompose, or kill. A stale `High` is a contradiction — resolve it.
4. **Blocked audit.** For every item with an open _blocked-by_ relation: confirm the blocker
   is real and names an **unblock action**. No action ⇒ de-prioritize or close.
5. **WIP check.** Count active-in-progress items. Over the team's WIP limit (default **2**)
   ⇒ stop starting, start finishing. Recommend which to push to done.
6. **Definition-of-Ready pass.** Every item headed toward active work must have testable
   acceptance criteria + Effort + no open blocker. Demote the ones that don't, with a note.
7. **Definition-of-Done pass.** Every recently-done item must actually meet its acceptance
   criteria. Reopen the ones that don't.
8. **Milestone health.** Any open milestone (Mode 5) fully done? Close it. Any milestone
   whose membership changed enough to blow its point budget? Flag for a rebalance.
9. **Frame the next session.** Pick a small, mixed set (a feature + a bug/chore) sized to
   fit one sitting — or, better, point at Mode 5 and build/refresh a real milestone.

## Definitions

- **Definition of Ready (DoR)** — an item may move into active work only with: clear
  what/why, testable acceptance criteria, an Effort estimate, the team's real labels set,
  a Priority, and no open blocker.
- **Definition of Done (DoD)** — an item may reach done only when every acceptance
  criterion is verifiably true (and, for planned work, the linked plan's steps are complete).
- **WIP limit** — default at most **2** items in progress at once, adjustable to the
  team's stated policy. Finishing beats starting.
