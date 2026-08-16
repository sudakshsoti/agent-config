# editorial

## Thesis

Paper and ink, two families, and not one negative letterspace value.

A long read on a warm sheet. Structure comes from a hairline and the space
around it, never from a box. Nothing floats, nothing is rounded, nothing is
bold. The only decision the reader should notice is where the next section
starts.

## When to use, when not

Use it for long reads, essays, explainers, reports, post-mortems, and anything
whose reader already wants the content and is going to read it start to finish.
It is the direction for a document, and for the kind of page that is really a
document with a masthead.

Do not use it for pricing, feature comparisons or anything that has to argue a
case to someone who has not committed: that is `instrument`, which has bordered
cards and a real accent. Do not use it for a developer-tool surface, which is
`product-dark`. Do not use it for onboarding or consumer warmth, which is
`calm`, and which owns the large flat colour fields this direction refuses. And
do not reach for it because "editorial" sounds serious. If the artifact needs a
hero to sell itself, this is the wrong ground.

## Reference values

Measured against The New Yorker, Pope.L article, served CSS rather than
computed. These are the reference's own numbers, reproduced as measured:

| Property | Measured value |
| --- | --- |
| Ground | `#fff` base, `#f5f5f5` subtle and hover, `#e5e5e5` 1px borders |
| Ink | `#000` |
| Display | `IrvinHeadingPro`, weight 400, 30px → 36px → **42px**, line-height 1.0667, **tracking `normal`** |
| Body | `TNYAdobeCaslonPro`, **21px / 1.5em**, weight 400 |
| Utility / nav | Graphik 12–13px, weight 400/500, tracking −0.0125em |
| Measure | grid columns 3 / span 8 of 12 at ≥768px |
| Radius | almost nowhere: 4px table container, 50% avatar, 64px sticky utility |
| Accents | action blue `#0879bf`, pressed `#07588b`, rubric red `#db3334` |
| Spacing | 0.5, 1, 1.5, 2, 2.5, 3rem, 40px |
| Shadow | none in the article shell |

**Measured against, not copied from.** Four deliberate departures:

1. **Ground and ink are the operator's own ladder**, from
   `docs/2026-08-15-omp-audit-explainer.html:9-15`, not `#fff` on `#000`. Pure
   white and pure black are banned by `references/anti-patterns.md`, and the
   ladder is already in production use, so this direction inherits it rather
   than inventing a second paper.
2. **The faces are different, the constraint is not.** IrvinHeadingPro, Adobe
   Caslon Pro and Graphik are not held. Source Serif 4 carries display and
   Hanken Grotesk carries body and utility, which inverts the reference's
   serif-body against sans-display arrangement. What survives the substitution
   is what actually made the reference: two families, weight 400 on display,
   and tracking at zero.
3. **The accent is darkened.** `#0879bf` reaches 4.31:1 against this paper, not
   the 4.69:1 it gets against `#fff`, so it fails AA for body text as a link
   colour. `oklch(0.510 0.128 245.4)` holds the measured hue and reaches
   5.26:1.
4. **The spacing scale keeps five of the measured six and re-ends both ends.**
   The measured set is 0.5 / 1 / 1.5 / 2 / 2.5 / 3rem. 2.5rem is dropped,
   because 2 / 2.5 / 3 is three values inside a 20% span and at section scale
   the reader cannot tell them apart. 0.75rem is added at the bottom, where a
   label-to-value gap needs a step between 0.5 and 1, and the top step goes to
   6rem rather than 4rem so the one longest interval on the page is
   unmistakably longer than a section break.
5. **The ground ladder's deepest step is pushed down.** The measured border
   tier is `#e5e5e5`, and matching it put `--ground-3` only 1.09:1 away from
   `--ground-2` — two sunk fields the reader cannot tell apart. `--ground-3`
   drops to `oklch(0.900 0.005 85)` and `--hair` follows to
   `oklch(0.855 0.006 65)` so a rule still reads when it is drawn on the
   deepest field.

## Ground and ink

| Token | OKLCH | Hex | On paper | Job |
| --- | --- | --- | --- | --- |
| `--ground` | `0.972 0.004 85` | `#f7f6f3` | 1.00:1 | the sheet |
| `--ground-2` | `0.945 0.005 85` | `#eeede9` | 1.08:1 | sunk field: code block, table header |
| `--ground-3` | `0.900 0.005 85` | `#dfdeda` | 1.24:1 | deepest field: row hover, badge |
| `--ink` | `0.235 0.010 65` | `#211d19` | 15.39:1 | all body and display type |
| `--ink-2` | `0.475 0.010 65` | `#605b56` | 6.17:1 | utility type, captions, labels |
| `--ink-3` | `0.640 0.008 65` | `#908b87` | 3.11:1 | structural rules only, never text |
| `--hair` | `0.855 0.006 65` | `#d2cfcb` | 1.44:1 | repeated separation |

Two hues, twenty degrees apart: the grounds sit at hue 85 and the inks and
rules at hue 65. The paper is yellower than the ink is red. That offset is what
makes the sheet read as warm while the ground itself carries almost no chroma.

The chroma ceiling on the grounds is 0.005. Cream, the `#F4F1EA` of AI default
one, sits near 0.015. Three times the chroma is the entire difference between
paper and cream, and it is the first thing to check if this direction starts
looking generated.

The two sunk fields sit 1.15:1 apart from each other, which is the smallest
step in the direction that is still a step. An earlier ladder put them 1.09:1
apart to land `--ground-3` on the reference's own `#e5e5e5` border tier; the
match was pleasing and the distinction was invisible, so the tier was given up
and the separation kept.

`--ink-2` on `--ground-3` is 4.97:1 and `--accent` on it is 4.23:1. Small text
on the deepest field is therefore `--ink-2`, and the accent may not set text
there at all.

## Surface ladder

**Elevation is not signalled, because there is no elevation.** The three
grounds are recession rather than lift: each step is a slightly sunk field cut
into the same sheet, and nothing ever sits above it. `--shadow-1: none`, which
matches the reference, whose article shell has no shadow at all.

Depth is carried by rules and space, in two weights:

- `--hair` at 1.44:1 for repeated separation. Heavier than the reference's
  `#e5e5e5` tier, which measures 1.27:1 against white, because this paper is
  darker than white and a rule matched to the reference's ratio would go
  missing on `--ground-3`.
- `--ink-3` at 3.11:1 for the two divisions that carry structural weight: the
  rule under the masthead and the rule under a table header. 3:1 is the WCAG
  non-text threshold, so this is the lightest a rule is allowed to be while
  still meaning something.

Everything else is vertical space. A field is filled, never bordered and
filled: `--ground-2` for the code block and the table header, `--ground-3` for
row hover and the badge.

## Type roles

| Role | Family | Size | Weight | Line-height | Tracking |
| --- | --- | --- | --- | --- | --- |
| h1 | Source Serif 4 | `clamp(30px, 1.6rem + 1.14vw, 42px)` | 400 | 1.0667 | `normal` |
| h2 | Source Serif 4 | `clamp(24px, 1.36rem + 0.57vw, 30px)` | 400 | 1.0667 | `normal` |
| h3 | Source Serif 4 *italic* | 21px | 400 | `--leading-h3` (1.2) | `normal` |
| Body | Hanken Grotesk | 21px | 400 | 1.5 | `normal` |
| Emphasis, pull quote, citation | Source Serif 4 *italic* | inherits | 400 | inherits | `normal` |
| Meta | Hanken Grotesk | 15px | 400 | 1.45 | `normal` |
| Utility | Hanken Grotesk | 13px | 500 | 1.4 | −0.0125em |
| Code | IBM Plex Mono | 13px | 400 | 1.5 | `normal` |

The reference's scale has nothing between 21px body and its 30px headline, so
h3 does not get a size of its own. It is the display serif at body size, set
**italic**, which is how print marks a run-in subhead. The family switch alone
was not enough separation: at the same size, the same weight and the same
colour as the paragraph under it, an upright serif h3 differed from body by one
variable. The italic is the second.

Italic is a role here, not an effect. Source Serif 4 ships a true italic, and
it carries emphasis inside prose, the pull quote and a cited title. It is the
only hierarchy signal in the direction that costs no size, no weight and no
colour, which is why a direction with no bold has one.

`--text-meta` at 15px fills the gap between 21px body and 13px utility. Table
cells, captions, footnotes and figure credits live there. Without it every one
of them takes 13px, a size the reference chose for a navigation bar.

Display weight is 400 at every size, 42px included. There is no bold anywhere
in this direction. Weight 500 exists only on 13px utility type, where it is
doing the work tracking would otherwise do.

Utility type carries the reference's −0.0125em and is the only negative
tracking in the direction.

## Radius scale

| Token | Value | Where |
| --- | --- | --- |
| `--radius-sm` | `0` | everything, by default |
| `--radius-md` | `0` | everything, by default |
| `--radius-lg` | `4px` | the table container, and nothing else |
| `--radius-pill` | `999px` | the badge, and the solid button if the page has one |

Radius is the exception here, not the default. Both small and medium are zero
on purpose, so reaching for a rounded corner requires typing a different token
name and noticing that you did.

`--radius-lg` is the reference's 4px table container. `--radius-pill` comes
from the reference's 64px sticky utility bar, which is the one place it lets a
control round.

The pill is allowed on exactly two things, the badge and the solid button, and
a page carries at most one of each. Every other rectangle has hard corners.
Never round a panel, a section, an image, a table cell or a code block.

`--radius-sm` and `--radius-md` are both zero. They are two tokens refusing the
same thing, and they stay separate rather than collapsing because a consumer
swapping another direction's `tokens.css` in has to overwrite both.

## Accent policy

One hue: `oklch(0.510 0.128 245.4)`, the reference's action blue held at its
measured hue and darkened until it passes AA on paper.

Blue rather than the rubric red, for two reasons. The accent has to survive
being a link colour inside a long read, and red at `oklch(0.586 0.204 26)`
carries 0.204 chroma, which fatigues the eye at reading lengths. The rubric red
is measured, and it is unused.

The accent appears in exactly three places: the underline under a link, the
fill of the one solid button, and the focus ring. Nothing else is accented, and
no second hue is introduced for a second meaning.

Contrast limits, measured: the accent as text is legal on `--ground` (5.26:1)
and on `--ground-2` (4.86:1), and illegal on `--ground-3` (4.46:1). Paper on
the accent is 5.26:1, so the solid button passes AA for its 13px label.

States are made without a fourth colour. A link is `--ink` with an accent
underline, goes accent on hover, and thickens its underline to 2px when
pressed, because there is no pressed token to reach for. The solid button
hovers to `--ink` rather than to a darker blue: blue to near-black is the
strongest state change available inside a three-colour system.

## Spacing rhythm

`0.25 / 0.5 / 0.75 / 1 / 1.5 / 2 / 3 / 6rem`. Five of the measured six survive
at `--space-2`, `--space-4`, `--space-5`, `--space-6` and `--space-7`.

The scale is fine-grained where things touch and widens where things separate,
and the intervals must widen rather than narrow. The measured set ended
`2 / 2.5 / 3rem`, three values inside a 20% span, which at section scale is one
value written three ways. 2.5rem is dropped for that reason. 0.75rem is added
at the other end, where the gap between a 13px label and its value needs a step
between 0.5 and 1.

| Token | Value | Where |
| --- | --- | --- |
| `--space-1` | 0.25rem | inside a badge, the focus-ring offset |
| `--space-2` | 0.5rem | badge padding, nav gaps |
| `--space-3` | 0.75rem | label to value |
| `--space-4` | 1rem | table cell padding, code block padding |
| `--space-5` | 1.5rem | paragraph to paragraph, page gutter |
| `--space-6` | 2rem | hairline to heading, the rail gutter, heading to table |
| `--space-7` | 3rem | section to section |
| `--space-8` | 6rem | masthead to body, once per page |

The rhythm is deliberately uneven. A section opens with 3rem of space, then a
hairline, then 2rem, then the heading. Paragraphs inside it sit 1.5rem apart.
That ratio between "a new section starts here" and "the next paragraph starts
here" is the whole vertical structure of the page, and it is the reason no
section needs a border to be legible as a section.

`--space-8` separates the masthead from the body and nothing else. At double
the section break rather than the old one-and-a-third, the one longest interval
on the page is unmistakable as the place the reader crosses from the title into
the text.

## Signature move

**The standing rule with the label in the margin.**

Every section opens with a hairline across the full width. Below it, in a
`--rail` left rail of 10rem, the section's category is set in 13px utility type at −0.0125em and
right-aligned against the gutter, so it reads as a margin note rather than a
label stuck on top of a heading. The heading hangs in the content column on the
same line, at up to 42px, weight 400, tracking zero. Below 900px the rail
collapses and the category sits directly above the heading.

This is the reference's twelve-column grid, which starts its content at column
3 and spans 8, reduced to two columns: a rail and the measure. It gives the
page an asymmetric left edge and a visible sense of margin without a single
box, card or coloured band.

## Avoid list

1. **Cream ground, high-contrast display serif, terracotta accent.** This is AI
   default one, and this direction is a single wrong step away from it. The
   guards are numeric: ground chroma at or below 0.005 against cream's 0.015,
   Source Serif 4 held at weight 400 because it is a low-contrast text serif
   and reads as one, and blue as the only accent.
2. **Negative tracking on display or body type.** Zero at 42px is the
   direction. The reference's own 13px utility tracking of −0.0125em is the one
   exception, and it is deliberately not given a token so it cannot drift
   upward onto a headline.
3. **Source Serif 4 above weight 400, anywhere.** The reference's display
   weight is 400. A bold serif headline is the fastest route to looking like a
   template that was told the word "editorial".
4. **The broadsheet look.** That is AI default three, and this direction is
   the closest of the four to it, so the guard is structural rather than a
   matter of taste: **prose is one column at every viewport, and a view carries
   at most two rule weights** (`--hair` for repetition, `--ink-3` for the two
   structural divisions). No multi-column text, no rules stacked on rules, no
   all-caps run longer than a label, no drop cap, no invented dateline.
5. **Any `box-shadow`.** `--shadow-1: none`, and the reference's article shell
   has none. A shadow claims a second surface where there is one sheet.
6. **Radius on anything but the table container, the badge and the solid
   button.** Four rounded corners on a panel turns a printed page into an app
   screen, which is a different direction's job. `--radius-sm` and
   `--radius-md` are zero, so reaching for a rounded corner means typing a
   different token name and noticing that you did.
7. **Rubric red as a second accent.** It is measured and it is unused. Two
   hues means neither one signals anything after its second appearance.
8. **`--ink-3` as live text, and the accent as text on `--ground-3`.**
   `--ink-3` is 3.11:1 on paper and 2.50:1 on the deepest field: it is a rule
   colour, and the one text use it gets is a disabled control's label, which
   WCAG 1.4.3 exempts as an inactive component and which is *supposed* to
   recede. Everything a reader can act on or read is `--ink` or `--ink-2`. The
   accent reaches only 4.23:1 on `--ground-3`, so text on the deepest field is
   `--ink-2` at 4.97:1 or darker.
9. **Centred prose, or a symmetrically centred layout.** The left rail exists
   to break the symmetry. A centred column with centred headings throws away
   the one structural idea the direction has.
10. **13px standing in for every small thing.** `--text-meta` at 15px exists
    for table cells, captions, footnotes and credits. 13px is utility type: an
    eyebrow, a nav item, a code line. Sending body-adjacent content to 13px
    because it is "small" is how a document ends up set at two sizes.

A card grid standing in for a comparison is also out, though it is the shared
list's rule rather than this direction's: four items with four attributes each
is a table, and a grid of panels costs the reader the ability to compare down a
column.

## Token map

| Token | Value | What it means here |
| --- | --- | --- |
| `--ground` | `oklch(0.972 0.004 85)` | the sheet, every page and every section |
| `--ground-2` | `oklch(0.945 0.005 85)` | sunk field: code block, table header |
| `--ground-3` | `oklch(0.900 0.005 85)` | deepest field: row hover, badge fill |
| `--ink` | `oklch(0.235 0.010 65)` | all display and body type, and button hover fill |
| `--ink-2` | `oklch(0.475 0.010 65)` | utility type: eyebrow, caption, meta, table header |
| `--ink-3` | `oklch(0.640 0.008 65)` | structural rules and the ghost button border. Never text |
| `--hair` | `oklch(0.855 0.006 65)` | every repeated rule: section tops, table rows, footer |
| `--accent` | `oklch(0.510 0.128 245.4)` | link underline, solid button fill, focus ring. Nothing else |
| `--accent-ink` | `oklch(0.972 0.004 85)` | paper, as the label on the solid button |
| `--ring` | `oklch(0.510 0.128 245.4)` | the `:focus-visible` ring, the accent's third and last job |
| `--ring-offset` | `0.25rem` | the gap between the ring and what it rings, always filled with `--ground` |
| `--radius-sm` | `0` | inert by design: the default corner is square |
| `--radius-md` | `0` | inert by design: the default corner is square |
| `--radius-lg` | `4px` | the table container only |
| `--radius-pill` | `999px` | the badge, and the solid button if the page has one |
| `--font-display` | `"Source Serif 4", Georgia, serif` | h1, h2, h3, and the direction name in a stacked table |
| `--font-body` | `"Hanken Grotesk", system-ui, sans-serif` | body, lead, and all utility type |
| `--font-mono` | `"IBM Plex Mono", ui-monospace, Menlo, monospace` | the code block only |
| `--text-base` | `21px` | body, and the reference's article body size |
| `--text-h1` | `clamp(30px, 1.6rem + 1.14vw, 42px)` | the measured 30 → 42px headline, fluid between them |
| `--text-h2` | `clamp(24px, 1.36rem + 0.57vw, 30px)` | section headings, topping out at the headline's floor |
| `--text-h3` | `21px` | equals `--text-base` on purpose: a run-in serif subhead, set italic |
| `--text-meta` | `15px` | table cells, captions, footnotes, figure credits |
| `--text-small` | `13px` | utility type, and the code block |
| `--leading-body` | `1.5` | the reference's 21px / 1.5em body |
| `--leading-h3` | `1.2` | the run-in subhead, which `--leading-display` would collide on |
| `--leading-display` | `1.0667` | the reference's headline leading, at every heading level |
| `--track-display` | `normal` | inert by design, and the point of the direction |
| `--track-body` | `normal` | inert by design. Negative tracking has no token here |
| `--measure` | `64ch` | every run of prose, whatever the viewport |
| `--rail` | `10rem` | the left rail the signature move is built on |
| `--space-1` | `0.25rem` | inside a badge, the focus-ring offset |
| `--space-2` | `0.5rem` | badge padding, nav gaps |
| `--space-3` | `0.75rem` | label to value |
| `--space-4` | `1rem` | table cell padding, code block padding |
| `--space-5` | `1.5rem` | paragraph to paragraph, page gutter |
| `--space-6` | `2rem` | hairline to heading, the rail gutter, heading to table |
| `--space-7` | `3rem` | section to section |
| `--space-8` | `6rem` | masthead to body, once per page |
| `--shadow-1` | `none` | inert by design. Depth is rules and space |

Deliberately inert: `--radius-sm`, `--radius-md`, `--track-display`,
`--track-body` and `--shadow-1`. Five tokens declare that this direction does
not do a thing, which is why they are declared rather than omitted: swapping a
different direction's `tokens.css` in has to change them, not leave them
undefined.

Tracking is stated once and it is `normal`, so the fluid `--text-h1` needs no
optical-size compensation. That is a property of setting it at zero: a track
that does not exist cannot be wrong at 30px and right at 42px. It is the one
direction of the four where the fluid headline and the static tracking token do
not disagree.

`font-variant-numeric: tabular-nums` on every table and stat block. Hanken
Grotesk's default figures are proportional, and a report is mostly columns of
numbers.

The operator's ladder carries a second rule weight, `--rule-hard` at
`oklch(0.760 0.008 65)`, which has no slot in the shared token vocabulary. A
heavier rule here is drawn in `--ink-3` instead, one step darker than
`--rule-hard`, so that the two rule weights read as clearly different rather
than nearly the same.
