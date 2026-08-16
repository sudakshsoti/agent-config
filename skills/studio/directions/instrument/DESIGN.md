# instrument

## Thesis

One grotesque on a white ground, and a 1px hairline where every other page
would put a shadow.

## When to use, when not

Use it for pricing tables, plan comparisons, spec sheets, changelogs, API
overviews and technical product pages: content that is a set of facts the
reader is comparing rather than an argument they are following. The direction
is built to hold a lot of adjacent, equally weighted material without the page
turning into a pile of floating boxes.

Do not use it for a long read. The white ground, the 16px body and the
generous card insets are tuned for scanning, not for forty minutes of prose;
`editorial` exists for that. Do not use it when the subject is emotional or
consumer-facing, because a page whose only decoration is a ruled line reads as
cold on purpose; `calm` exists for that. Do not use it for a dark surface at
all: inverting this direction means re-deriving the whole ladder, which is
what `product-dark` already is.

## Reference values

Measured against Ramp's pricing page. These are measurements taken off that
page, not a copy of it. One value is reproduced exactly, the accent, because
the fact worth keeping about a single-accent page is which single colour it
picked. Everything else is a measurement this direction then answers in its
own terms: Lausanne is not available, so the family is a substitution, and the
sizes below h2, the spacing scale and the measure are derived rather than
measured because the reference does not expose them.

|Property|Measured on the reference|In this direction|
|---|---|---|
|Ground|`lab(100 0 0)`|`--ground: oklch(0.995 0 0)`, white one step off the ceiling|
|h1|64px / 64px, weight 400, tracking −0.01px|`--text-h1` clamps 40px → 64px, weight 400, `--track-display: -0.01em`|
|h2|48px / 50px|`--text-h2` clamps 32px → 48px, weight 400|
|Body|16px / 24px|`--text-base: 1rem`, `--leading-body: 1.5`|
|Card|transparent fill, 1px border, radius 8px, padding 40px 32px, no shadow|`--radius-lg: 0.5rem`, `padding: var(--space-6) var(--space-5)`, `--shadow-1: none`|
|CTA|radius 6px, padding 0 20px|`--radius-md: 0.375rem`, `padding: 0 var(--space-4)`, height from `min-height`|
|Radius scale|0.25 / 0.375 / 0.5 / 0.75 / 1 / 1.5rem|three tokens on three of those six steps, plus a true pill for badges|
|Accent|`lab(92.1406% -20.4979 84.7726)`|`--accent: oklch(0.92 0.2 114)`, the same colour converted|
|Families|one throughout|one throughout|

Two of those measurements are the direction's whole argument. The card has no
shadow, and the h1 tracking at 64px is −0.01px, which is arithmetically
nothing. The reference signals depth with a line and signals size with size.

## Ground and ink

The ground is `oklch(0.995 0 0)`, which renders `#fdfdfd` and sits 1.01:1 from
pure white. The instrument metaphor needs an unbiased surface, a measuring
sheet has no opinion, and the measured value is `lab(100 0 0)`. The shared
anti-pattern list bans a pure `#fff`, and rather than argue the exception this
direction takes the one step off the ceiling that no reader can see and every
checker can. The tint the eye-fatigue argument asks for still lives in the ink,
not in the sheet.

Every neutral shares one hue, 255, at chroma 0.004 to 0.014: a cool grey
family, dark enough at the top of the ladder to read as black without being
`#000`. The accent is the only warm thing on the page, at hue 114. That is why
it reads as a signal rather than as decoration, and it is the reason not to
tint the greys toward it.

Contrast, WCAG 2.2, against every ground each ink can land on:

| Ink | On `--ground` | On `--ground-2` | On `--ground-3` |
| --- | --- | --- | --- |
| `--ink` | 17.26 | 16.15 | 14.91 |
| `--ink-2` | 8.33 | 7.80 | 7.20 |
| `--ink-3` | 5.66 | 5.30 | 4.89 |

**Every ink clears AA on every ground, and that is deliberate.** `--ink-3` used
to sit at 4.95:1 on the sheet and 4.22:1 on `--ground-3`, so the direction
carried a rule saying "never put the label tier on the deepest ground". A rule
the author has to remember is a rule that gets broken, and the tier it applied
to was the smallest type on the page. `--ink-3` is now `oklch(0.510 0.011 255)`
and the rule is gone, replaced by a value that cannot fail.

`--ink-2` moved with it, from lightness 0.455 to 0.420, so three ink tiers stay
three tiers rather than compressing into two once the bottom one moved up.

## Surface ladder

Elevation is a line, not a blur. There is exactly one raised state and it is
signalled by the presence of a hairline: a transparent fill with
`1px solid var(--hair)` around it. Nothing else. There is no second raised
level, because a second level would need a second signal and the only one left
is a shadow.

Depth therefore runs downward instead of upward:

|Level|Token|What sits there|
|---|---|---|
|Page|`--ground`|the sheet everything is on|
|Sunk|`--ground-2`|code blocks, the footer strip, a pressed control|
|Deepest|`--ground-3`|table header row, inline code, a control mid-press|
|Raised|transparent + `--hair`|cards, panels, the lattice, the table container|

A raised surface never takes a fill and a sunk surface never takes a border,
so the two signals cannot be confused. `--shadow-1` is `none`, which means a
shadow can only reach this direction as a hardcoded value, and a hardcoded
value is the bug the token is there to catch.

## Type roles

One family carries everything read as language. The mono carries labels and
literals, which is a role, not a decoration: eyebrows, table headers, metadata
and code are all readouts.

|Role|Family|Size|Weight|Line-height|Tracking|
|---|---|---|---|---|---|
|h1|`--font-display`|`--text-h1` (40 → 64px)|400|`--leading-display`|`--track-display`|
|h2|`--font-display`|`--text-h2` (32 → 48px)|400|`--leading-display`|`--track-display`|
|h3|`--font-body`|`--text-h3` (22px)|500|`--leading-h3`|`--track-body`|
|Lead, thesis, pull quote|`--font-body`|`--text-h3` (22px)|400|`--leading-body`|`--track-body`|
|Body|`--font-body`|`--text-base` (16px)|400|`--leading-body`|`--track-body`|
|Button label|`--font-body`|`--text-base` (16px)|500|`--leading-body`|`--track-body`|
|Label, eyebrow, meta, table header|`--font-mono`|`--text-small` (13px)|500|`--leading-body`|`--track-body`|
|Code|`--font-mono`|`--text-small` (13px)|400|`--leading-body`|`--track-body`|

Body prose is `--ink` at 17.26:1, not `--ink-2`. This is a surface built for
scanning, and putting the most-read content on the second ink tier gives away
exactly the contrast scanning depends on. `--ink-2` is genuinely secondary:
table cells under a heading row, a caption, a note. The reference sets its own
body near-black for the same reason.

Display weight is 400 at 64px, matching the reference and the wider finding
that display weight across the measured set runs 300 to 510. Bold display is
not available in this direction; weight 500 is the heaviest thing on the page.

Weight 500 carries three roles — h3, button labels and mono labels — which in a
one-family system is one signal doing three jobs. h3 is 22px rather than 20px
so it separates from a 16px button label by size as well as by position, and
takes `--leading-h3` at 1.25 rather than the display leading.

`--leading-display` is 1.05, one value covering a measured 1.0 at h1 and 1.042
at h2. It rounds up rather than down so the h1 still clears its own descenders
once it clamps to 40px on a phone. **h2 adds 0.1 to it**, written
`calc(var(--leading-display) + 0.1)`, because h2 clamps to 32px and a
three-line heading at 33.6px of leading closes up. The h1 does not need it: it
clamps to 40px and the extra 2px of leading per line is enough at that size.

**Figures are tabular everywhere they are compared.**
`font-variant-numeric: tabular-nums` on every table, stat and price. Schibsted
Grotesk's default figures are proportional, so a `1` is narrower than a `7` and
a column of prices will not align down its own decimal. This direction exists
to be read down a column, which makes it the one property the whole thing
depends on.

`--track-display` is −0.01em where the reference measures −0.01px at 64px,
which is −0.00016em, indistinguishable from `normal`. The token is not the
measurement. It exists because Schibsted Grotesk stands in for Lausanne, and
any substitution changes the fit, so this is the one adjustable joint in the
type system. −0.01em is under half of Linear's −0.022em and a third of
Headspace's −0.03em: still reads as untracked, but it is a decision rather
than a default. `--track-body` is `normal`, exactly as measured, and is meant
to stay that way.

## Radius scale

The measured scale has six steps, 0.25 / 0.375 / 0.5 / 0.75 / 1 / 1.5rem, and
four tokens expose the four this direction uses:

|Token|Value|Used on|
|---|---|---|
|`--radius-sm`|0.25rem (4px)|table container, inline code|
|`--radius-md`|0.375rem (6px)|buttons and CTAs, the measured value|
|`--radius-lg`|0.5rem (8px)|a detached card or panel, the measured value|
|`--radius-pill`|`9999px`|small mono badges only|

The scale is the four values above and nothing else. The reference's 0.75rem
and 1rem steps are real, and they are **not** available by hand: a size no
token names is a hardcode, and a hardcode is what the token exists to catch.
If something genuinely needs a step between a control and a card, add the
token first.

`--radius-pill` is `9999px` rather than the measured 1.5rem. 1.5rem is the top
of the reference's scale, and on a 28px badge the browser clamps it to half the
height and produces a true capsule — but on a 44px control it produces a
lozenge that is neither a capsule nor a corner. A token whose correct use
depends on knowing the element's height is mis-specified. `9999px` always
produces a capsule, and "badges only" moves to the avoid-list where it can be
scored.

Zero is always available and is not a violation of the scale. The lattice, the
signature move below, has no radius at all, because two adjacent rounded
corners cannot share one line.

## Accent policy

One hue, `oklch(0.92 0.2 114)`, and it is a fill. It sits at 1.22:1 against
the ground, so it cannot be text, it cannot be a hairline, and it cannot
be a focus ring. Ink goes on top of it at 14.2:1, which is why
`--accent-ink` is the same value as `--ink` rather than white.

Where it is allowed: the primary button, a small mono badge, and the text
selection highlight. Two accent fills on a screen is the working ceiling. A
third and it stops meaning "act here".

**The accent may not be the only thing marking the primary action.** At 1.22:1
it is a light shape, and in greyscale, in print, or for a reader with a colour
deficiency it reads as an empty box. The shared list bans communicating meaning
by colour alone and the primary button is not exempt. The primary carries the
accent fill *and* a 1px `--ink` border; the secondary is a `--hair` border with
no fill. The pair is legible with the colour removed.

The focus ring is `--ring`, which is `--ink`, 2px at `--ring-offset`. That is a
direct consequence of a high-lightness accent and not a compromise: a ring the
reader cannot see is worse than a ring in a different colour. The offset is
filled with `--ground`, so the ring reads against the sheet whatever it is
ringing, including the accent fill and the primary's own ink border.

## Spacing rhythm

An 8px grid, with the two measured card values landing on it exactly.

|Token|Value|What it is for|
|---|---|---|
|`--space-1`|4px|focus-ring offset, inline code inset|
|`--space-2`|8px|heading to its own paragraph|
|`--space-3`|12px|mono label to its value|
|`--space-4`|16px|page gutter on a phone, gaps in a row of controls|
|`--space-5`|24px|paragraph flow, table cell inset, CTA horizontal inset|
|`--space-6`|32px|card horizontal padding, page gutter from 768px up|
|`--space-7`|40px|card vertical padding, and section vertical padding on a phone|
|`--space-8`|64px|section vertical padding from 768px up, and the masthead's gap|

12px is added because a 13px mono label and its value sit wrong at both 8px and
16px, and a page of labelled readouts hits that gap constantly. 96px comes off
the other end: the masthead's extra air is now 64px plus the section hairline,
which is one interval and a rule rather than a ninth value that appeared once.

The card's measured 40px vertical and 32px horizontal padding is
`var(--space-7) var(--space-6)` with nothing rounded. The CTA's measured
20px horizontal inset is the one value that is not a step on an 8px grid; it
rounds up to 24px, because keeping every inset on the scale is worth more than
the 4px. Vertical padding on a control is zero at every size: height comes
from `min-height: 44px`, which is how the reference gets a consistent control
height and is also the tap-target floor.

Sections are separated by 40px and a hairline on a phone, 64px and a hairline
from 768px up. That pair is the rhythm: air, then a line, then air. There is no
other divider.

## Signature move

**Cards share their borders.** Set them edge to edge in a grid with no gap and
the two 1px lines between them collapse into one, so the grid draws as a
lattice rather than as a row of objects hovering over a page. Build it by
putting the top and left hairline on the grid container and the right and
bottom hairline on each cell: no doubling anywhere, one continuous rule, and
it reflows to a single column on a phone without a line going missing.

**The cell count must fill the row.** Five items in a three-across lattice
leave a half row, and the empty slot has no cell to carry the right and bottom
hairline, so the rule stops in mid-air at the ragged edge. Two fixes, in order
of preference: change the column count so the grid divides evenly (five items
go five-across, or reflow to a list), or emit an empty cell that carries the
same borders and no content. Never leave the gap open. A lattice with a
half-drawn bottom edge reads as a rendering fault, which is the one thing a
direction whose depth *is* the line cannot afford.

The whole point is that depth is only ever a question of whether a line is
there. A shadow would say the cards are above the page; a shared border says
they are ruled onto it.

## Avoid list

1. **Any `box-shadow` at all, including an inset ring.** Border-only elevation
   is the entire direction, `--shadow-1` is `none`, and the reference has no
   shadow anywhere. A ring like `0 0 0 1px` is Linear's answer, not this one.
2. **A second accent hue.** The lime means "act here". A blue beside it and
   neither one means anything after its second appearance.
3. **The accent on text, a hairline, a focus ring, or as the only mark on the
   primary action.** At `oklch(0.92 ...)` it is 1.22:1 on the ground: a fill
   with ink on top, or invisible. And because it vanishes in greyscale, the
   primary button carries an `--ink` border the secondary lacks, so the pair
   still reads with the colour removed.
4. **Uneven card padding.** Every panel insets 40px by 32px. The lattice only
   reads as one ruled surface if every cell in it is the same box.
5. **A filled card.** A grey fill plus a border states depth twice and the
   fill wins, which takes the job away from the hairline. Fills belong to the
   sunk levels, `--ground-2` and `--ground-3`.
6. **A non-zero radius that is not one of the four tokens.** 0.75rem and 1rem
   are on the reference's scale and are still not available by hand: a size no
   token names is a hardcode. A 10px or 20px corner is nobody's measurement and
   reads as a second component library arriving.
7. **`--radius-pill` on anything taller than a badge.** It is `9999px`, so it
   always produces a capsule, which is exactly why the constraint has to be
   stated rather than enforced by the value. A capsule on a 44px control is a
   consumer app's button, not an instrument's.
8. **Display tracking past −0.01em.** The reference measures effectively none.
   −0.022em is Linear's signature and −0.03em is Headspace's; borrowing either
   makes this page read as the wrong direction.
9. **A second display family.** One grotesque throughout, mono for labels and
   literals. Two families is `editorial`'s move, and the whole measured set
   uses one or two, never three.
10. **Proportional figures in a table, a stat or a price.** Every compared
    number takes `font-variant-numeric: tabular-nums`. Without it a column of
    prices does not align down its own decimal, which costs the direction the
    one thing it exists to do.

## Token map

Colour, all in OKLCH at hue 255 except the accent:

- `--ground` — the page. A true white, the measured value.
- `--ground-2` — the first sunk level: code blocks, the footer strip, a
  pressed control.
- `--ground-3` — the deepest sunk level: table header row, inline code.
- `--ink` — headings, lead text, body prose, anything on the accent. 17.26:1.
- `--ink-2` — genuinely secondary text: table cells under a heading row,
  captions, notes. 8.33:1.
- `--ink-3` — mono labels, eyebrows, metadata. 5.66:1 on `--ground` and 4.89:1
  on `--ground-3`, so it is legal on every surface and carries no exception.
- `--hair` — the 1px border, and therefore the entire elevation system. 1.44:1
  against the ground: visible as structure without reading as a frame. Under
  `forced-colors: active` it is repainted by the OS, so keep the border present
  rather than swapping it for a fill.
- `--ring` — the focus ring, `--ink` at 2px. `--ring-offset` is 4px of
  `--ground`, so the ring reads against the sheet whatever it rings.
- `--accent` — one fill, the reference's own colour converted from
  `lab()`. Never text, never a line.
- `--accent-ink` — what goes on the accent. Identical to `--ink`, and that is
  the point: the accent is light, so its ink is dark.

Radius: `--radius-sm` container corners, `--radius-md` controls,
`--radius-lg` a detached card, `--radius-pill` badges only, at `9999px`.

Type: `--font-display` and `--font-body` are the same stack, which is the
direction rather than an oversight. `--font-mono` is a role, not an accent.
`--text-h1` and `--text-h2` clamp between the phone and desktop measurements;
`--text-h3` is 22px and doubles as the lead and pull-quote size so no fourth
prose size exists; `--text-small` is every mono label. `--measure` is 60ch,
derived rather than measured, since the reference does not run prose long
enough to expose one. It was 66ch, which invited the paragraph-heavy pages this
direction says it is not for; 60ch is the more honest number for a surface
whose prose arrives in short blocks between tables.

`--track-display` is a single value against a fluid `--text-h1`, which in most
directions means the tracking is right at one end of the clamp and wrong at the
other. It survives here because −0.01em is small enough that the difference
between its effect at 40px and at 64px is under a quarter of a pixel per
character. Any tighter and this token would have to vary with the clamp.

Deliberately inert, and correct that way:

- `--shadow-1: none` — the refusal, kept in the vocabulary so a consumer can
  write `box-shadow: var(--shadow-1)` and get nothing, and so swapping in
  another direction's tokens leaves no dangling variable.
- `--track-body: normal` — the measured value. Body tracking is not a place
  this direction has an opinion, and setting one would be the opinion.
