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
|Ground|`lab(100 0 0)`|`--ground: oklch(1 0 0)`, the same white|
|h1|64px / 64px, weight 400, tracking −0.01px|`--text-h1` clamps 40px → 64px, weight 400, `--track-display: -0.01em`|
|h2|48px / 50px|`--text-h2` clamps 32px → 48px, weight 400|
|Body|16px / 24px|`--text-base: 1rem`, `--leading-body: 1.5`|
|Card|transparent fill, 1px border, radius 8px, padding 40px 32px, no shadow|`--radius-lg: 0.5rem`, `padding: var(--space-6) var(--space-5)`, `--shadow-1: none`|
|CTA|radius 6px, padding 0 20px|`--radius-md: 0.375rem`, `padding: 0 var(--space-4)`, height from `min-height`|
|Radius scale|0.25 / 0.375 / 0.5 / 0.75 / 1 / 1.5rem|four tokens on four of those six steps|
|Accent|`lab(92.1406% -20.4979 84.7726)`|`--accent: oklch(0.92 0.2 114)`, the same colour converted|
|Families|one throughout|one throughout|

Two of those measurements are the direction's whole argument. The card has no
shadow, and the h1 tracking at 64px is −0.01px, which is arithmetically
nothing. The reference signals depth with a line and signals size with size.

## Ground and ink

The ground is a true white, `oklch(1 0 0)`, because that is the measured value
and because the instrument metaphor needs an unbiased surface: a measuring
sheet has no opinion. The usual argument against pure white, that maximum
contrast fatigues the eye on a long read, does not bind here, since this
direction is for scanning a comparison rather than reading an essay. The tint
that argument asks for lives in the ink instead.

Every neutral shares one hue, 255, at chroma 0.004 to 0.014: a cool grey
family, dark enough at the top of the ladder to read as black without being
`#000`. The accent is the only warm thing on the page, at hue 114. That is why
it reads as a signal rather than as decoration, and it is the reason not to
tint the greys toward it.

Measured against the white ground: `--ink` 17.5:1, `--ink-2` 7.3:1, `--ink-3`
5.0:1, all clear of WCAG 2.2 AA at any size. `--ink-3` drops to 4.2:1 on
`--ground-3`, which is the one combination the direction forbids.

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
|h3|`--font-body`|`--text-h3` (20px)|500|`--leading-display`|`--track-body`|
|Lead, thesis, pull quote|`--font-body`|`--text-h3` (20px)|400|`--leading-body`|`--track-body`|
|Body|`--font-body`|`--text-base` (16px)|400|`--leading-body`|`--track-body`|
|Button label|`--font-body`|`--text-base` (16px)|500|`--leading-body`|`--track-body`|
|Label, eyebrow, meta, table header|`--font-mono`|`--text-small` (13px)|500|`--leading-body`|`--track-body`|
|Code|`--font-mono`|`--text-small` (13px)|400|`--leading-body`|`--track-body`|

Display weight is 400 at 64px, matching the reference and the wider finding
that display weight across the measured set runs 300 to 510. Bold display is
not available in this direction; weight 500 is the heaviest thing on the page
and it is reserved for 20px headings, button labels and mono labels.

`--leading-display` is 1.05, one value covering a measured 1.0 at h1 and 1.042
at h2. It rounds up rather than down so the h1 still clears its own descenders
once it clamps to 40px on a phone.

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
|`--radius-pill`|1.5rem (24px)|small mono badges only|

The two unexposed steps, 0.75rem and 1rem, are on the reference's scale and
are available by hand for anything between a control and a card. Nothing
rounds to a value that is not one of the six.

`--radius-pill` is 1.5rem, not `9999px`, because 1.5rem is the top of the
measured scale. On a 28px badge the browser clamps it to half the height and
the result is a true capsule. On a 44px button it is a lozenge that is neither
one thing nor the other, so the pill is for badges and nothing else.

Zero is always available and is not a violation of the scale. The lattice, the
signature move below, has no radius at all, because two adjacent rounded
corners cannot share one line.

## Accent policy

One hue, `oklch(0.92 0.2 114)`, and it is a fill. It sits at 1.23:1 against
the white ground, so it cannot be text, it cannot be a hairline, and it cannot
be a focus ring. Ink goes on top of it at 14.2:1, which is why
`--accent-ink` is the same value as `--ink` rather than white.

Where it is allowed: the primary button, a small mono badge, and the text
selection highlight. Two accent fills on a screen is the working ceiling. A
third and it stops meaning "act here".

The focus ring is `--ink`, 2px with a `--space-1` offset. That is a direct
consequence of a high-lightness accent and not a compromise: a ring the reader
cannot see is worse than a ring in a different colour.

## Spacing rhythm

An 8px grid, with the two measured card values landing on it exactly.

|Token|Value|What it is for|
|---|---|---|
|`--space-1`|4px|focus-ring offset, inline code inset|
|`--space-2`|8px|heading to its own paragraph|
|`--space-3`|16px|page gutter on a phone, gaps in a row of controls|
|`--space-4`|24px|paragraph flow, table cell inset, CTA horizontal inset|
|`--space-5`|32px|card horizontal padding, page gutter from 768px up|
|`--space-6`|40px|card vertical padding, and section vertical padding on a phone|
|`--space-7`|64px|section vertical padding from 768px up, and the masthead's extra gap on a phone|
|`--space-8`|96px|the masthead's extra gap from 768px up|

The card's measured 40px vertical and 32px horizontal padding is
`var(--space-6) var(--space-5)` with nothing rounded. The CTA's measured
20px horizontal inset is the one value that is not a step on an 8px grid; it
rounds up to 24px, because keeping every inset on the scale is worth more than
the 4px. Vertical padding on a control is zero at every size: height comes
from `min-height: 44px`, which is how the reference gets a consistent control
height and is also the tap-target floor.

Sections are separated by 40px and a hairline on a phone, 64px and a hairline
from 768px up. That pair is the rhythm: air, then a line, then air. There is no
other divider, and the masthead is the one place the gap steps up a level.

## Signature move

**Cards share their borders.** Set them edge to edge in a grid with no gap and
the two 1px lines between them collapse into one, so the grid draws as a
lattice rather than as a row of objects hovering over a page. Build it by
putting the top and left hairline on the grid container and the right and
bottom hairline on each cell: no doubling anywhere, one continuous rule, and
it reflows to a single column on a phone without a line going missing.

The whole point is that depth is only ever a question of whether a line is
there. A shadow would say the cards are above the page; a shared border says
they are ruled onto it.

## Avoid list

1. **Any `box-shadow` at all, including an inset ring.** Border-only elevation
   is the entire direction, `--shadow-1` is `none`, and the reference has no
   shadow anywhere. A ring like `0 0 0 1px` is Linear's answer, not this one.
2. **A second accent hue.** The lime means "act here". A blue beside it and
   neither one means anything after its second appearance.
3. **The accent on text, a hairline, or a focus ring.** At `oklch(0.92 ...)`
   it is 1.23:1 on the white ground. It is a fill with ink on top, or it is
   invisible.
4. **Uneven card padding.** Every panel insets 40px by 32px. The lattice only
   reads as one ruled surface if every cell in it is the same box.
5. **A filled card.** A grey fill plus a border states depth twice and the
   fill wins, which takes the job away from the hairline. Fills belong to the
   sunk levels, `--ground-2` and `--ground-3`.
6. **A non-zero radius off the six-step scale.** A 10px or 20px corner is
   nobody's measurement and reads as a second component library arriving.
7. **`--radius-pill` on anything taller than a badge.** It is 1.5rem, not
   `9999px`, so on a 44px control it produces a lozenge rather than a capsule
   and the intent is lost.
8. **Display tracking past −0.01em.** The reference measures effectively none.
   −0.022em is Linear's signature and −0.03em is Headspace's; borrowing either
   makes this page read as the wrong direction.
9. **A second display family.** One grotesque throughout, mono for labels and
   literals. Two families is `editorial`'s move, and the whole measured set
   uses one or two, never three.
10. **`--ink-3` on `--ground-3`.** 4.2:1, under AA for small text. Small type
    on the deepest ground uses `--ink-2` at 6.2:1.

## Token map

Colour, all in OKLCH at hue 255 except the accent:

- `--ground` — the page. A true white, the measured value.
- `--ground-2` — the first sunk level: code blocks, the footer strip, a
  pressed control.
- `--ground-3` — the deepest sunk level: table header row, inline code.
- `--ink` — headings, lead text, anything on the accent. 17.5:1 on the ground.
- `--ink-2` — body prose, table cells, secondary text. 7.3:1.
- `--ink-3` — mono labels, eyebrows, metadata, captions. 5.0:1 on `--ground`
  and 4.6:1 on `--ground-2`, but only 4.2:1 on `--ground-3`, where `--ink-2`
  takes over.
- `--hair` — the 1px border, and therefore the entire elevation system. 1.46:1
  against the ground: visible as structure without reading as a frame.
- `--accent` — one fill, the reference's own colour converted from
  `lab()`. Never text, never a line.
- `--accent-ink` — what goes on the accent. Identical to `--ink`, and that is
  the point: the accent is light, so its ink is dark.

Radius: `--radius-sm` container corners, `--radius-md` controls,
`--radius-lg` a detached card, `--radius-pill` badges only.

Type: `--font-display` and `--font-body` are the same stack, which is the
direction rather than an oversight. `--font-mono` is a role, not an accent.
`--text-h1` and `--text-h2` clamp between the phone and desktop measurements;
`--text-h3` doubles as the lead and pull-quote size so no fourth prose size
exists; `--text-small` is every mono label. `--measure` is 66ch, derived
rather than measured, since the reference does not run prose long enough to
expose one.

Deliberately inert, and correct that way:

- `--shadow-1: none` — the refusal, kept in the vocabulary so a consumer can
  write `box-shadow: var(--shadow-1)` and get nothing, and so swapping in
  another direction's tokens leaves no dangling variable.
- `--track-body: normal` — the measured value. Body tracking is not a place
  this direction has an opinion, and setting one would be the opinion.
