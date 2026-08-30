---
name: design-review
description: >
  The gate for visual work. Renders a UI at three widths, then reports composition
  and material defects at P0/P1/P2 with concrete fixes. Use before claiming any UI
  work is done, and whenever asked to audit, critique or review a screen, page or
  design. Runs against a render, never against source alone. Holds the canonical
  anti-slop list for visual work in `references/slop.md`.
disable-model-invocation: true
---

# Design review

Source cannot show you a crush, a dead gutter, a reflow, a clipped label, or a row
that fails to align. Render first. Everything below is judged against images, and
a finding without a render behind it is a guess.

## 1. Render

Three widths, always: **390**, **900**, **1440**.

Two mechanisms, either is fine:

- **Playwright, for the repeatable capture.** Copy `scripts/shoot.mjs` into the
  target project on first use, then:
  `node scripts/shoot.mjs http://127.0.0.1:8000 390 900 1440`
  It writes PNGs to the session scratchpad and prints the paths. Read them.
- **Chrome, for live critique.** `tabs_create_mcp`, `navigate`, then `computer`
  screenshots. Use this when the state you need to see requires interaction: a
  sheet open, a row hovered, an error showing.

Capture the populated state, then the empty state and the error state if the screen
has them. A review of the happy path only is half a review.

## 2. Report

One line per finding, most severe first:

```
file:line | tell | P0/P1/P2 | fix
```

Name the file and line where the fix goes. "The layout feels cramped" is not a
finding. "App.tsx:198 caps at max-w-5xl while ProgrammeGrid switches to 5 columns
at 75rem, so each column gets 179px" is.

### P0 — composition. The screen does not work.

1. **Grid cannot fit.** Column count times minimum usable width exceeds the
   container. Compute it.
2. **Breakpoint the container never reaches.** The column count triggers at a
   viewport width the `max-width` forbids.
3. **Wrong pattern for the data.** Items compared on 3 or more shared attributes,
   rendered as cards instead of rows.
4. **More than one primary action in the view.**
5. **`items x actions > 8`** with no collapse.
6. **Comparable fields do not share an axis** across repeated units.
7. **Text clipped, overflowing, or forcing horizontal scroll** at any of the three
   widths.
8. **Dead gutter over 15%** of the viewport at 1440.
9. **A label repeats more than three times** on one screen.
10. **Layout shifts** when an image, empty state or error state swaps in.

### P1 — material. The screen works and looks generated.

Walk `references/slop.md`. It is the list of record for visual work; do not
re-derive it and do not write a fourth copy of it somewhere else.

### P2 — finish.

Spacing values off the project's scale. Unused tokens where a hardcoded value sits
beside them. Missing `:focus-visible`. Tap targets under 44px. Motion outside
150ms or using transform where opacity and colour would do. Missing
`prefers-reduced-motion`.

## 3. Gate

The work is not done until **P0 is zero**. P1 findings are fixed or each one is
justified in a line. P2 is listed.

Then answer this, honestly, in one sentence:

> Could a reader tell this from default LLM output at a glance?

If not, the restraint has not been applied hard enough. Say so and name the one
change that would fix it.

## 4. Respecting intent

A deliberate choice that trips a rule is marked in the source with a
`design-review-ignore` comment naming the rule. Skip those and do not re-raise
them. Absence of the comment is not proof the choice was accidental, so where a
finding contradicts something the project's `DESIGN.md` states explicitly, the
project wins and the finding is dropped.

## 5. Knowing whether the rules work

`references/evals.md` holds three fixed briefs. Run them in a fresh session
against a baseline without the skills, then with. A rule that does not change the
render is an adjective, not a constraint, and should be cut rather than reworded.
