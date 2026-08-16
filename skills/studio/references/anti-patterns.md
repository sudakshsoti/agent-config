# Anti-patterns

Load this before making a visual decision. Applies to both artifact shapes,
`document` and `page`. Each ban carries its reason, because the reason is what
generalises to the case not listed here.

## Structural

- **A card or border around every section.** Headings already separate prose
  sections, so the boxes add noise and steal horizontal space for nothing.
- **Alternating coloured section bands.** *Document only — a page may do this
  when the content is genuinely parallel.* Bands cut a continuous argument
  into slabs and imply the sections differ in kind when they do not.
- **Left-edge accent stripes on every block.** A stripe means "this one is
  different". On every block it means nothing and narrows the measure.
- **Identical repeated card grids.** *Document only — a page may do this when
  the content is genuinely parallel.* A grid claims the items are parallel and
  equally weighted. Document content rarely is, so it flattens real
  hierarchy.
- **Full-bleed prose.** Past roughly 80 characters the eye loses the line
  return and reading speed drops. Constrain the measure however wide the
  viewport is.
- **Centred body text.** A ragged left edge forces the eye to hunt for each
  line start. Centre a title if you must, never a paragraph.
- **An oversized hero heading.** *Document only — a page may do this when the
  content is genuinely parallel.* A hero sells a page to someone who has not
  committed; a document's reader already has. It gets a title, not a hero.

## Chromatic

- **Gradients of any kind, especially gradient text via `background-clip:
  text`.** Pure decoration carrying no information, and on text it wrecks
  contrast midway through the word.
- **Saturated accent colours.** At reading lengths high-chroma colour fatigues
  the eye and pulls attention off the words. Desaturate.
  *Lifts when the colour is never set as reading-length text.* Chroma above
  roughly 0.15 is allowed for a large flat field or a solid fill with its own
  paired ink, because the objection is to fatigue over a paragraph, not to the
  chroma itself. A link in running text is the furthest an accent of that
  chroma may go. `calm` is the direction this exemption exists for.
- **More than one accent hue.** Two accents give the reader two competing
  signals and neither one means anything after the second use.
- **Pure `#000` or `#fff`.** Maximum contrast on a long read is harsh. Tint
  the neutrals toward the accent so the page reads as one considered object.
  *Never lifts for `#000`*, which has no hue to tint the ladder from and clips
  to the panel's own black on OLED. *Lifts for the ground only* on a surface
  built for scanning rather than reading, where an unbiased sheet is the point.
  Even then, stop at `oklch(0.995 0 0)`: it is indistinguishable from white,
  and it keeps the ladder inside one system. `instrument` is the direction this
  exemption exists for.
- **Communicating meaning by colour alone.** Documents get printed and read
  in greyscale, so every callout and status carries a text label as well. This
  reaches the primary button too: if the only thing separating it from a
  secondary control is a fill, it is a plain box in greyscale. Give it a second
  signal — a border that the secondary lacks, or a heavier label.

## Decorative

- **Pills and badges as decoration.** A pill is a container for a value.
  Empty of a value it is just a rounded rectangle competing with the text.
- **Emoji or icons with no informational content.** They cost vertical space
  and reading attention, and return nothing the words did not already say.
- **More than one hairline-weight shadow.** *Document only — a page may do
  this when the content is genuinely parallel.* Shadows imply layers. A
  document is one surface, so a second depth level is a lie about the
  structure.
- **`01 / 02 / 03` numbered markers.** Numbers promise an ordered sequence.
  Unless the content genuinely is one, the reader hunts for an order that is
  not there.
- **Animation of any kind unless explicitly requested.** Motion draws the eye
  away from the sentence being read, and breaks entirely in print and in PDF
  export.

## Fabrication

- **Fake dashboard metrics.** Inventing numbers to fill a layout makes the
  whole artifact untrustworthy, including the parts that are true.
- **Illustrative sparklines.** A chart shape with no data behind it asserts a
  trend that was never measured.
- **Placeholder or lorem text.** It ships as-is more often than not, and
  tells the reader the author did not finish.
- **A chart where a table would read better.** Under about a dozen values a
  chart loses precision and gains nothing. Give the reader the actual
  numbers.
- **Stat blocks for numbers that were not measured.** Large-type figures
  carry authority; spending it on a guess spends credibility on nothing.

## Typesetting

- **Proportional figures in a table or a stat block.** Default figures in most
  grotesques are proportional, so a `1` is narrower than a `7` and a column of
  numbers will not align down its own decimal. Any artifact containing a
  `<table>`, a `.stat` or a run of compared figures sets
  `font-variant-numeric: tabular-nums` on those elements. This is not optional
  in a direction built for comparison.
- **A neutral ladder with no `color-scheme`.** A dark artifact on a browser
  defaulting to light gets light native scrollbars, form controls and
  `::selection` against its own ground. Declare `color-scheme: dark` (or
  `light`) on `:root` so the chrome matches the page.
- **Depending on a hairline that `forced-colors` will repaint.** Windows High
  Contrast overrides border colours, so a direction whose entire elevation
  system is a 1px line loses it. Keep the border *present* under
  `forced-colors: active` rather than swapping to a fill, and never carry
  structure in a border's colour alone.

## Format

- **Anything requiring a build step, a framework or a CDN.** The output must
  render offline, from disk, years later. Each dependency is a future blank
  page. A remote webfont `<link>` is allowed and costs offline rendering;
  base64-embed the subset `woff2` for anything shareable.
- **JavaScript where `<details>` or `position: sticky` would do.** Native
  elements survive a JS-disabled context, print correctly and cost nothing.
- **Mermaid.** A bare browser opening a local file has no renderer for it, so
  the diagram arrives as a code block.
- **Raster images the model invented.** A generated illustration is a
  fabricated claim in picture form, and it bloats a file that must stay
  portable.

## Page

Ported from what a landing/overview page slides into by default:

- A purple-to-blue gradient standing in for a decision.
- Exactly three feature cards.
- Uniform border radius on everything.
- Emoji iconography.
- Decorative `01 / 02 / 03` markers.
- Shadows where nothing is elevated.
- A centred 1200px container as the only layout idea.
- Filler words: `seamlessly`, `effortlessly`, `powerful`, `beautiful`,
  `elevate`, `unlock`, `supercharge`.
- Three-item lists purely for rhythm.
- Invented statistics.

**Nobody uses blur for elevation.** Ramp uses a 1px border and no shadow,
Linear uses `0 0 0 1px` and `0 0 0 2px` rings, V7 uses nothing, New Yorker's
article shell has none. The agent default `0 4px 6px rgba(0,0,0,0.1)` matches
none of the seven references.

## The three current AI defaults

AI-generated design right now clusters around three looks. Landing on one of
them by accident is the specific failure this file exists to prevent, because
the result reads as machine output regardless of how well executed it is.

1. Warm cream background near `#F4F1EA`, high-contrast serif display type,
   terracotta accent.
2. Near-black background with a single bright acid-green or vermilion accent.
3. Broadsheet layout: hairline rules, zero border-radius, dense newspaper
   columns.

If the brief explicitly asks for one of these, the brief wins. The rule only
binds on axes the brief left free. (Source: Anthropic's `frontend-design`
skill.)

Visual complexity follows informational complexity. A 400-word note gets a
header and prose and nothing else.
