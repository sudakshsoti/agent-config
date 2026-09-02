---
name: interface-composition
description: |
  Arrangement arithmetic for product UI: verifying table vs list vs card grid
  against item and attribute counts; column and container maths; density and
  row height; action counts; alignment across repeated units; progressive
  disclosure. Runs **after** `app-ui` has decided the design, on any screen that
  repeats a unit, compares records, or carries per-item controls. Use when
  columns do not fit, a grid crushes at some width, every row carries too many
  buttons, or values that should line up do not. It catches defects; it does not
  design. Not for component behaviour, state, data flow or tests.
---

# Interface composition

Material and arrangement are separate failures. A screen can have a correct token
system, correct contrast, tabular numerals and a disciplined palette, and still be
unusable because five things are compared in five columns that cannot fit, or
because every repeated unit carries three equal-weight buttons.

This skill is arrangement only. Every rule here is checkable against your own
output. If a rule cannot be checked, it does not belong in this file.

**Handoff in.** `app-ui` has already fixed the brief, the shell, the unit, the
tokens (base unit, type scale, gutter, margin, container max-width) and the
wireframe. Do not re-decide them here. This skill takes those decisions and
proves they fit. If `app-ui` did not run, or the container max-width was never
written down, stop and go back; nothing below can be computed without it.

**Handoff out.** `design-review` receives the ten answers in §7 plus renders at
390 / 900 / 1440. It judges fit, shell absence and reference fidelity; this skill
never does. A screen that passes everything here can still be a bad screen, so
never treat a clean pass as a finished design.

Work in order: verify the pattern, prove the container, place the actions, align
the repeats, then hand over.

## 1. Verify the pattern, with counts

`app-ui` §3 chose the unit. This skill does not choose again; it checks that the
choice survives counting. Count the repeated items and count the attributes they
share, then write one sentence with both numbers: "Five films compared on four
rating sources, so a table with one header row." If the sentence does not carry
the counts, the check has not been done.

The choice fails, and goes back to `app-ui`, when:

- 3 or more shared attributes are compared across items and the unit is a card.
  Comparison needs values on one shared axis and one set of column labels.
- A card grid's image is not real, or does not drive the decision.
- Fewer than 4 items with a single action each are laid out as a grid.
- Rows are numbered and order carries no information. Numbering is then
  decoration; delete it.

If the counts contradict the choice and `DESIGN.md` says nothing, `app-ui`'s
choice stands only after it is re-justified in that file.

**Repetition audit.** Count how many times each label appears on the finished
screen. A label appearing more than three times belongs in a column header, a
section header, or nowhere. Four rating labels printed once per card across five
cards is twenty printed labels carrying four labels' worth of information.

## 2. Prove the container before writing the grid

Card and list grids use the column maths below. A 12-column page scaffold uses
the gutter, margin and max-width `app-ui` §6 wrote down. Never mix the two on one
surface.

Compute this and write the number down:

```
columns x minimum usable column width + (columns - 1) x gutter + 2 x container padding
  <= container max-width
```

Minimum usable column width, unless the project proves otherwise:

| Content | Minimum |
|---|---|
| Title plus two metadata lines | 240px |
| Title only, or a single figure, in a card or list | 160px |
| A figure, date, status or badge column in a data table | 96px, ellipsis allowed |
| Poster or thumbnail plus title | 200px |
| Body paragraph | 320px |

If the sum exceeds the container, you have four moves and must pick one: reduce
the column count, raise the container width, change the pattern, or — for a data
table with more than six columns — allow horizontal scroll with a sticky header
and a sticky first column. Never ship the grid and hope.

**The breakpoint and the container must agree.** A grid that switches to N columns
at a viewport width the container never reaches is dead code that renders as a
crush. Convert both to px (rem × 16 at the default root) and compare: the
breakpoint that triggers the column count must be at or below the container's
`max-width`. "They match" without the two numbers is not a check.

**Dead gutter.** At the design's widest target, compute
`(viewport − container) / 2 / viewport`. Above 15% is a failure unless
`DESIGN.md` justifies it. A prose or reading surface with a 560–720px measure is
the one exemption; a data screen is never one.

## 3. Action hierarchy

- **One primary action per view.** Not one per card. Not one per row.
- **Per-item actions are icon, link, or menu.** Never a stack of full-width
  buttons inside a repeated unit.
- **`items x actions > 8`** → collapse. Count the controls visible in one
  viewport; the contents of an overflow menu do not count. Collapse into a menu,
  a segmented control, a single cycling toggle, a row hover state, or a detail
  view.
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
- Row heights on pointer surfaces: 36 to 40px dense, 48 to 52px comfortable. Pick
  one per surface and hold it. At 390, every row and control is at least 44px
  tall, whatever the desktop density.
- Grid gutters stay at or above 16px on an 8px base, 12px on a 4px base. Below
  that, adjacent units visually merge and the reader loses the boundary.
- Vertical rhythm comes from the project's spacing scale, as `app-ui` §6 set it.

## 6. Progressive disclosure

Once a repeated unit's primary content exceeds three lines at the project's body
size, the surplus is secondary and moves behind expansion, hover, or a detail
view. Blurbs, warnings, provenance and full metadata are surplus. Title, the one
identifying figure, and the one action are not.

`app-ui` §8 designed the empty, loading and error states. Verify each occupies the
populated state's region and does not shift the surrounding layout when it swaps.

## 7. Before handing over

Answer each with a number or a named move, not a yes:

1. Pattern verified, with the item count and attribute count that justify it.
2. Container arithmetic, computed, and the result compared to the max-width.
3. Breakpoint and container, both in px, and the breakpoint is the smaller.
4. Count of primary actions in the view. It is 1.
5. `items x actions` total, and the collapse used if it exceeds 8.
6. Every label's on-screen repeat count is 3 or fewer.
7. Comparable fields share an axis, and the fix used where content length varies.
8. Widest empty margin as a percentage of the viewport. It is under 15%.
9. Row height chosen and held; gutter at or above the base-unit minimum; every
   row and control at least 44px at 390.
10. Empty, loading and error states occupy the populated state's region.

If any answer is a yes rather than a number, you have not checked it.

## Refusal protocol

When a request asks for something this skill forbids, name the rule it hits in one
line and offer the nearest compliant arrangement. Do not silently comply, and do
not silently refuse. "A card per film puts four repeated rating labels on screen
twenty times; a table gives one header row and the same information. Cards are
right if the posters are real and carry the decision."
