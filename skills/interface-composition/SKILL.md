---
name: interface-composition
description: >
  Arrangement rules for product UI: choosing between table, list, card grid and
  detail view; column and container arithmetic; density and row height; action
  hierarchy; alignment across repeated units; progressive disclosure. The
  arithmetic pass that runs **after** `app-ui` has decided the design, on any
  screen that repeats a unit, compares records, or carries per-item controls. It
  catches defects; it does not design. Do not invoke for component behaviour,
  state, data flow or tests.
disable-model-invocation: true
---

# Interface composition

Material and arrangement are separate failures. A screen can have a correct token
system, correct contrast, tabular numerals and a disciplined palette, and still be
unusable because five things are compared in five columns that cannot fit, or
because every repeated unit carries three equal-weight buttons.

This skill is arrangement only. Every rule here is checkable against your own
output. If a rule cannot be checked, it does not belong in this file.

This skill runs **after** `app-ui`, not instead of it. `app-ui` decides what the
screen is and what it has; this one proves the arrangement holds up. A screen that
passes everything here can still be a bad screen, so never treat a clean pass as
a finished design.

Work in order: pick the pattern, prove the container, place the actions, align the
repeats, then hand over to `design-review`.

## 1. Pick the pattern, and say why

Count the repeated items and count the attributes they share. Then:

- **3 or more shared attributes, and the user compares across items** → table or
  list rows. Not a card grid. Comparison needs values on a shared horizontal or
  vertical axis, and one set of column labels.
- **Heterogeneous items where an image carries meaning** → card grid. The image
  must be real and load; a letter in a grey rectangle is not an image.
- **One item, many attributes** → detail view, not a card.
- **Fewer than 4 items with a single action each** → a list, not a grid.
- **A sequence where order carries information** → numbered rows. If order does
  not carry information, numbering is decoration. Delete it.

State the choice in one line before building: "Five films compared on four rating
sources, so a table with one header row." If the sentence does not name the count
and the attributes, you have not made the decision yet.

**Repetition audit.** Count how many times each label appears on the finished
screen. A label appearing more than three times belongs in a column header, a
section header, or nowhere. Four rating labels printed once per card across five
cards is twenty printed labels carrying four labels' worth of information.

## 2. Prove the container before writing the grid

Compute this and write the number down:

```
columns x minimum usable column width + (columns - 1) x gutter + 2 x container padding
  <= container max-width
```

Minimum usable column width, unless the project proves otherwise:

| Content | Minimum |
|---|---|
| Title plus two metadata lines | 240px |
| Title only, or a single figure | 160px |
| Poster or thumbnail plus title | 200px |
| Body paragraph | 320px |

If the sum exceeds the container, you have three moves and must pick one: reduce
the column count, raise the container width, or change the pattern. Never ship the
grid and hope.

**The breakpoint and the container must agree.** A grid that switches to N columns
at a viewport width the container never reaches is dead code that renders as a
crush. Check the container's `max-width` against the breakpoint that triggers the
column count, in the same unit family.

**Dead gutter.** At the design's widest target, no single empty margin may exceed
15% of the viewport. A centred narrow container flanked by empty space is a
decision that has to be justified out loud, not a default that arrives because
`max-w-*` was the first thing typed.

## 3. Action hierarchy

- **One primary action per view.** Not one per card. Not one per row.
- **Per-item actions are icon, link, or menu.** Never a stack of full-width
  buttons inside a repeated unit.
- **`items x actions > 8`** → collapse. A menu, a segmented control, a single
  cycling toggle, or move the actions into a detail view or a row hover state.
- **A form control in every repeated unit is a table column, not a control.** A
  `<select>` repeated once per card is five controls competing for the same
  attention; make it one column of inline values, or put it behind the row.
- **Destructive and dismissive actions never sit at the same weight as the
  affirmative one.** "Not interested" and "Watched" are not peers.

## 4. Align the repeats

Comparable fields across repeated units must land on a shared axis. If unit
content varies in length and pushes a comparable field to a different offset in
each unit, you have two moves:

- Fix the varying field's height, by line clamp or reserved space.
- Lift the comparable field out of the repeated unit into a shared row or column.

Reserve space for anything asynchronous. An image that arrives late must occupy
its aspect ratio from first paint, or the row reflows under the reader.

## 5. Density

- Density comes from row count, not from tightness. Reaching more rows by cutting
  padding to 4px is not density, it is a legibility failure.
- Row heights: 36 to 40px dense, 48 to 52px comfortable. Pick one per surface and
  hold it.
- Grid gutters stay at or above 12px. Below that, adjacent units visually merge
  and the reader loses the boundary.
- Vertical rhythm comes from the project's spacing scale. Two adjacent steps of
  the scale must be visibly different, or the scale has too many steps.

## 6. Progressive disclosure

Once a repeated unit's primary content exceeds three lines, the surplus is
secondary and moves behind expansion, hover, or a detail view. Blurbs, warnings,
provenance and full metadata are surplus. Title, the one identifying figure, and
the one action are not.

Empty, loading and error states are part of the composition, not an afterthought.
Each one occupies the same region as the populated state and does not shift the
surrounding layout when it swaps.

## 7. Before handing over

Answer each with a number or a named move, not a yes:

1. Pattern chosen, with the item count and attribute count that justify it.
2. Container arithmetic, computed, and the result compared to the max-width.
3. Breakpoint unit family matches the container unit family.
4. Count of primary actions in the view. It is 1.
5. `items x actions` total, and the collapse used if it exceeds 8.
6. Every label's on-screen repeat count is 3 or fewer.
7. Comparable fields share an axis, and the fix used where content length varies.
8. Widest empty margin as a percentage of the viewport. It is under 15%.
9. Row height chosen and held; gutter at or above 12px.
10. Empty, loading and error states occupy the populated state's region.

If any answer is a yes rather than a number, you have not checked it.

## Refusal protocol

When a request asks for something this skill forbids, name the rule it hits in one
line and offer the nearest compliant arrangement. Do not silently comply, and do
not silently refuse. "A card per film puts four repeated rating labels on screen
twenty times; a table gives one header row and the same information. Cards are
right if the posters are real and carry the decision."
