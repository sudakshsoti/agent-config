# product-dark

Near-black ground, hairline rings for depth, no blur anywhere.

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

Do not use it for a long read. Ink at 18.7:1 on near-black is comfortable for
a screenful; twenty minutes of 21px body copy on this ground is not, and the
direction has no light counterpart to switch to — `editorial` exists for that.
Do not use it when the artifact will be printed: a near-black ground either
prints as a solid block of ink or the ground drops out and takes the hairlines
with it, and this direction ships no `@media print` translation. Do not use it
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
| Surface ladder | `#08090A` → `#101112` → `#121314` → `#161718`, plus `rgba(255,255,255,0.01)` and `rgba(255,255,255,0.02)` tints | three named grounds at `#08090A` / `#101112` / `#161718`; the tints are not a separate mechanism, they are how the ladder is built (see below), so `#121314` needs no token |
| Ink | `#F7F8F8` | `--ink: oklch(0.978 0.002 248)`, which renders `#F7F8F9` |
| Borders | 1px `rgba(255,255,255,0.05)` and 1px `rgba(255,255,255,0.08)` | `--hair: oklch(1 0 0 / 0.08)`; the 0.05 tier is derived with `color-mix()`, not declared twice |
| h1 | 64px / 64px, weight 510, tracking −0.022em | `--text-h1` tops out at 64px, `--leading-display: 1`, `--track-display: -0.022em`, Geist at 500 |
| Body | 16px / 24px, weight 400, tracking normal | `--text-base: 1rem`, `--leading-body: 1.5`, `--track-body: normal` |
| Button | 13px / 19.5px, radius `9999px` | `--text-small: 0.8125rem` on `--leading-body`, `--radius-pill: 9999px` |
| Radius ramp | 2 / 4 / 6 / 8 / 12 / 16 plus `9999px` | sampled at 4 / 8 / 12 / `9999px` |
| Elevation | `0 0 0 1px rgba(0,0,0,0.2)`, `0 0 0 2px rgba(0,0,0,0.1)`, inset `0 0 0 1px rgb(35,37,42)`; real blur only on overlays | `--shadow-1` stacks all three as one token; no blur token exists, because a studio artifact has no overlays |

Not measured, and therefore this direction's own choices: the accent, `--ink-2`
and `--ink-3`, the spacing ramp, `--measure`, and all three families. The
reference gives its display role to Inter; the font policy does not allow that,
so Geist takes it.

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
| `--ink` | 18.74 | 17.78 | 16.88 |
| `--ink-2` | 7.46 | 7.08 | 6.72 |
| `--ink-3` | 5.35 | 5.07 | 4.82 |
| `--accent` | 6.32 | 5.99 | 5.69 |

All three ink tiers clear AA for normal text on all three grounds, which is the
reason `--ink-3` sits at lightness 0.615 rather than the 0.56 that looked right
by eye and measured 3.85 on `--ground-3`.

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
resolves to exactly `#121314` — the reference's own next step. At 0.024 it
resolves to `#161718`, the step after that. So the measured tints are not
something layered on top of the ladder; they *are* the ladder, and a raised
surface is one tint up. The fill step between `--ground-2` and `--ground-3` is
1.05:1, which is the whole elevation signal.

That leaves the ring doing only edge work, and the numbers say it is enough. The
measured inset ring `rgb(35,37,42)` is `#232529`, at 1.17:1 against
`--ground-3`. `--hair` at 0.08 alpha over `--ground-2` composites to `#232425`,
at 1.22:1 against it. Nearly the same tone at nearly the same strength, so the
two tiers read as one system at different heights rather than two different
ideas about edges.

## Type roles

| Role | Family | Size | Weight | Line-height | Tracking |
|---|---|---|---|---|---|
| Masthead `h1` | Geist | `--text-h1`, 38px at 390 → 64px at 1440 | 500 | `--leading-display` (1) | `--track-display` (−0.022em) |
| Section `h2` | Geist | `--text-h2`, 28px at 390 → 42px at 1440 | 500 | `calc(var(--leading-display) + 0.1)` | −0.02em |
| Lead and hero sub | Inter | `--text-h3` (21px) | 400 | `--leading-body` (1.5) | −0.01em |
| Body | Inter | `--text-base` (16px) | 400 | `--leading-body` (1.5) | `--track-body` (normal) |
| Small: meta, caption, button | Inter | `--text-small` (13px) | 400, 500 on buttons | `--leading-body` (1.5) | normal |
| Eyebrow | JetBrains Mono | `--text-small` (13px) | 400, uppercase | `--leading-body` (1.5) | +0.08em |
| Badge | JetBrains Mono | `--text-small` (13px) | 400 | `--leading-body` (1.5) | +0.04em |
| Code | JetBrains Mono | `--text-small` (13px) | 400 | `--leading-body` (1.5) | normal |

Three families is one more than any measured reference uses, and it is only
tolerable because the mono is confined to code, eyebrows and badge labels —
the places where a developer-tool page genuinely means "this is a literal
value". If a real `h3` is needed it takes the `--text-h3` step in Geist at 500
with −0.014em, above the lead, not beside it.

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
2. Links in prose, at 6.32:1 on `--ground`.
3. The `:focus-visible` ring.

Never a heading, never a border, never a section background, never a second hue
for a "secondary" state — a ghost button on `--hair` is the secondary state.
`--accent-ink` is a tinted near-black rather than white because white on this
indigo measures 2.97:1 and fails AA; darkening the ink instead of lightening
the accent keeps the accent recognisable as one colour wherever it appears.

## Spacing rhythm

An 8px grid with one 4px half-step for the tight cases:

| Token | Value | Where |
|---|---|---|
| `--space-1` | 4px | Gap inside a control, badge padding. |
| `--space-2` | 8px | Label to value, icon to text. |
| `--space-3` | 12px | Nav item padding, tight list gaps. |
| `--space-4` | 16px | Paragraph spacing, code block padding at 390. |
| `--space-5` | 24px | Page gutter, panel padding, grid gap. |
| `--space-6` | 32px | Panel padding at 1440, heading to body. |
| `--space-7` | 48px | Section padding at 390, section head to content. |
| `--space-8` | 80px | Section padding at 1440. |

The rhythm is deliberately uneven: 4-8-12-16 for anything inside a component,
then a jump to 24-32 for the component itself, then 48-80 for the gaps between
sections. Even spacing everywhere is one of the named anti-patterns, and it is
the gap between sections, not a border, that tells the reader a new argument has
started. This direction ships no section dividers for that reason.

Prose is capped at `--measure: 60ch`, tighter than a reading document needs,
because at 16px on a dark ground a shorter line makes the return sweep easier
and keeps the page feeling like an interface.

## Signature move

**Elevation is a ring, not a blur.** A raised surface carries
`box-shadow: var(--shadow-1)` and no border: two outer alpha rings at 1px and
2px darken the seam, an inset hairline at `oklch(0.264 0.009 265)` draws the
top edge, and the blur radius on all three is zero. None of the seven measured
references elevates with blur; the agent default
`0 4px 6px rgba(0,0,0,0.1)` matches none of them.

The move is only legible if the flat tier stays flat. A bordered container and
a ringed surface in the same view is what makes the ring mean something.

## Avoid list

1. **Any `box-shadow` with a non-zero blur radius.** The whole ladder is alpha
   rings; one blurred shadow reads as a second, softer elevation system and the
   two cancel out. `0 4px 6px rgba(0,0,0,0.1)` in particular is the agent
   default and matches none of the seven measured references.
2. **Inter at display size.** Inter carries body and UI here and nothing above
   `--text-h3`. Inter at 72px in a hero is the loudest "an agent made this"
   signal there is, which is precisely why the display role went to Geist even
   though the reference gives it to Inter.
3. **Tracking looser than −0.01em on any heading.** The reference sits at
   −0.022em. Default tracking at 64px opens visible gaps between the capitals
   and the heading reads as a system font at a size nobody chose. Eyebrows and
   uppercase labels are not headings and take positive tracking.
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
8. **`--ink-3` for running body copy.** It clears AA at 4.82:1 on the lightest
   surface, so the checker will not catch it, but it is a label tier. Paragraphs
   in it make the whole page feel dimmed and push the reader to zoom.
9. **A fourth surface tone, or a raised panel inside a raised panel.** The
   grounds are three or four per cent apart. A fourth improvised tone is
   invisible as a distinction and visible as a smudge, and nesting elevation on
   this ground produces two rings 24px apart that read as a rendering bug.
10. **A hairline lighter than `--hair`.** The measured pair is 0.05 and 0.08
    alpha and the token spends its one hairline on 0.08, because 0.05 on this
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
  header row, badge fill. Measured `#161718`, which is `--ground-2` under the
  measured 0.024 white tint.
- `--ink` — body and headings. Measured `#F7F8F8`, rendered `#F7F8F9`.
- `--ink-2` — secondary prose, captions, table cell text under a heading row.
  Derived, not measured.
- `--ink-3` — labels, eyebrows, metadata. The floor for text. Derived.
- `--hair` — the one border colour, at the measured 0.08 alpha. The 0.05 tier
  is `color-mix(in oklch, var(--hair), transparent 40%)`, which composites to
  `#141516` on `--ground`.
- `--accent` — indigo, chosen not measured. Button fill, links, focus ring.
- `--accent-ink` — the ink that sits on `--accent`. A tinted near-black,
  6.14:1, because white on this indigo fails AA.
- `--radius-sm|md|lg|pill` — 4 / 8 / 12 / 9999px, sampled from the measured
  ramp. Pill matches the measured button exactly.
- `--font-display` — Geist, weight 500. Falls back to `ui-sans-serif` rather
  than Inter on purpose, so a failed webfont load cannot put Inter at 64px.
- `--font-body` — Inter, 400 and 500. Everything at reading size.
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
- `--leading-display` — 1, exactly the measured 64 on 64. `h2` derives 1.1 from
  it with `calc()`, because a 28px heading wrapping to three lines at 390 needs
  the extra and a second token would be a lie about the measurement.
- `--track-display` — −0.022em, measured.
- `--track-body` — `normal`, measured. Deliberately inert: the temptation on a
  dark ground is to tighten body copy too, and the reference does not.
- `--measure` — 60ch.
- `--space-1` … `--space-8` — 4 / 8 / 12 / 16 / 24 / 32 / 48 / 80px.
- `--shadow-1` — the measured elevation stack, three rings, blur zero on all
  three. Deliberately not a blur, and there is no second shadow token because
  this direction has exactly one raised tier.
