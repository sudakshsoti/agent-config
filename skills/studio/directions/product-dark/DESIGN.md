# product-dark

Near-black ground, a sticky left rail, hairline rings for depth, no blur.

## Thesis

A near-black ground where depth is one alpha tint and a one-pixel ring, never a
shadow. The interest comes from three grounds that sit three or four per cent
apart and from edges hard enough to read at 1px. Everything else stays out of
the way: one desaturated accent, tracking pulled tight on display type, body
copy at the measured 16 on 24. It should read like the product's own UI escaped
onto a marketing page, which is the point — the reader of a developer tool
already knows what a dark interface feels like, and a page that feels different
from the product is promising something the product does not deliver.

## When to use, when not

Use it for developer tools, dashboards-as-marketing, changelogs, API and
infrastructure pages, and anything whose real product UI is already dark.

Do not use it for a long read. Ink at 16.7:1 on near-black is comfortable for
a screenful; twenty minutes of 21px body copy on this ground is not, and the
direction has no light counterpart to switch to — `editorial` exists for that.
It does now ship a print translation, so a `document` in this direction is
legal: `@media print` swaps the ground to paper, the ink to near-black and
every alpha ring to a hairline. Do not use it
for consumer, wellbeing or onboarding work, where `calm` is the right answer,
and do not use it as a container for photography or client artwork, because a
near-black ground makes every image look like it has a vignette.

## Reference values

Measured against Linear (linear.app), not copied from it. The left column is
what was measured on the reference; the right column is what this direction
does with it. Where they differ, the difference is deliberate.

| What | Measured on Linear | This direction |
|---|---|---|
| Ground | `#08090A` | `--ground: oklch(0.139 0.003 248)`, which is `#08090A` exactly |
| Surface ladder | `#08090A` → `#101112` → `#121314` → `#161718`, plus `rgba(255,255,255,0.01)` and `rgba(255,255,255,0.02)` tints | three named grounds at `#08090A` / `#101112` / `#1B1C1D`; the tints are not a separate mechanism, they are how the ladder is built (see below), so `#121314` needs no token, and the top of the ladder goes one tint past the measured `#161718` so the fill step stays visible |
| Ink | `#F7F8F8` | `--ink: oklch(0.940 0.002 248)`, `#EAEBEC`, deliberately dimmer — see below |
| Borders | 1px `rgba(255,255,255,0.05)` and 1px `rgba(255,255,255,0.08)` | `--hair: oklch(1 0 0 / 0.08)`; the 0.05 tier is derived with `color-mix()`, not declared twice |
| h1 | 64px / 64px, weight 510, tracking −0.022em | `--text-h1` tops out at 64px, `--leading-display: 1.05`, `--track-display: -0.022em` scaled by optical size, Geist at 500 |
| Body | 16px / 24px, weight 400, tracking normal | `--text-base: 1rem`, `--leading-body: 1.5`, `--track-body: normal` |
| Button | 13px / 19.5px, radius `9999px` | `--text-small: 0.8125rem` on `--leading-body`, `--radius-pill: 9999px` |
| Radius ramp | 2 / 4 / 6 / 8 / 12 / 16 plus `9999px` | sampled at 4 / 8 / 12 / `9999px` |
| Elevation | `0 0 0 1px rgba(0,0,0,0.2)`, `0 0 0 2px rgba(0,0,0,0.1)`, inset `0 0 0 1px rgb(35,37,42)`; real blur only on overlays | `--shadow-1` stacks all three as one token; no blur token exists, because a studio artifact has no overlays |

Not measured, and therefore this direction's own choices: the accent, `--ink-2`
and `--ink-3`, the spacing ramp, `--measure`, the rail, and both families.

**Two families, not three.** An earlier version gave display to Geist and body
to Inter. Both are neo-grotesques with near-identical metrics, so the switch
was invisible as hierarchy and visible only as an inconsistency in the `g` and
the `a` — a constraint spent for nothing, and one more family than any measured
reference uses. Geist now carries display and body, and JetBrains Mono carries
literals. The reference gives its display role to Inter; the font policy does
not allow that, and dropping Inter entirely removes the failure mode rather
than guarding against it.

## Ground and ink

Every neutral sits on hue 248 — the hue the measured ground already carries at
`oklch(0.139 0.003 248)`. Holding one hue across the ladder is what makes the
page read as a single cool object rather than four greys that happen to be near
each other. It costs one bit: `--ink` renders `#F7F8F9` against the measured
`#F7F8F8`, an invisible difference on the blue channel, and worth it for a ladder
that tints consistently.

Chroma stays between 0.002 and 0.012, rising as lightness falls off the ink so
the dimmer text tiers do not go flat grey. Contrast, WCAG 2.2, against every
ground the token can land on:

| Ink | On `--ground` | On `--ground-2` | On `--ground-3` |
|---|---|---|---|
| `--ink` | 16.72 | 15.85 | 14.34 |
| `--ink-2` | 8.50 | 8.06 | 7.29 |
| `--ink-3` | 6.05 | 5.74 | 5.19 |
| `--accent` | 6.29 | 5.96 | 5.39 |

All three ink tiers clear AA for normal text on all three grounds with real
headroom, not on the line.

**`--ink` is deliberately not the measured `#F7F8F8`.** At lightness 0.978 it
measured 18.74:1, and near-white on near-black at that ratio haloes: the
glyph edges bloom into the ground, worst for astigmatic readers, and the effect
is a large part of why a dark page tires faster than a light one. `--ink` sits
at 0.940 and 16.72:1, still far above AA and far enough under the ceiling to
stop blooming. The measurement is reproduced everywhere it does not hurt to
reproduce it; this is the one place it does.

## Surface ladder

Two tiers, and elevation is signalled by an alpha tint step plus a ring where a
border would otherwise be. Never by blur, and never by a drop.

**Flat** is a container fenced *on* the ground: `background: var(--ground-2)`,
`border: 1px solid var(--hair)`, `box-shadow: none`. Tables, code blocks and
notes are flat. They are the same object as the page, just fenced off.

**Raised** is a surface one step *above* it: `background: var(--ground-3)`,
`box-shadow: var(--shadow-1)`, and **no border at all**. The ring is the border.
Two outer alpha rings darken the seam where the surface meets the ground, and
the inset hairline draws the surface's own top edge.

`--ground-3` carries every "nearer" state, because they are all the same idea: a
raised surface, a hovered row, a pressed control, a table's header row, the fill
behind a badge. A hover state does not also get a ring — that would be two
signals for one event.

The tint and the ladder are the same mechanism, which is the finding this
direction is built on. `rgba(255,255,255,0.01)` composited over `#101112`
resolves to exactly `#121314` — the reference's own next step, and further
tints walk it up from there. The measured tints are not something layered on
top of the ladder; they *are* the ladder, and a raised surface is one tint up.

**`--ground-3` sits one step past the measured `#161718`, at `#1B1C1D`.** The
measured step gave a fill difference of 1.05:1 against `--ground-2`, and this
direction already rejects a 0.05-alpha hairline on the grounds that it
"disappears on a phone held at arm's length in daylight". A 1.05:1 fill
disappears in exactly the same conditions, and the argument cannot apply to the
line and not to the fill. At `oklch(0.225 0.003 248)` the elevation signal is
1.11:1, which is the smallest step in the direction that survives daylight.

`--ink-3` moved up with it, from 0.615 to 0.645, so the label tier still clears
AA on the new deepest ground rather than sliding to 4.61:1.

That leaves the ring doing only edge work, and the numbers say it is enough.
The measured inset ring `rgb(35,37,42)` is `#232529`, at 1.11:1 against the new
`--ground-3`. The token draws it as `oklch(1 0 0 / 0.04)`, which composites
over `--ground-3` to `#242526` and 1.11:1 — the measurement, reproduced by an
alpha rather than baked as an opaque colour. That matters: the old opaque value
was correct on `--ground-3` and wrong anywhere else, so the token encoded its
own placement. An alpha is correct at every level.

`--hair` at 0.08 alpha over `--ground-2` composites to `#232425`, at 1.22:1
against it. Nearly the same tone at nearly the same strength as the inset ring,
so the two tiers read as one system at different heights rather than two
different ideas about edges.

## Type roles

| Role | Family | Size | Weight | Line-height | Tracking |
|---|---|---|---|---|---|
| Masthead `h1` | Geist | `--text-h1`, 38px at 390 → 64px at 1440 | 500 | `--leading-display` (1.05) | see optical sizing below |
| Section `h2` | Geist | `--text-h2`, 28px at 390 → 42px at 1440 | 500 | `calc(var(--leading-display) + 0.05)` | −0.018em |
| Real `h3` | Geist | `--text-h3` (21px) | 500 | `--leading-h3` (1.25) | −0.014em |
| Lead and hero sub | Geist | `--text-h3` (21px) | 400 | `--leading-body` (1.5) | −0.01em |
| Body | Geist | `--text-base` (16px) | 400 | `--leading-body` (1.5) | `--track-body` (normal) |
| Small: meta, caption, button | Geist | `--text-small` (13px) | 400, 500 on buttons | `--leading-body` (1.5) | normal |
| Eyebrow | JetBrains Mono | `--text-small` (13px) | 400, uppercase | `--leading-body` (1.5) | +0.08em |
| Badge | JetBrains Mono | `--text-small` (13px) | 400 | `--leading-body` (1.5) | +0.04em |
| Code | JetBrains Mono | `--text-small` (13px) | 400 | `--leading-body` (1.5) | normal |

Two families, which is what every measured reference uses. The mono is confined
to code, eyebrows and badge labels — the places where a developer-tool page
genuinely means "this is a literal value". A real `h3` takes the `--text-h3`
step in Geist at 500, above the lead rather than beside it: same size, and the
weight and the leading are what separate them.

**`--leading-display` is 1.05, not the measured 1.** 64 on 64 was measured on a
headline that fit one line. At 390 the h1 clamps to 38px and wraps to two or
three, and at exactly 1.0 the descenders of one line meet the cap-height of the
next. 1.05 costs nothing at 64px and stops the collision at 38px. h2 adds a
further 0.05 by `calc()` for the same reason at its own floor.

**Display tracking scales with optical size.** `--track-display` is the
measured −0.022em, which was measured at 64px, and −0.022em at 38px is visibly
too tight — the counters close and the heading reads as compressed rather than
as set. `--text-h1` is fluid, so its tracking is too:

```css
h1 {
  font-size: var(--text-h1);
  letter-spacing: clamp(-0.022em, -0.036em + 0.022rem, -0.012em);
}
```

Tighter as the size grows, looser as it shrinks, hitting the measured −0.022em
only where the measurement was taken. A single tracking value against a fluid
size is right at one end of the clamp and wrong at the other.

The eyebrow is the one place tracking goes positive. Uppercase at 13px needs it;
an eyebrow is a label, not a heading, so the avoid-list rule on heading tracking
does not reach it.

## Radius scale

The reference ramps 2 / 4 / 6 / 8 / 12 / 16 plus `9999px`. Four tokens sample it:

- `--radius-sm: 4px` — inline code, small fills, anything under about 2rem tall.
- `--radius-md: 8px` — the working radius. Panels, table shells, code blocks.
- `--radius-lg: 12px` — the widest surfaces only: a figure, a full-width note.
- `--radius-pill: 9999px` — buttons and badges, matching the measured button.

2px is out because on a near-black ground a 2px corner is indistinguishable
from a rendering artefact, so it spends a token on nothing. 6px is out because
it sits close enough to 8px that no reader could tell them apart, and a scale
whose steps are invisible is not a scale. 16px is out because it is softer than
anything the reference puts on a bordered surface, and it starts to read as
`calm`.

Radius is never uniform across a view. If four things in one artifact all want
8px, three of them are the wrong size for it.

## Accent policy

One hue: `--accent: oklch(0.660 0.120 272)`, a desaturated indigo, `#798DDC`.
The reference's own accent is not in the measured set, so this is a choice, not
a reproduction. Chroma is held at 0.120 deliberately — a near-black ground with
one high-chroma acid hue is the second of the three AI defaults named in
`references/anti-patterns.md`, and 0.18-plus chroma on this ground is exactly
that look.

It is spent on three things and nothing else:

1. The primary button fill, with `--accent-ink` on it at 6.14:1.
2. Links in prose, at 6.29:1 on `--ground`.
3. The `:focus-visible` ring, which is `--ring` at 2px with `--ring-offset`.

**Link states come from the accent, not from a second colour.** Hover is
`color-mix(in oklch, var(--accent), var(--ink) 25%)`, which lifts it toward the
page's own white without introducing a hue. Active is
`color-mix(in oklch, var(--accent), var(--ground) 20%)`, a step back into the
ground. This is the same derivation the hairline uses, and it is stated so the
alternative — inventing a second indigo — never comes up.

Never a heading, never a border, never a section background, never a second hue
for a "secondary" state — a ghost button on `--hair` is the secondary state.
`--accent-ink` is a tinted near-black rather than white because white on this
indigo measures 2.97:1 and fails AA; darkening the ink instead of lightening
the accent keeps the accent recognisable as one colour wherever it appears.

## Spacing rhythm

An 8px grid with one 4px half-step for the tight cases:

| Token | Value | Where |
|---|---|---|
| `--space-1` | 4px | Gap inside a control, badge padding, `--ring-offset`. |
| `--space-2` | 8px | Label to value, icon to text. |
| `--space-3` | 12px | Nav item padding, tight list gaps. |
| `--space-4` | 16px | Paragraph spacing, code block padding at 390. |
| `--space-5` | 24px | Page gutter, panel padding, grid gap, the rail's sticky top. |
| `--space-6` | 40px | Panel padding at 1440, heading to body. |
| `--space-7` | 64px | Section padding at 390, section head to content. |
| `--space-8` | 96px | Section padding at 1440. |

The rhythm is deliberately uneven: 4-8-12-16 for anything inside a component,
then a jump to 24-40 for the component itself, then 64-96 for the gaps between
sections. Even spacing everywhere is one of the named anti-patterns, and it is
the gap between sections, not a border, that tells the reader a new argument has
started. This direction ships no section dividers for that reason.

The top of the ramp used to be 32 / 48 / 80, which gave a page made almost
entirely of sections two usable section values and four steps under 16px. The
ramp now widens where sections separate and keeps the fine grain only where
things touch.

Prose is capped at `--measure: 60ch`, tighter than a reading document needs,
because at 16px on a dark ground a shorter line makes the return sweep easier
and keeps the page feeling like an interface.

## Signature move

**A sticky left rail, and the measure hung off it.**

Every other direction has an idea about the page: `editorial` has its margin
rail, `instrument` has its lattice, `calm` has its colour field. This one used
to have only an idea about components, which meant a page could follow it
exactly and still be a narrow column floating in the middle of 1440px of empty
ground.

From 900px up, a `--rail` column of 13rem is fixed to the left edge and holds
the section links. The content column starts immediately to its right and stays
at `--measure`, 60ch, rather than centring in the space that is left. That
gives the page one hard left edge and all its slack on the right, which is what
a dashboard looks like and is the opposite of a centred container.

The rail is chrome, not a surface. It takes no fill, no ring and no border on
its inner edge: it is separated from the content by space alone. Rail links sit
at `--ink-3`, the current one at `--ink` with a 2px `--hair` left border, so
the current position is marked by position and weight rather than by colour
alone. `position: sticky` with `top: var(--space-5)`, no JavaScript.

Below 900px the rail becomes a horizontal strip at the top of the page, still
sticky, still marking the current section, scrolling horizontally if the links
overflow. The content takes the full gutter. Nothing is hidden behind a menu.

## Component signature

**Elevation is a ring, not a blur.** A raised surface carries
`box-shadow: var(--shadow-1)` and no border: two outer alpha rings at 1px and
2px darken the seam, an inset hairline at `oklch(1 0 0 / 0.04)` draws the top
edge, and the blur radius on all three is zero. None of the seven measured
references elevates with blur; the agent default
`0 4px 6px rgba(0,0,0,0.1)` matches none of them.

The move is only legible if the flat tier stays flat. A bordered container and
a ringed surface in the same view is what makes the ring mean something.

## Avoid list

1. **Any `box-shadow` with a non-zero blur radius.** The whole ladder is alpha
   rings; one blurred shadow reads as a second, softer elevation system and the
   two cancel out. `0 4px 6px rgba(0,0,0,0.1)` in particular is the agent
   default and matches none of the seven measured references.
2. **A second sans family.** Geist carries display, body and UI. Adding Inter
   beside it — the arrangement this direction used to ship — buys nothing: two
   neo-grotesques with near-identical metrics read as one family set
   inconsistently, not as two voices. Inter at display size specifically is the
   loudest "an agent made this" signal there is, and dropping Inter from the
   stack removes the failure mode instead of guarding it.
3. **A single tracking value on a fluid heading.** −0.022em is the measured
   value *at 64px*, and applying it unchanged at the 38px floor closes the
   counters. Display tracking clamps with the size. Looser than −0.012em at any
   size is also out: default tracking at 64px opens visible gaps between the
   capitals and the heading reads as a system font at a size nobody chose.
   Eyebrows and uppercase labels are not headings and take positive tracking.
4. **Pure `#000` as the ground.** The measured ground is `#08090A`, which
   carries the hue 248 that the whole neutral ladder tints toward; `#000` has
   no hue to tint from. On OLED it also clips to the panel's own black, so the
   page appears to float free of the screen edge.
5. **A bright acid accent — green, vermilion, cyan — on the near-black.** That
   pairing is AI default number two in `references/anti-patterns.md`. It is the
   single most recognisable machine-made dark page, and chroma above roughly
   0.15 on this ground lands on it however tasteful the hue.
6. **A border and a ring shadow on the same element.** The ring's inset
   hairline already is the edge. Doubling gives a 2px muddy rim and destroys
   the only thing separating the flat tier from the raised one.
7. **`backdrop-filter: blur()` on a nav bar, panel or overlay.** This token set
   contains no blur at all. A frosted strip is the one move that turns a
   considered dark page into 2024 glassmorphism, and the reference reserves real
   blur for overlays, which a self-contained artifact does not have.
8. **`--ink-3` for running body copy.** It clears AA at 5.19:1 on the lightest
   surface, so the checker will not catch it, but it is a label tier. Paragraphs
   in it make the whole page feel dimmed and push the reader to zoom.
9. **A fourth surface tone, or a raised panel inside a raised panel.** A
   fourth improvised tone is invisible as a distinction and visible as a
   smudge, and nesting elevation on this ground produces two rings 24px apart
   that read as a rendering bug.
10. **A centred content column.** The rail is the direction's page-level idea
    and it only works if the measure hangs off it: content starts at the rail's
    right edge and all the slack lives on the right. Centring the column in the
    space that is left throws the asymmetry away and produces the thing the
    rail exists to prevent — a narrow column floating in the middle of an empty
    dark page.

A hairline lighter than `--hair` is also out. The measured pair is 0.05 and
0.08 alpha and the token spends its one hairline on 0.08, because 0.05 on this
ground disappears on a phone held at arm's length in daylight. Derive the
softer tier with `color-mix(in oklch, var(--hair), transparent 40%)` rather
than inventing a third value.

## Token map

- `--ground` — the page, measured `#08090A`. It doubles as the fill for a chip
  sitting on a nearer surface — an inline code span inside a raised panel, a
  badge inside a hovered row — so a chip is a well cut down to the page rather
  than a fourth tone invented to sit on top of a third.
- `--ground-2` — every flat container: tables, code blocks, notes, and the
  resting fill of a ghost control. Measured `#101112`.
- `--ground-3` — one step nearer: the raised tier, hover, pressed, a table's
  header row, badge fill. `#1B1C1D`, one step past the measured `#161718` so
  the fill difference survives daylight.
- `--ink` — body and headings. `#EAEBEC`, deliberately dimmer than the measured
  `#F7F8F8` to stop near-white haloing on near-black.
- `--ink-2` — secondary prose, captions, table cell text under a heading row.
  Derived, not measured.
- `--ink-3` — labels, eyebrows, metadata. The floor for text. Derived.
- `--ring` / `--ring-offset` — the `:focus-visible` ring, `--accent` at 2px
  with 4px of clearance.
- `--hair` — the one border colour, at the measured 0.08 alpha. The 0.05 tier
  is `color-mix(in oklch, var(--hair), transparent 40%)`, which composites to
  `#141516` on `--ground`.
- `--accent` — indigo, chosen not measured. Button fill, links, focus ring.
- `--accent-ink` — the ink that sits on `--accent`. A tinted near-black,
  6.14:1, because white on this indigo fails AA.
- `--radius-sm|md|lg|pill` — 4 / 8 / 12 / 9999px, sampled from the measured
  ramp. Pill matches the measured button exactly.
- `--font-display` — Geist, weight 500. Falls back to `ui-sans-serif`, never
  to a named second sans.
- `--font-body` — Geist, 400 and 500. The same stack as `--font-display`, which
  is the direction rather than an oversight.
- `--rail` — 13rem, the sticky left nav column. The direction's page-level
  idea, and the reason the content column is not centred.
- `--font-mono` — JetBrains Mono. Code, eyebrows, badge labels. Stands in for a
  licensed face so the artifact stays shareable.
- `--text-base` — 16px, the measured body size.
- `--text-h1` — `clamp(2.375rem, 1.75rem + 2.6vw, 4rem)`. Hits the measured
  64px at 1385px and holds it through 1440; 38px at 390.
- `--text-h2` — `clamp(1.75rem, 1.35rem + 1.55vw, 2.625rem)`. 28px at 390,
  42px at 1440.
- `--text-h3` — 21px. Lead, hero sub, and a real `h3` if one is needed.
- `--text-small` — 13px, the measured button size. Also meta, caption, badge,
  eyebrow, code.
- `--leading-body` — 1.5, exactly the measured 16 on 24.
- `--leading-display` — 1.05. The measured value is 1, taken on a headline that
  fit one line; at the 38px floor the h1 wraps and 1.0 puts descenders into the
  next line's caps. `h2` derives a further 0.05 with `calc()`.
- `--leading-h3` — 1.25, for a real `h3` and for the lead.
- `--track-display` — −0.022em, measured at 64px, and clamped down toward
  −0.012em as the fluid `--text-h1` shrinks.
- `--track-body` — `normal`, measured. Deliberately inert: the temptation on a
  dark ground is to tighten body copy too, and the reference does not.
- `--measure` — 60ch.
- `--space-1` … `--space-8` — 4 / 8 / 12 / 16 / 24 / 40 / 64 / 96px.
- `--shadow-1` — the measured elevation stack, three rings, blur zero on all
  three. The inset is `oklch(1 0 0 / 0.04)` rather than an opaque grey, so it
  composites correctly on any ground instead of only on `--ground-3`.
  Deliberately not a blur, and there is no second shadow token because this
  direction has exactly one raised tier.

`color-scheme: dark` is declared on `:root`. Without it a browser defaulting to
light paints native scrollbars, form controls and `::selection` light against
this ground, and the one part of the page the direction does not control ends
up being the part that gives it away.

`font-variant-numeric: tabular-nums` on tables and stat blocks.

## Print

A `document` in this direction inverts rather than disclaiming print. `@media
print` sets the ground to `#fff` and the ink to `--ground`, replaces every alpha
ring and hairline with a 1px `#ccc` border, drops `--shadow-1` to `none`, and
collapses the rail into a static list at the top. A near-black ground either
prints as a solid block of ink or drops out and takes the hairlines with it, so
the translation is not optional.
