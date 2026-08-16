# Vocabularies

**These are starting sets, not closed lists.** Reaching for a shape the set
lacks is allowed; say so in the hand-off, and expect `check.py` to WARN on the
novel class rather than fail.

These two class lists are the same ones `scripts/check.py` embeds as
`VOCAB_DOCUMENT` and `VOCAB_PAGE`. Changing one without the other is the
drift to avoid — keep them in sync.

## Document set

15 primitives, one line each naming the case it exists to handle:

- `.doc-header` + `.doc-meta` — the title block and its byline/date/tags.
- `.lead` — the opening paragraph that orients the reader before the body.
- `nav.toc` — a table of contents past roughly six sections.
- `.summary` — a top-of-document abstract or tl;dr.
- `aside.callout` with `--note` / `--warn` / `--rec` and `.callout-label` —
  an aside that needs to be seen out of reading order.
- `dl.kv` — a flat key/value list (metadata, specs, settings).
- `.table-wrap > table` — any tabular data, wrapped so it scrolls instead of
  overflowing narrow screens.
- `pre > code` — a code block or literal output.
- `blockquote` — a quoted passage attributed to someone else.
- `ol.steps` — a numbered procedure meant to be followed in order.
- `.stat-row > .stat` — a row of measured figures, never invented ones.
- `.bar` — a single proportional bar for one measured ratio.
- `details.appendix` — supporting material the reader can expand, not
  required for the main argument.
- `footer > ol.sources` — a citation list.
- footnotes (`sup` → `#fn-N`) — an inline reference to a footnote.

## Page set

- `.page-header` — the top masthead strip: logo/name plus primary nav.
- `.nav` — the primary navigation list.
- `.hero` — the above-the-fold opening section.
- `.hero-title` — the hero's single `h1`.
- `.hero-sub` — the hero's supporting line.
- `.section` — a full-width content section.
- `.section-head` — a section's heading block.
- `.eyebrow` — a small label above a heading naming its category.
- `.lead` — an opening paragraph orienting the reader.
- `.grid` — a layout grid for parallel items.
- `.panel` — a bordered or filled content block within a grid or section.
- `.feature` — one item in a feature grid.
- `.stat-row` — a row of measured figures.
- `.stat` — one measured figure within a `.stat-row`.
- `.quote` — a pulled quote or testimonial, only ever a real one.
- `.table-wrap` — a scroll-safe wrapper for tabular data.
- `.list` — a plain content list.
- `.steps` — a numbered or ordered procedure.
- `.cta` — a call-to-action button or link.
- `.btn` (+ `.btn--ghost`) — a button, with a lower-emphasis variant.
- `.note` — an inline aside or caveat.
- `.figure` — an image, diagram or SVG with its caption.
- `.caption` — the caption text for a `.figure`.
- `.divider` — a visual break between sections.
- `.code` — an inline or block code sample.
- `.badge` — a small status or category marker.
- `.meta` — small supporting metadata (date, author, tag).
- `.footer` — the closing footer.

## Specimen set

These are part of the page set, not a third shape: `check.py --shape page`
accepts them. They exist because a direction's `example.html` is a spec sheet,
and a spec sheet needs primitives a marketing page does not.

- `.swatch-grid` — the colour section's grid of chips.
- `.swatch` — one chip plus its labels.
- `.swatch-chip` — the colour area itself.
- `.swatch-name` — the token name, printed.
- `.swatch-value` — the token's literal value, printed.
- `.pair` — one ink shown in its sanctioned role on one ground.
- `.pair-label` — which two tokens that row is showing.
- `.type-row` — one step of the type scale.
- `.type-sample` — the words set at that step.
- `.type-spec` — token, family, size, weight, line-height, tracking for that step.
- `.glyphs` — the uppercase, lowercase, numeral and punctuation run for one family.
- `.scale-row` — one step of the spacing scale.
- `.scale-bar` — the bar whose width is that step.
- `.scale-label` — the step's token name and value.
- `.radius-row` — the radius scale laid out.
- `.radius-tile` — one corner sample.
- `.elev-row` — the elevation comparison laid out.
- `.elev-tile` — one surface in the comparison.
- `.state-row` — one interactive element repeated across its five states.
- `.state-label` — which state a copy is showing.
- `.field` — a form control with its label.

Forced states use `data-state`, not a class. Write each state once as a
selector list — `.btn:hover, .btn[data-state="hover"]` — so a forced state
and the real pseudo-class can never drift, and so no `.is-*` class has to
enter the vocabulary.
