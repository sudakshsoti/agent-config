# Prioritization & grooming — the PM's working detail

Loaded on demand by the `homelab-backlog` skill (Modes 2 and 3). Keep the math light;
this is a solo homelab, not a product org — the frameworks are for _honest, fast_
ranking, not ceremony.

## The mental model: value vs effort (2×2)

Plot every candidate on **value (≈ Priority, risk folded in)** against **Effort (T-shirt)**:

|                | Low effort                      | High effort                         |
| -------------- | ------------------------------- | ----------------------------------- |
| **High value** | **Quick wins** — do first       | **Big bets** — plan, then a weekend |
| **Low value**  | **Fill-ins** — batch when bored | **Money pits** — decline or snooze  |

This is the default lens. The scores below are tie-breakers when the 2×2 is crowded.

## ICE — the everyday scorer (Mode 2)

```
ICE = Impact × Confidence × Ease     (each 1–10, higher = better)
```

- **Impact** — how much does finishing this improve the homelab (reliability, time saved,
  capability)?
- **Confidence** — how sure are you it'll work and is worth it? (Low confidence = a
  `type:research` spike first.)
- **Ease** — inverse of Effort (extended T-shirt): `XS`≈10, `S`≈8, `M`≈6, `L`≈4,
  `XL`≈2, `XXL`/`XXXL`≈1 (and those should be decomposed, not scored).

Score the top of the backlog, rank descending, sanity-check against the 2×2. Re-score
weekly — ICE drifts and inflates if you don't.

## WSJF — the override for time-bound items (Mode 2)

When **delay itself causes harm** (a cert expires, a security patch ages, a backup window
lapses, disk is filling), ICE under-rates it. Float these up with:

```
WSJF = Cost of Delay ÷ Job size
Cost of Delay = Value + Time-criticality + Risk-reduction   (each 1–10)
Job size = Effort (XS=1, S=2, M=3, L=5, XL=8, XXL=13, XXXL=21)
```

A small job that gets much worse if ignored wins. Use WSJF as a **promotion override**, not
the everyday ranker.

## Skip these (noted so you don't reach for them)

- **RICE** — "Reach" is meaningless for a 1-user homelab; the Effort divisor duplicates ICE's Ease.
- **Kano** — needs a user base to survey. You are the only user.
- **MoSCoW** — useful only as _language_ when scoping a single weekend ("Must/Should/Could
  this session"), never as a ranker.

## Weekly grooming checklist (Mode 3)

Run top to bottom. Write findings back to Linear as you go.

1. **Prune.** `list_issues` across the project. Close/`Cancel` anything no longer relevant.
   Don't hoard — important items resurface; dead ones just rot. A lean backlog is the goal.
2. **Re-score the top.** ICE the `Backlog`/`Todo` candidates. Promote/demote Priority to
   match. State the reasoning in a comment if a priority changes meaningfully.
3. **Stale sweep.** Find issues with no update in **>14 days**. For each: re-prioritize,
   decompose, or kill. A stale `High` is a contradiction — resolve it.
4. **Blocked audit.** For every item with an open _blocked-by_ relation: confirm the blocker
   is real and names an **unblock action**. No action ⇒ de-prioritize or close.
5. **WIP check.** Count `In Progress`. **>2 ⇒ stop starting, start finishing.** Recommend
   which to push to `Done`.
6. **Definition-of-Ready pass.** Every `Todo` item must have testable acceptance criteria +
   Effort + no open blocker. Demote the ones that don't back to `Backlog` with a note.
7. **Definition-of-Done pass.** Every recently-`Done` item must actually meet its acceptance
   criteria. Reopen the ones that don't.
8. **Frame the next stint.** Pick a small, mixed set (a feature + a bug/chore) sized to fit
   one sitting; MoSCoW the scope ("Must / Should / Could this weekend").

## Definitions

- **Definition of Ready (DoR)** — an item may enter `Todo` only with: clear what/why,
  testable acceptance criteria, an Effort estimate, both `area:`+`type:` labels, a Priority,
  and no open blocker.
- **Definition of Done (DoD)** — an item may reach `Done` only when every acceptance
  criterion is verifiably true (and, for planned work, the `plans/` doc's steps are complete).
- **WIP limit** — at most **2** items `In Progress` at once. Finishing beats starting.
