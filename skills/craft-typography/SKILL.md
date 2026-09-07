---
name: craft-typography
description: Testable rules for type as a system — scale, measure, line-height, weight, tracking, hierarchy, webfont loading and numerals. Does not cover control anatomy; see craft-interface. Consult when setting or reviewing any type scale or block of text.
---

# craft: typography

## Purpose and scope

Carries no opinion on which typeface, scale ratio or size to use — those come from `design/decisions.md`.

## When to invoke

Setting a type scale for a new project, reviewing a render for typographic craft, or diagnosing feedback like "the heading is screaming" or "this reads as cramped".

## Inputs to inspect

- The rendered scale, at the sizes actually used on the surface, not just the token list.
- Line-height and measure together, not separately.
- `design/decisions.md` for any stated type thesis.
- The longest realistic string at each size.
- A specimen of the project's own content at its extremes, before any type decision is prescribed: headings, a long body passage, the shortest and longest real labels, numerals, punctuation, and one real string per required script. Where the project has no content yet, build the specimen from representative strings and label it as proof content.

## Rules (testable)

- Adjacent scale steps must be visually distinguishable at their actual rendered size, side by side, at a glance. Verify by rendering two adjacent steps and confirming a reader without a ruler can order them correctly.
- Line-height must scale down as measure narrows and up as measure widens; a fixed line-height across very different measures fails. Verify by checking line-height as a function of characters-per-line, not a single constant across the page.
- Measure stays within a readable character-count band for body text; verify by counting characters per line at the rendered width, not the token value. Where the project states a specific number rather than "readable", the stated-measure rule below is the one that governs.
- Every visual hierarchy level must be reachable through size, weight or position alone, with colour and decoration removed. Verify by viewing the page in greyscale at one weight and checking the order still reads.
- Display type — the largest size step in the scale — sets `line-height` between 1.0 and 1.1 (Apple Human Interface Guidelines; WWDC 2020, "The Details of UI Typography", which cites 1.05). Verify by reading the computed `line-height` ratio at the largest type size in the scale and confirming it falls inside the band.
- Tracking at display sizes must not be left at the body default; verify by comparing default tracking against the specimen at the actual display size.
- A heading level must not be skipped in the DOM even if visually restyled; verify with an accessibility tree or heading-order check, not the visual render alone.
- A surface carrying long-form body text must have its reading measure stated as a number — characters per line at the target width — and the render must match what was stated within 10 per cent. Verify by measuring the rendered column width against the average character width of the resolved body font at its rendered size, not by counting the token value or eyeballing the column. When the stated measure is a range rather than a single number, "within 10 per cent" means within 10 per cent of the band's nearer edge, not its midpoint — a render at 62 against a stated 68–75 is 8.8 per cent short of 68 and passes; one at 60 is 11.8 per cent short and fails. Where the project has no `design/decisions.md` to hold the number, state it in the reply, as with a Quick override. This rule fixes no value: any measure is compliant. An unstated measure, or a render that misses its own stated band by more than 10 per cent, is not.

- Form inputs must render at 16px or larger on touch viewports, and a `maximum-scale` or `user-scalable=no` viewport declaration is not an acceptable substitute — it fails WCAG 2.2 SC 1.4.4. Verify by reading the computed `font-size` of every text input at a phone viewport and grepping the viewport meta tag.
- Copy is stored in sentence case, and an all-caps appearance comes from `text-transform`; capitals in the DOM are announced letter by letter by some screen readers. Verify by reading the DOM text content, not the render.
- `line-height` is unitless. Verify by reading the computed value's ratio to font-size across two nested elements at different sizes.
- `text-wrap: balance` is applied to headings only; the engine stops balancing past a line cap and does nothing beyond it. The cap is a browser-version fact — confirmed at 6 lines in Chrome as of 2026-09-06; recheck and redate before relying on the number. Verify by rendering the element at a width that produces more lines than the cap and confirming the wrap is unchanged.
- Truncated text must have a route to the full string. Verify by finding the full value in a title attribute, an expanded state, or a detail view.
- A characteristic that has a high-level property — weight, style, stretch, optical sizing — must be set through that property, not `font-variation-settings`, which overrides the high-level property regardless of cascade position. Verify by grepping for `font-variation-settings` and checking each axis against the registered-axis table.
- `font-synthesis: none` is set at the root, so a missing weight or style fails visibly instead of being faked. Verify by reading the computed value at the root.
- Underlines use `text-decoration-thickness: from-font` and `text-decoration-skip-ink: auto`. Verify by reading both computed values.
- Ranges use an en dash, ellipses a single character, and a value and its unit are separated by a non-breaking space. Verify by reading the DOM text content for `-` between numerals, three consecutive periods, and a plain space before a unit.
- A self-hosted webfont must declare `font-display`, and the fallback it swaps from must carry the metric-override descriptors — `size-adjust`, and `ascent-override`, `descent-override` and `line-gap-override` where the fallback's metrics differ — derived from that webfont against that fallback, per `references/webfont-loading.md`. Verify by reading the `@font-face` blocks for the descriptors, then recording `layout-shift` entries from the Layout Instability API across the swap with the font request delayed: any shift attributed to the text block means the descriptors are absent or wrong.
- A variable axis or OpenType feature is set only after it has been found in the font binary — the axis in `fvar`, the feature in `GSUB` or `GPOS`. Verify by listing the file's axis and feature tags with `fonttools ttx -t fvar -t GSUB -t GPOS -o - <file>` or `fc-query`, and checking every `font-variation-settings` and `font-feature-settings` tag against that list; a specimen page is not the file, and an axis that cannot be verified is not set.
- A `unicode-range` subset split must cover every script the content actually contains, because the ranges decide which subset files are fetched at all. Verify by calling `document.fonts.check('1em <family>', sample)` with one real string per script in the content, confirming each returns true, and confirming the network log shows the subset carrying that script was requested.

## Open questions / to be evidenced

- What perceptual-distinctness threshold (in px or ratio) reliably separates adjacent scale steps across common ratios?
- What measure range in characters-per-line holds across the type sizes seen so far? Narrowed by `references/measure.md` (Bringhurst's print-derived 45–75/60–70 band), not closed — the band is not yet confirmed to hold on screen.
- Does optical sizing (variable font `opsz`) matter enough at real project sizes to become a rule, or does it stay a heuristic?
- How much does metric-mismatch in fallback fonts actually shift layout in practice, and at what threshold does it matter?
- Tabular vs proportional numerals: answered for tables and live counters; open for running text.

Measured thresholds, specimen comparisons and cited sources go in `references/` — see `references/README.md`.

