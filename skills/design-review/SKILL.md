---
name: design-review
description: >
  The gate for visual work. Renders a UI at three widths, compares it against the
  project's reference images, and reports defects and absences at P0/P1/P2 with
  concrete fixes. Use before claiming any UI work is done, and whenever asked to
  audit, critique or review a screen or page. Runs against a render, never against
  source alone.
disable-model-invocation: true
---

# Design review

Source cannot show you a crush, a dead gutter, a reflow, a clipped label, a
misaligned row, or a screen that is merely dull. Render it, and put the reference
beside it. A finding without an image behind it is a guess.

A review that only hunts defects will pass a screen that has no defects and no
quality. That is why half of this file is about **absence**.

## 1. Render, and load the reference

Three widths, always: **390**, **900**, **1440**. Both themes if the project has
two.

- **Playwright, for the repeatable capture.** Copy `scripts/shoot.mjs` into the
  project on first use, then
  `node scripts/shoot.mjs http://127.0.0.1:8000 390 900 1440`. It writes PNGs to
  the session scratchpad and prints the paths. Read them.
- **Chrome, for states that need interaction:** a sheet open, a row hovered, an
  error showing. `tabs_create_mcp`, `navigate`, then `computer`.

Capture the populated state, then the empty and error states. A review of the
happy path is half a review.

Then **read `design/reference/*.png`**. If the project has no reference images,
say so in the report and stop — the comparative half of this gate cannot run, and
`design-brief` establishes the anchor.

## 2. Report

One line per finding, most severe first:

```
file:line | finding | P0/P1/P2 | fix
```

Name the file and line where the fix goes. Make every claim measurable. "The
layout feels cramped" is not a finding. These are:

- "The reference gives the image 60% of the card; mine gives it 3%."
- "The reference shell carries five slots; mine carries two."
- "`App.tsx:198` caps at `max-w-5xl` while the grid switches to five columns at
  75rem, so each column gets 179px."

### P0a — absence. The screen is missing something a product screen has.

1. **No shell**, or a shell missing identity, navigation or search, and the global
   action.
2. **The decision-carrying medium is a placeholder** — a letter in a box where a
   photograph belongs.
3. **Reading order does not match the decision** the user is making. A serial
   number or an internal id leads.
4. **A screen state is undesigned**: empty, loading, error, first-run, or
   post-action.
5. **A spacing value off the base unit**, or a type size off the scale.
6. **Two type families with no written justification**, or a second family used
   inside body copy.

### P0b — composition. The screen does not work.

7. **Grid cannot fit**: column count times minimum usable width exceeds the
   container. Compute it.
8. **A breakpoint the container never reaches.**
9. **Wrong pattern for the data**: homogeneous, comparable items rendered as cards.
10. **More than one primary action** in a unit, or `items x actions > 8` with no
    collapse.
11. **Comparable fields do not share an axis** across repeated units.
12. **Text clipped, overflowing, or forcing horizontal scroll** at any width.
13. **Layout shifts** when an image or a state swaps in.
14. **A label repeats more than three times** on one screen.

### P1 — material.

Walk `references/slop.md`, which is scoped to marketing and brand surfaces. On a
product screen most of it does not apply, and looking conventional is correct;
what still binds anywhere is the palette discipline, the contrast minimums, and
the type defaults worth avoiding.

### P2 — finish.

Missing `:focus-visible`. Tap targets under 44px. Motion outside ~150ms, or using
transform where opacity and colour would do. Missing `prefers-reduced-motion`.
Unused tokens sitting beside a hardcoded value. Proportional numerals in a column
of figures.

## 3. Gate

Not done until **P0 is zero** — both tiers. P1 findings are fixed or each one is
justified in a line. P2 is listed.

Then the question the defect list cannot ask:

> Set beside the reference at the same width, could a stranger tell which one
> shipped?

If the answer is no, say so, name the single largest gap, and the review **fails**.
A screen can have zero defects and still fail here, and that is the point. Do not
soften this to make a result pass.

## 4. Respecting intent

A deliberate choice that trips a rule carries a `design-review-ignore` comment
naming the rule; skip those. Where a finding contradicts something the project's
`DESIGN.md` states explicitly, the project wins and the finding is dropped.

## 5. Knowing whether the rules work

`references/evals.md` holds three fixed briefs. Run them in a fresh session
against a baseline without the skills, then with. A rule that does not change the
render is an adjective, not a constraint, and should be cut rather than reworded.
