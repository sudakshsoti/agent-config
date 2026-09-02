---
name: design-review
description: |
  The gate for visual work. Renders a UI at three widths, compares it against the
  project's reference images, and reports defects and absences at P0/P1/P2 with
  concrete fixes. Use before claiming any UI work is done, and whenever asked to
  audit, critique or review a screen or page. Runs against a render, never against
  source alone. Normally the last step of the `design-brief` pipeline.
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

- **Playwright, for the repeatable capture.** The script lives in the installed
  skill directory, which is not on the project's path and cannot resolve the
  project's `playwright`, so copy it in on first use, then run it from the
  project:

  ```bash
  mkdir -p scripts
  cp ~/.claude/skills/design-review/scripts/shoot.mjs scripts/shoot.mjs 2>/dev/null \
    || cp ~/.agents/skills/design-review/scripts/shoot.mjs scripts/shoot.mjs
  pnpm add -D playwright && pnpm exec playwright install chromium   # once
  node scripts/shoot.mjs http://127.0.0.1:<port> 390 900 1440 --theme both
  ```

  Find `<port>` from the project's dev script or config; never assume one. Start
  the dev server first. The script writes PNGs to `$CLAUDE_SCRATCHPAD` if set,
  else `./.shots/` (gitignore it), and prints the paths. Read every one. If
  `playwright` is missing, the server refuses the connection, or `goto` times
  out, report `BLOCKED: <reason>` with the one-line fix and stop; do not retry
  blindly and do not review from source.
- **The browser tool, for states that need interaction:** a sheet open, a row
  hovered, an error showing. Open the page, drive it, screenshot.

Capture the populated state, then the empty and error states. A review of the
happy path is half a review.

Then **read `design/reference/*.png`**. If the directory is empty, report
`BLOCKED: no reference anchor — run design-brief §1` and the review **fails**.
The comparative half of this gate cannot run without it, and a build that reached
this point without one skipped the router.

## 2. Report

Put the reference beside the render at each width. Walk every P0 item below at
390, 900 and 1440 and record pass or fail per width; a fail at one width is a
fail. Take the ten answers `interface-composition` §7 produced as given and
re-check them against the pixels — any answer that was a yes rather than a
number is itself a P0.

One line per finding, most severe first:

```
file:line | finding | P0/P1/P2 | width(s) | fix
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
   container. Compute it as `interface-composition` §2 does.
8. **A breakpoint the container never reaches**, both converted to px.
9. **Wrong pattern for the data**: homogeneous, comparable items rendered as cards.
10. **More than one primary action** in a unit, or `items x actions > 8` with no
    collapse.
11. **Comparable fields do not share an axis** across repeated units.
12. **Text clipped, overflowing, or forcing horizontal scroll** at any width.
13. **Layout shifts** when an image or a state swaps in.
14. **A label repeats more than three times** on one screen.

### P1 — material.

On a marketing or brand surface, load `references/slop.md` and walk it; each row
it hits is a P1. On a product screen do **not** load it: `app-ui` wins there and
looking conventional is correct. Three rows bind anywhere and are checked from
memory: one flat brand colour plus one accent and nothing else saturated; text
contrast at WCAG AA (4.5:1 body, 3:1 large); and no untuned framework defaults
for type. A P1 is fixed, or justified in one line, before the gate passes.

### P2 — finish.

Each is a threshold, not a taste. Missing `:focus-visible`. A tap target under
44px at 390. Motion outside 100–200ms, or using transform where opacity and
colour would do. Missing `prefers-reduced-motion`. An unused token sitting beside
a hardcoded value of the same kind. Proportional numerals in a column of figures.
P2 never blocks the gate; it is listed.

## 3. Gate

Not done until **P0 is zero** — both tiers. This is a loop, not a verdict:

1. Fix every P0 in code.
2. Re-render at 390 / 900 / 1440, both themes if present.
3. Re-run §2 against the new PNGs and `design/reference/*.png`.
4. Repeat until P0 is zero. Then every P1 is fixed or justified in one line, and
   P2 is listed.

Then the question the defect list cannot ask:

> Set beside the reference at the same width, could a stranger tell which one
> shipped?

If the answer is no, say so, name the single largest gap, the review **fails**,
and you return to step 1 with that gap as the P0. A screen can have zero defects
and still fail here, and that is the point. Do not soften this to make a result
pass.

## 4. Respecting intent

A deliberate choice that trips a rule carries a `design-review-ignore` comment
naming the rule; skip those. Where a finding contradicts something the project's
`DESIGN.md` states explicitly, the project wins and the finding is dropped.

## 5. Knowing whether the rules work (maintainers only)

Not part of a review; do not load it while reviewing. `references/evals.md` holds
three fixed briefs for whoever edits this file: run them in a fresh session
against a baseline without the skills, then with. A rule that does not change
the render is an adjective, not a constraint, and should be cut rather than
reworded.
