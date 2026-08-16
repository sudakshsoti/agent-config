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
4. **Spacing gains two steps.** The measured 40px is already 2.5rem, so the
   reference set is six values. `--space-1` at 0.25rem and `--space-8` at 4rem
   are additions: a page needs one interval longer than an article shell does,
   and label-to-value gaps need one shorter.

## Ground and ink

| Token | OKLCH | Hex | On paper | Job |
| --- | --- | --- | --- | --- |
| `--ground` | `0.972 0.004 85` | `#f7f6f3` | 1.00:1 | the sheet |
| `--ground-2` | `0.945 0.005 85` | `#eeede9` | 1.08:1 | sunk field: code block, table header |
| `--ground-3` | `0.917 0.005 85` | `#e5e3e0` | 1.18:1 | deepest field: row hover, badge |
| `--ink` | `0.235 0.010 65` | `#211d19` | 15.39:1 | all body and display type |
| `--ink-2` | `0.475 0.010 65` | `#605b56` | 6.17:1 | utility type, captions, labels |
| `--ink-3` | `0.640 0.008 65` | `#908b87` | 3.11:1 | structural rules only, never text |
| `--hair` | `0.878 0.006 65` | `#dad6d3` | 1.33:1 | repeated separation |

Two hues, twenty degrees apart: the grounds sit at hue 85 and the inks and
rules at hue 65. The paper is yellower than the ink is red. That offset is what
makes the sheet read as warm while the ground itself carries almost no chroma.

The chroma ceiling on the grounds is 0.005. Cream, the `#F4F1EA` of AI default
one, sits near 0.015. Three times the chroma is the entire difference between
paper and cream, and it is the first thing to check if this direction starts
looking generated.

`--ground-3` at `#e5e3e0` lands on the reference's own `#e5e5e5` border tier,
warmer by five units of blue. The ladder and the measurement agree without
being made to.

## Surface ladder

**Elevation is not signalled, because there is no elevation.** The three
grounds are recession rather than lift: each step is a slightly sunk field cut
into the same sheet, and nothing ever sits above it. `--shadow-1: none`, which
matches the reference, whose article shell has no shadow at all.

Depth is carried by rules and space, in two weights:

- `--hair` at 1.33:1 for repeated separation, which tracks the reference's
  `#e5e5e5` 1px border tier at 1.27:1 against white.
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
| h3 | Source Serif 4 | 21px | 400 | 1.2 | `normal` |
| Body | Hanken Grotesk | 21px | 400 | 1.5 | `normal` |
| Utility | Hanken Grotesk | 13px | 500 | 1.4 | −0.0125em |
| Code | IBM Plex Mono | 13px | 400 | 1.5 | `normal` |

The reference's scale has nothing between 21px body and its 30px headline, so
h3 does not get a size of its own. It is the display serif at body size, and
the family switch plus the space above it is what makes it read as a heading.
A run-in subhead, the way print does it.

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
| `--radius-pill` | `999px` | the one solid button |

Radius is the exception here, not the default. Both small and medium are zero
on purpose, so reaching for a rounded corner requires typing a different token
name and noticing that you did.

`--radius-lg` is the reference's 4px table container. `--radius-pill` comes
from the reference's 64px sticky utility bar, which is the one place it lets a
control round: the single interactive element is a pill, and every other
rectangle on the page has hard corners.

Never round a panel, a section, an image, a table cell or a code block.

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

The measured six, `0.5 / 1 / 1.5 / 2 / 2.5 / 3rem`, sit at `--space-2` through
`--space-7`, with `--space-1` at 0.25rem below and `--space-8` at 4rem above.

The rhythm is deliberately uneven. A section opens with 3rem of space, then a
hairline, then 2rem, then the heading. Paragraphs inside it sit 1.5rem apart.
That ratio between "a new section starts here" and "the next paragraph starts
here" is the whole vertical structure of the page, and it is the reason no
section needs a border to be legible as a section.

`--space-1` is for label-to-value gaps only. `--space-8` separates the masthead
from the body and nothing else, so the one longest interval on the page marks
the one place the reader crosses from the title into the text.

## Signature move

**The standing rule with the label in the margin.**

Every section opens with a hairline across the full width. Below it, in a 10rem
left rail, the section's category is set in 13px utility type at −0.0125em and
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
4. **The broadsheet look.** Multi-column newspaper text, rules stacked on
   rules, all-caps everything, a drop cap, a dateline nobody wrote. That is AI
   default three. Rules here are single and horizontal, and prose is one column.
5. **Any `box-shadow`.** `--shadow-1: none`, and the reference's article shell
   has none. A shadow claims a second surface where there is one sheet.
6. **Radius on anything but the table container and the pill button.** Four
   rounded corners on a panel turns a printed page into an app screen, which is
   a different direction's job.
7. **Rubric red as a second accent.** It is measured and it is unused. Two
   hues means neither one signals anything after its second appearance.
8. **`--ink-3` as text at body or utility size.** It is 3.11:1, which is a rule
   colour. Small text is `--ink-2` at 6.17:1, body is `--ink` at 15.39:1.
9. **Centred prose, or a symmetrically centred layout.** The left rail exists
   to break the symmetry. A centred column with centred headings throws away
   the one structural idea the direction has.
10. **A card grid standing in for a comparison.** Four items with four
    attributes each is a table. A grid of panels claims the items are parallel
    and equally weighted, and costs the reader the ability to compare down a
    column.

## Token map

| Token | Value | What it means here |
| --- | --- | --- |
| `--ground` | `oklch(0.972 0.004 85)` | the sheet, every page and every section |
| `--ground-2` | `oklch(0.945 0.005 85)` | sunk field: code block, table header |
| `--ground-3` | `oklch(0.917 0.005 85)` | deepest field: row hover, badge fill |
| `--ink` | `oklch(0.235 0.010 65)` | all display and body type, and button hover fill |
| `--ink-2` | `oklch(0.475 0.010 65)` | utility type: eyebrow, caption, meta, table header |
| `--ink-3` | `oklch(0.640 0.008 65)` | structural rules and the ghost button border. Never text |
| `--hair` | `oklch(0.878 0.006 65)` | every repeated rule: section tops, table rows, footer |
| `--accent` | `oklch(0.510 0.128 245.4)` | link underline, solid button fill, focus ring. Nothing else |
| `--accent-ink` | `oklch(0.972 0.004 85)` | paper, as the label on the solid button |
| `--radius-sm` | `0` | inert by design: the default corner is square |
| `--radius-md` | `0` | inert by design: the default corner is square |
| `--radius-lg` | `4px` | the table container only |
| `--radius-pill` | `999px` | the solid button and the badge |
| `--font-display` | `"Source Serif 4", Georgia, serif` | h1, h2, h3, and the direction name in a stacked table |
| `--font-body` | `"Hanken Grotesk", system-ui, sans-serif` | body, lead, and all utility type |
| `--font-mono` | `"IBM Plex Mono", ui-monospace, Menlo, monospace` | the code block only |
| `--text-base` | `21px` | body, and the reference's article body size |
| `--text-h1` | `clamp(30px, 1.6rem + 1.14vw, 42px)` | the measured 30 → 42px headline, fluid between them |
| `--text-h2` | `clamp(24px, 1.36rem + 0.57vw, 30px)` | section headings, topping out at the headline's floor |
| `--text-h3` | `21px` | equals `--text-base` on purpose: a run-in serif subhead |
| `--text-small` | `13px` | utility type, and the code block |
| `--leading-body` | `1.5` | the reference's 21px / 1.5em body |
| `--leading-display` | `1.0667` | the reference's headline leading, at every heading level |
| `--track-display` | `normal` | inert by design, and the point of the direction |
| `--track-body` | `normal` | inert by design. Negative tracking has no token here |
| `--measure` | `64ch` | every run of prose, whatever the viewport |
| `--space-1` | `0.25rem` | label to value, and nothing else |
| `--space-2` | `0.5rem` | inside a line: badge padding, nav gaps |
| `--space-3` | `1rem` | table cell padding, code block padding |
| `--space-4` | `1.5rem` | paragraph to paragraph, page gutter |
| `--space-5` | `2rem` | hairline to heading |
| `--space-6` | `2.5rem` | the rail gutter, heading to table |
| `--space-7` | `3rem` | section to section |
| `--space-8` | `4rem` | masthead to body, once per page |
| `--shadow-1` | `none` | inert by design. Depth is rules and space |

Deliberately inert: `--radius-sm`, `--radius-md`, `--track-display`,
`--track-body` and `--shadow-1`. Five of the thirty-five tokens declare that
this direction does not do a thing, which is why they are declared rather than
omitted: swapping a different direction's `tokens.css` in has to change them,
not leave them undefined.

The operator's ladder carries a second rule weight, `--rule-hard` at
`oklch(0.760 0.008 65)`, which has no slot in the shared token vocabulary. A
heavier rule here is drawn in `--ink-3` instead, one step darker than
`--rule-hard`, so that the two rule weights read as clearly different rather
than nearly the same.
