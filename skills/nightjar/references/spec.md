# NIGHTJAR — the system

§2–§10 of the house style. Rules and ratios bind; values marked `ref` are one
valid answer, not the only one. The rejection list (§11) and the self-check
(§12) are in `self-check.md`.

---

## 2. Surfaces

A **three-step neutral ramp**, equal RGB channels, no blue or warm cast.

| Step | Role | `ref` |
|---|---|---|
| `bg` | Page / canvas. The darkest thing. | `#0f0f0f` |
| `sunk` | Sidebars, rails, wells — recedes *behind* the page | `#070707` |
| `raised` | Cards, rows, panels, inputs — sits *above* the page | `#171717` |

Rules:

- **Never pure `#000000`.** It reads as absence, not as a surface, and it makes
  every step above it look like a mistake.
- **Never a tinted black.** Channels stay within 2 points of each other. Warmth
  and coolness are things the accent does, not the background.
- **Exactly three steps in one view.** A fourth step is a sign the hierarchy is
  wrong. Nesting a `raised` inside a `raised` is not allowed — regroup instead.
- **Steps are ~8 points apart** in 8-bit terms. Enough to see, not enough to
  announce itself.
- The step ratio matters more than the values: `sunk` : `bg` : `raised` should
  read as roughly `-0.5x : 1x : +1.5x` perceptual lightness.

### Containment

A container becomes visible **by fill step**. In order of preference:

1. Fill step (`raised` on `bg`) — the default. Use this unless there's a reason.
2. Hairline border at ~`#242424` `ref` — only when a fill step is unavailable:
   a panel already sitting on `raised`, or a panel grid where every panel would
   take the same step. The dashboard grid is that case, not an exception to it.
3. Nothing at all — grouped by whitespace. Legitimate and often better.

Never: drop shadows, glows, outer rings, gradient fills, glass blur, or a
coloured left border. If a card needs a shadow to be visible, the fill step is
wrong.

### State variations

*Interactive artifacts only.* A state shifts a surface within its own step; it
never introduces a new one. A hovered `raised` row is still `raised`, and the
three-step count is unaffected.

- Hover: **+4 points** on the current step. `raised` → ~`#1b1b1b` `ref`.
- Pressed: **−2 points** on the current step.
- Selected: `accent` at ~8% alpha, or a 2px accent edge marker. Not both.
- Disabled: see §8. It is a colour step, never an opacity.

**Precedence, highest wins:** disabled → error → loading → pressed → selected →
hover. Focus-visible sits on top of whichever won; it is a ring, not a fill.

### Overlays

*Interactive artifacts only.* Shadows are unavailable, so an overlay separates
by scrim and step: scrim at `bg` ~70% alpha over the page, panel on `raised`
with a hairline.

Layering is **contextual, not a global order.** An overlay renders above the
context that opened it, so a dropdown opened inside a modal sits above that
modal. Never author a fixed z-index table.

---

## 3. Accent

**One hue. Selection and focus only.**

```
accent        oklch(0.6675 0.1142 244.33 / 89.31%)   ≈ #519bd5 at 89% alpha
accent-solid  oklch(0.6675 0.1142 244.33)            ≈ #519bd5
accent-light  oklch(0.47   0.1142 244.33)            ≈ #066096   (light mode only)
```

Contrast, measured. Method: WCAG 2.1 relative luminance, with any alpha
composited over the named backdrop *before* measuring.

| Pair | Ratio | Verdict |
|---|---|---|
| `accent` composited over `bg` → `#4a8cc0` | **5.30:1** | AA normal text ✓ |
| `accent-solid` on `bg` | **6.39:1** | AA normal text ✓ |
| `accent-solid` on `#faf9f7` | 2.85:1 | ✗ — use `accent-light` |
| `accent-light` on `#faf9f7` | **6.39:1** | AA normal text ✓ |

None of these clear AAA (7:1). Do not set body text in the accent at any size.

Permitted uses — this is the entire list:

- Selected row, tab, or nav item (as a fill at low alpha, or a 2px edge marker)
- Focus ring (2px, offset 2px), on `:focus-visible` only — never on a mouse
  click
- Active toggle / checked control
- The single primary line in a multi-series chart
- Text link on hover

The focus ring clears **3:1 against the surface it is drawn on**. It does not
also have to clear 3:1 against the control it surrounds — at 2px offset the ring
is not adjacent to the fill, and for an accent-filled control that would be
unsatisfiable.

Link hover is the one permitted use that is neither selection nor focus. It is a
named exception, not a precedent; the self-check counts it as compliant.

Forbidden: headings, body copy, buttons that aren't the focused element, icon
tinting, section dividers, decorative fills, "brand moments."

**Everything else is neutral.** If you are reaching for a second accent, you
want a status colour or a chart series instead.

---

## 4. Status and data colour

Colour that encodes state is not decoration and is exempt from the accent rule.
A status hue appears **only inside a pill or a glyph**, never as body text.

| State | Fill `ref` | Glyph/label `ref` |
|---|---|---|
| positive / delivered / done | `#172f25` | `#3fdc90` |
| negative / error / bounced | `#301418` | `#e8695f` |
| warning / pending | `#2e2413` | `#e0a92e` |
| info / in progress | `#141f2e` | `#6aa9e0` |
| special / clicked / custom | `#191033` | `#b7a1f6` |

Rules:

- **Dark tinted fill, bright label.** The fill is a ~10–14% mix of the hue into
  `bg`; the label is the hue at full chroma.
- Pills are small, low-radius (~4px `ref`), and always right-aligned in their
  own column when in a table.
- **Five states maximum.** A sixth means the state model needs collapsing.
- Sign is carried by *both* the glyph (`+`/`−`, arrow) and the hue. Never hue
  alone — that fails for colourblind readers and in print.
- **Every pill carries a text label or a glyph.** The same rule, applied to
  state: hue is never the only carrier.

### Chart series

Near-equal-lightness, low-chroma, five maximum. **White is series one**; colour
starts at series two. A ramp built so overlapping lines never fight:

```
ref: #f4f5f6  #6aa9e0  #b7a1f6  #e0c96a  #3fbfa8
```

Chart chrome: axis lines and gridlines at `hairline`, gridlines on **one axis
only**. Labels, ticks, and legends take the §5 text ramp — never the surface
ramp, which is invisible on the canvas it came from.

Over five series is two charts. Never an "other" bucket: aggregating a tail
falsifies rates, percentages, and anything non-additive.

No area fills under lines unless there is exactly one series. No 3D, no donut
charts, no gradient fills, no drop shadows on data.

---

## 5. Type

**Two families, strict division of labour.** Do not name Inter, Roboto, Arial,
or Helvetica — the first two are the default-AI signal this style exists to
avoid.

**Prose family** — all language: headings, body, UI labels, buttons.
Characteristics to select for: humanist or neo-grotesque sans; low contrast
between thick and thin; open apertures; a single-storey or lightly-curved `a`
tolerated; slightly narrow lowercase; tabular figures available as a feature.
Avoid geometric sans with perfect-circle bowls (too cold, dates instantly) and
anything with a decorative italic.

**Machine family** — monospace, for exactly: code, log output, IDs, hashes,
timestamps, filenames, key badges, and column headers in dense tables.
Characteristics: modest x-height, unambiguous `0`/`O` and `1`/`l`/`I`, no
programming ligatures. Ligatures are for editors, not for artifacts.

Rules:

- **The division never blurs.** No monospace in a heading for "technical
  flavour." No sans in a log line. Mono is a signal that content is machine-
  generated; using it decoratively destroys that signal.
- **Weight carries hierarchy before size does.** Two weights (regular ~400 and
  medium ~500/600) do most of the work. A bold-black weight is rarely needed.
- **One display size, one body size, and as little between as possible.** The
  restraint comes from the gap. A scale with seven active sizes reads as a
  template.
- Ratios, not px: display ≈ 3.5–4× body; section heading ≈ 1.6× body; label =
  body size, separated by weight and colour only.
- **The ratios need an anchor.** Body is 16px on screen, 24px minimum in a deck
  (§10), 11–12pt in print (§9). Everything else resolves against that.
- **Fonts are installed locally or embedded.** Never satisfy the family rule by
  fetching a webfont from a CDN. Prose `ref`: Söhne, Untitled Sans, Suisse
  Int'l, IBM Plex Sans. Machine `ref`: Berkeley Mono, Söhne Mono, IBM Plex Mono,
  Commit Mono. When nothing is available the chain ends at `system-ui` /
  `ui-monospace` — never at Inter or Roboto by way of a fallback.
- Display headlines: leading **below 1.0** (0.95 `ref`), tracking **negative**
  (−0.02 to −0.03em). Author the line break by hand; two lines is the target.
- Body: leading 1.55–1.7, tracking 0, measure 60–75 characters, `text-wrap:
  pretty`.
- **Numerals are always tabular** in any table, metric, or price. Non-tabular
  figures in a data view is a bug.

### Text colour ramp

Three greys, each with a job. Contrast is the binding constraint.

| Role | Min contrast | `ref` |
|---|---|---|
| primary — headings, values | 13:1 | `#f4f5f6` |
| secondary — body, labels | 7:1 | `#b3b6b8` |
| tertiary — mono output, meta | 4.6:1 | `#8a8d90` |

**The minimum binds against the worst case, not against `bg`.** Check each tier
against the lightest surface it can land on — usually `raised`. At the `ref`
values every tier survives that check: on `#171717`, primary is 16.42:1,
secondary 8.79:1, tertiary 5.37:1.

The mono tier is **dimmer than the prose tier** by intent. Never go below
4.5:1 for anything a reader must actually read; decorative-only text does not
exist in this style.

### Two-tier numeral

For any headline figure — price, metric, total:

> large `primary` integer + smaller `tertiary` decimal, both tabular

Decimal is ~0.58× the integer size. Both baseline-aligned. This is the single
most portable idea in the system; use it wherever a number is the content.

---

## 6. Space, radius, rhythm

- **Spacing is a 4px-based scale.** `4 8 12 16 24 32 48 64 96` `ref`. Nothing
  off-scale, ever.
- **Layout with flex/grid and `gap`.** Never margins between siblings, never
  whitespace-as-spacing. Gap survives editing; margins don't.
- **Two radii, and only two:** small (`4px` `ref`) for pills, inputs, buttons,
  badges; large (`12px` `ref`) for cards, panels, modals. No third value. No
  full pills (`999px`) — they read as consumer-app, not tool.
- **Density comes from row count, not tightness.** Rows are generously padded
  vertically (~14–16px `ref`) and there are many of them. Never solve density
  by shrinking type or padding.
- **No zebra striping, no row dividers.** Group related rows in threes and
  fours; separate groups with a **single full-width hairline**. That hairline is
  the only rule in the table.
- **Numerals and pills align right, text aligns left.** No centred columns.
- A table wider than its container **scrolls inside its own box**; the page
  never scrolls sideways. In print a wide table is redrawn, not scrolled.
- Vertical rhythm between sections is larger than feels comfortable — at least
  2× the largest internal gap.

---

## 7. Iconography

- Outlined, uniform ~1.5px stroke, monochrome, inherits text colour.
- **16px or 20px.** Two sizes, no others.
- Icons live in a **gutter column**, aligned to each other — never inline mid-
  sentence, never inside a coloured circle or rounded square.
- A small standalone icon may act as an **eyebrow** above a heading, replacing a
  kicker label. One icon, no container, no colour.
- **No emoji.** Not in headings, not as bullets, not in status, not anywhere.
- Status/priority uses a **consistent glyph language**: a distinct shape per
  state that reads without colour (ring, half-ring, full ring, bars of
  increasing height for priority).

---

## 8. Controls

- **Toggle:** pill track, ~28×16 `ref`. Off = `raised` fill, knob `tertiary`.
  On = `accent` fill, knob white. No labels inside the track.
- **Select:** `raised` fill, small radius, chevron at right in `tertiary`,
  current value in `secondary`. Never a native select.
- **Button:** primary = inverted (near-white fill, `bg` text). Secondary =
  hairline border, no fill. Tertiary = text only. **One primary per view.**
- **Input:** `raised` fill, no border at rest, accent focus ring. Placeholder
  in `tertiary`.
- **Row with control:** label + one-line description on the left in
  `primary`/`secondary`, control right-aligned. This settings-row pattern is
  the workhorse layout — use it for any list of options.
- **Keyboard affordances are visible.** Shortcut keys render as mono badges
  with a hairline border, inline where the action is. Hint the model at its own
  keyboard grammar in place rather than hiding it in a help page.
- **Disabled:** a colour step, never an opacity. Fill drops to `bg`, label to
  `tertiary`, no focus ring. `opacity` breaks the §5 contrast minimums.
- **Loading:** skeletons are flat `raised` blocks at the finished element's
  dimensions. No shimmer, no pulse, no spinner laid over content.
- **Error:** one line in the negative label colour, directly below the field it
  belongs to and associated with it, always paired with a recovery action. Never
  a coloured border alone. States resolve by the §2 precedence order.
- Minimum hit target 44px on touch layouts.

---

## 9. Light counterpart

Same rules, inverted. **For documents, reports, and anything printed.** Not an
alternate theme for screens — screens stay dark.

| Dark | Light `ref` |
|---|---|
| `bg` `#0f0f0f` | `#faf9f7` — warm off-white, never pure `#ffffff` |
| `sunk` `#070707` | `#f0eeea` |
| `raised` `#171717` | `#ffffff` |
| hairline `#242424` | `#e2ded6` |
| primary `#f4f5f6` | `#16171a` |
| secondary `#b3b6b8` | `#4a4d52` |
| tertiary `#8a8d90` | `#75787d` |
| accent | `accent-light` `#066096` |

Note the inversion of the fill logic: on light, `raised` is *lighter* than the
page (white card on off-white). The rule "containers earn their edge by a fill
step" survives; the direction flips.

Print specifics: body 11–12pt minimum, measure 65–75 characters, no background
fills that cost ink, hairlines at 0.5pt. Status pills invert to a light tint
with a dark label.

---

## 10. Per-artifact rules

Which rule families bind, by class. **req** = required, **native** = the
medium's own equivalent, **n/a** = no target in this medium.

| | Deck | Dashboard | App UI | Document | Diagram |
|---|---|---|---|---|---|
| Surfaces, accent, type, space | req | req | req | req (light) | req |
| Token names in CSS | n/a | req | req | n/a | n/a |
| State variations | n/a | req | req | n/a | n/a |
| Overlays | n/a | req | req | n/a | n/a |
| Motion | n/a | req | req | n/a | n/a |
| Responsive behaviour | n/a | req | req | native | n/a |
| Table scroll + sticky | n/a | req | req | n/a | n/a |

`n/a` is not a licence to improvise. The rule has no target here; say so and
move on.

### Decks and presentations
1920×1080. Body text never below 24px; most text much larger. One idea per
slide. Max two background steps across the whole deck (`bg` and `sunk` for
section openers). Section openers are full-bleed with a single line of display
type. Data slides use the table and chart rules verbatim. No slide numbers
smaller than 18px. No transitions.

### Dashboards and data views
Modular bordered panels on a grid — nothing floats. A fixed right rail for
summary or narrative while the main column scrolls. Metric rows follow §6:
padded, undivided, grouped in threes. Tabular numerals everywhere. Two-tier
numeral for the headline figure. Crosshair with a full-series tooltip on charts;
per-series value flags at the plot's right edge.

Surfaces, text tiers, accent, and hairline are declared **once** as CSS custom
properties — `--bg`, `--sunk`, `--raised`, `--hairline`, `--text-primary`,
`--text-secondary`, `--text-tertiary`, `--accent` — and referenced by name.
Never inline a hex in markup.

Responsive: the right rail moves below the main column, the metric grid drops to
one column, and body size never shrinks — density still comes from row count.
Wide tables scroll; they stack only where each row reads on its own. Motion
follows the App UI rules below.

### App UI and prototypes
Sidebar in `sunk`, content in `bg`, rows in `raised`. Settings-row pattern for
any option list. Real interaction states — hover, focus, active, selected,
disabled — defined for every control before any of it is styled. Keyboard
shortcuts visible. Empty states are one sentence in `secondary` plus one
action, never an illustration.

Motion: ~150ms ceiling, opacity and colour only, no transform entrances, no
parallax, and `prefers-reduced-motion` turns all of it off. Same token contract
and responsive rules as dashboards.

### Documents and reports
Light counterpart, always. Flowing single column. Headings by weight and space,
not by rules or colour. Tables: hairline header underline only, no vertical
rules, no fills. One accent use per document at most, typically nothing.

### Diagrams and infographics
Neutral fills from the surface ramp; the accent marks the single most important
node or path. Labels in prose family, values in mono. No isometric projections,
no gradient nodes, no shadowed boxes, no clip-art. If a diagram needs more than
five colours it needs to be two diagrams.

---
