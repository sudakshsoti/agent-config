# calm

Measured against Headspace (`headspace.com`).

## Thesis

Play comes entirely from large flat colour fields and 24 to 112px radii. The
warm ground and the warm near-black ink are what stop it reading as childish.
One family, three weights, no second voice anywhere.

## When to use, when not

**Use it for** consumer surfaces, wellbeing and health, onboarding and first-run
explainers, a getting-started page, a changelog someone outside the team will
read, anything that has to feel approachable before it feels precise. It suits
content with few facts per screen and room to breathe.

**Not for** dense comparison, pricing matrices, spec tables or anything where
the reader is scanning for a number. The large radii and the colour fields eat
horizontal space and slow scanning down, which is the opposite of what a
comparison page needs. Use `instrument` for those. Also not for a long read: the
fields interrupt continuous prose every few hundred words. Use `editorial` for
that.

**Not the default.** Nothing here is a default. The direction is chosen in
Phase 0 and named out loud.

## Reference values

Measured from `headspace.com`. These are the reference's own values, in the
reference's own notation, so they can be checked against the source:

| Property | Measured value |
| --- | --- |
| Ground | `#f9f4f2` warm off-white, and `#fff` |
| Ink | `#2d2c2b` display, `#4b4c4d` body |
| Family | Headspace Apercu, **single family**, weights 400 / 500 / 700 only |
| H2 | 52px / 57.2px, weight **700**, tracking −1.56px (−0.03em) |
| Body | 16px / 18.4px |
| Radius scale | 8, 12, 16, 24, 30, 32, 112, 800px, plus `24px 24px 0 0` one-sided |
| Shadows | `0 1px 8px rgba(20,19,19,.2)`, `0 2px 0 rgba(65,61,69,.2)`, `0 3.23px 6.45px rgba(20,19,19,.2)` |
| Colour fields | blue `#0061ef`, yellow `#ffce00`, pink `#ffa1cc`, purple `#3b197f`, green `#02873e`, cyan `#00a4ff`, warm dark `#44423f` |
| Illustration | 133 inline SVG against 114 `<img>` |

**Measured against, not copied from.** Seven deliberate departures, each with
its reason:

1. **Body leading opens from 1.15 to 1.5.** The reference's 16/18.4 works
   because its body text arrives in one and two-line fragments beside
   illustrations. A studio artifact carries real paragraphs at a 60ch measure,
   where 1.15 is unreadable. 1.5 rather than 1.55, because leading is a
   function of measure and 60ch at 16px is a 480px line: 1.55 belongs to a
   longer one. The tight figure is kept where it was earned, on display:
   `--leading-display: 1.1` is the measured 57.2 ÷ 52.
2. **`#fff` becomes a warm near-white**, `oklch(0.993 0.0035 43)` = `#fffcfb`.
   The card still reads as white against the warm ground and the artifact
   contains no pure `#fff`, which the anti-pattern list bans. The difference
   next to `--ground` is invisible; the difference from a literal `#fff` is that
   the whole ladder is one temperature. Lightness is 0.993, not the 0.9945 this
   direction first carried: at 0.9945 the red channel clips the top of sRGB, so
   the token did not render as the value it declared. A colour specified to four
   decimals that the browser then clamps is worse than one specified to three
   that survives.
3. **The body ink is rewarmed.** Measured `#4b4c4d` is `oklch(0.416 0.002 248)`,
   which is faintly *cool* while the display ink `#2d2c2b` is warm at hue 68.
   `--ink-2` keeps the measured lightness and moves to hue 62, so nothing in the
   neutral ladder fights the ground. The display ink stays exactly as measured.
4. **The eight-step radius scale becomes four tokens**, 8 / 24 / a clamped
   large step / a true pill. The character of the reference is the *jump*
   between steps, and 12, 16, 30 and 32 sit close enough to 8 and 24 that eight
   steps blur into "everything is a bit rounded". The one-sided `24px 24px 0 0`
   survives as `var(--radius-md) var(--radius-md) 0 0`.
5. **Hanken Grotesk replaces Apercu**, which is not licensed here. It holds the
   single-family constraint: one grotesque across display, body and UI, at 400 /
   500 / 700. Mono is IBM Plex Mono, used only for literal commands.
6. **`--ground-3`, `--ink-3` and `--hair` are derived, not measured.** The
   reference signals almost everything with fields and cards and barely uses a
   rule, so it gives no hairline and no third surface. All three are interpolated
   along the ground's own hue (43) and checked for contrast rather than guessed.
7. **The blue accent is darkened just enough to be legal everywhere**,
   `oklch(0.525 0.220 260.5)` = `#005de6` against the measured `#0061ef`. The
   anti-pattern list warns off saturated accents at reading lengths, and lifts
   that ban for a colour that never sets reading-length text; the discipline
   here is to restrict where the colour lands rather than to desaturate it. But
   the measured value reached only 4.42:1 on `--ground-3`, so the direction had
   to carry a standing rule forbidding one surface. Two hundredths of lightness
   removes the rule: 4.71:1 on the deepest ground, and legal on all three. The
   hue is untouched and the chroma drops by 0.007, which is not a visible
   difference and is the whole cost of deleting a rule the author had to
   remember. See `## Accent policy`.

## Ground and ink

Four surfaces and three inks, every one on the ground's warm hue. Contrast is
WCAG 2.2, computed against `--ground` unless noted.

| Token | OKLCH | Hex | On `--ground` |
| --- | --- | --- | --- |
| `--ground` | `oklch(0.9705 0.006 43)` | `#f9f4f2` | — |
| `--ground-2` | `oklch(0.993 0.0035 43)` | `#fffcfb` | 1.07 (raised card) |
| `--ground-3` | `oklch(0.9385 0.0095 43)` | `#f1e9e6` | 1.10 (sunk block) |
| `--ink` | `oklch(0.2938 0.0023 68)` | `#2d2c2b` | 12.78 |
| `--ink-2` | `oklch(0.416 0.006 62)` | `#4e4b49` | 7.90 |
| `--ink-3` | `oklch(0.500 0.008 62)` | `#67625f` | 5.51 |
| `--hair` | `oklch(0.855 0.013 43)` | `#d7cdc9` | 1.43 (non-text) |
| `--accent` | `oklch(0.525 0.220 260.5)` | `#005de6` | 5.18 |

**The ladder reverses in the middle, and it is the only one of the four that
does.** `--ground-2` is *lighter* than the ground and means raised;
`--ground-3` is *darker* and means sunk. In the other three directions both
steps travel the same way, so an agent reaching for "ground-3" positionally
gets the deepest surface. Here it gets the sunk one, which may be the opposite
of what the layout wanted. The token file therefore aliases both by meaning:
`--surface-raised` and `--surface-sunk` resolve to `--ground-2` and
`--ground-3`, and new work should use the aliases. The numbered names stay so
that swapping another direction's `tokens.css` in overwrites them.

Every ink clears AA on every surface with headroom:

| Ink | On `--ground` | On `--ground-2` | On `--ground-3` |
| --- | --- | --- | --- |
| `--ink` | 12.78 | 13.65 | 11.61 |
| `--ink-2` | 7.90 | 8.44 | 7.18 |
| `--ink-3` | 5.51 | 5.89 | 5.01 |
| `--accent` | 5.18 | 5.53 | 4.71 |

`--ink-3` used to sit at lightness 0.525, which measured **4.50** on
`--ground-3` — the AA floor to two decimal places. A value set exactly on a
threshold has no tolerance for the changes a token system exists to absorb: a
gamut nudge, a browser's rounding, or a later tweak to either token, and it
fails. At 0.500 it clears 5.01 on the worst surface it can land on. There is no
lighter warm grey below it; if something needs to recede further it gets less
prominence, not less contrast.

## Surface ladder

**This is the one direction of the four that elevates with blur, and it does so
because the reference measurably does.** Of the seven references only Headspace
and Mercury blur anything at all, and Headspace's card lift is
`0 1px 8px rgba(20,19,19,.2)` — a 1px offset and an 8px blur at 20%. That single
value is `--shadow-1`. It is the whole depth budget.

Three levels, and the distinction between the second and the third is the point:

1. **Ground** — `--ground`, the warm off-white page. Nothing sits behind it.
2. **Raised** — `--ground-2` card with `--shadow-1`. A soft close lift, not a
   floating panel. Used where content is genuinely a separate object: the four
   direction panels.
3. **Sunk** — `--ground-3`, no shadow. A recess for literal content that is not
   prose: a command block, a code sample. Depth by tone, not by blur.

**Colour fields are not on this ladder.** A field is *painted*, not raised, so
it carries no shadow at any size. That is the rule that keeps the page from
looking like a stack of coloured cards, and it is also what makes the one blurred
shadow mean something when it appears.

The reference's second shadow, `0 2px 0 rgba(65,61,69,.2)`, is a flat 2px
offset with zero blur — a pressable affordance, not elevation. It belongs on a
button and nowhere else, and it now has its own token, `--shadow-press`. It
used to be specified in prose as a literal on the grounds that "there is one
shadow token and depth gets it", which is a design bending to a token budget
rather than to the design. Two shadows exist because the reference measurably
has two, and they mean different things: `--shadow-1` is depth,
`--shadow-press` is an affordance.

## Type roles

One family, Hanken Grotesk, at 400 / 500 / 700. IBM Plex Mono appears only where
the content is a literal command or identifier.

| Role | Family | Size | Weight | Line-height | Tracking |
| --- | --- | --- | --- | --- | --- |
| h1 | Hanken Grotesk | `--text-h1` 38px → 72px | 700 | 1.1 | see optical sizing |
| h2 | Hanken Grotesk | `--text-h2` 31.4px → 52px | 500 | 1.1 | see optical sizing |
| h3 | Hanken Grotesk | `--text-h3` 24px | 500 | `--leading-h3` (1.25) | −0.02em |
| lead | Hanken Grotesk | 20px | 400 | 1.45 | 0 |
| body | Hanken Grotesk | `--text-base` 16px | 400 | 1.55 | 0 |
| eyebrow | Hanken Grotesk | `--text-small` 13px | 500 | 1.2 | 0.08em, uppercase |
| meta | Hanken Grotesk | `--text-small` 13px | 400 | 1.4 | 0 |
| badge | Hanken Grotesk | `--text-small` 13px | 500 | 1 | 0 |
| button label | Hanken Grotesk | 16px | 500 | 1 | 0 |
| code | IBM Plex Mono | 13px | 400 | 1.6 | 0 |

`--text-h2` tops out at exactly the measured 52px. `--text-h1` is derived above
it at 72px, and both clamp so 390px and 1440px hold without a media query.

**h1 and h2 have to differ by more than a rounding.** They used to be 64 and
52, both weight 700, both leading 1.1, both −0.03em: a 12px gap and nothing
else, which in a one-family direction is not a hierarchy. h1 goes to 72px and
h2 drops to weight 500, so the two levels now differ in size *and* weight. That
also gives the middle weight a real job at display size, rather than appearing
once on a 24px h3.

**Display tracking scales with optical size.** −0.03em is the tightest value in
the whole studio set and it was measured at 52px. At the 31.4px floor it closes
Hanken Grotesk's counters and the heading reads as compressed. Both display
levels clamp their tracking with their size:

```css
h1, h2 { letter-spacing: clamp(-0.03em, -0.046em + 0.026rem, -0.016em); }
```

The eyebrow is the only positive tracking in the direction, and only because
13px uppercase closes up without it.

## Radius scale

| Token | Value | What it is for |
| --- | --- | --- |
| `--radius-sm` | 8px | Code blocks, badges, inputs. Anything holding a literal. |
| `--radius-md` | 24px | Cards and panels. The characteristic card radius. |
| `--radius-lg` | `clamp(40px, 8vw, 112px)` | Colour fields only. The signature. |
| `--radius-pill` | `9999px` | Buttons and pills. |

The gaps are the design. 8 to 24 to 112 is three unmistakably different shapes,
where the reference's eight steps include four values inside a 24px span. Dropped
from the measured scale: 12, 16, 30, 32.

**`--radius-lg` clamps rather than sitting at a flat 112px.** At 390 a flat
112px consumes 224 of roughly 358 available pixels, and the field stops being a
slab with soft corners and becomes a lozenge — the signature move broken at one
of the two widths the gate renders. The clamp holds 112px wherever there is room
for it and eases to 40px on a phone, which is still unmistakably the large step
and still nothing like `--radius-md`.

**`--radius-pill` is `9999px`, not the measured 800px.** 800px behaves
identically to `9999px` on everything under 1600px tall, and differs only in the
one case where it is wrong: on a genuinely tall element it stops being a
capsule. The measurement is interesting provenance and it was not earning its
token.

The one-sided form is written as
`border-radius: var(--radius-md) var(--radius-md) 0 0` and is only correct where
the block's bottom edge meets the bottom of its container, with
`overflow: hidden` on the parent so the square corners are clipped by the
parent's own radius. Anywhere else it is a rounded rectangle with two corners
forgotten.

`--radius-lg` stays reserved for full-width fields. On anything narrower than
the measure the same five colours read as decoration rather than as paint,
whatever the corner does.

## Accent policy

`--accent` is `oklch(0.5401 0.2271 260.5)`, the measured blue `#0061ef`. It is
the action colour and the primary field. `--accent-ink` is the warm near-white,
the same value as `--ground-2`, which clears 5.23 on the accent.

The measured palette has seven fields. One token can hold one. So:

- **All five measured fields are in the token set, each paired with its own
  ink.** They used to be prose: two of them, `--field-2` and `--field-3`, were
  specified as declarations the artifact made for itself beside the inlined
  token block. That put the direction's most distinctive asset outside the
  token layer, and it left a field and its ink as two independent values free
  to drift apart. The tokens are `--field-blue`, `--field-yellow`,
  `--field-pink`, `--field-purple` and `--field-green`, each with a
  `-ink` partner: reach for the pair, never for the fill alone.
- **Three fields is the ceiling for a whole artifact**, not per screen. Past
  three the colours stop being deliberate and start being a palette on display.
- **Ink on a field is chosen per field, not inherited.** The light fields need
  the warm near-black; the dark ones need the near-white. Measured ratios:

  | Field | Hex | Its `-ink` partner | Ratio |
  | --- | --- | --- | --- |
  | `--field-blue` | `#005de6` | warm near-white | **5.53** |
  | `--field-purple` | `#3b197f` | warm near-white | **12.60** |
  | `--field-green` | `#02873e` | warm near-white | **4.53** |
  | `--field-yellow` | `#ffce00` | warm near-black | **9.34** |
  | `--field-pink` | `#ffa1cc` | warm near-black | **7.45** |

  Every pairing clears AA. `--field-green` at 4.53 is the thinnest and is the
  one field to keep off small text.

- **The accent is a field, not an ink.** It may set a link in running text,
  where it clears 5.18 on the ground, and it may not set a paragraph, a heading,
  a hairline or a border. At 1px the chroma is wasted; at paragraph length it
  fatigues, which is the anti-pattern list's actual objection and the condition
  under which that list lifts its ban on saturated accents.
- **The accent is legal on all three surfaces**, including `--ground-3` at
  4.71. It was 4.42 there, which meant the direction carried a standing rule
  against one surface. The rule is gone because the value changed.

## Spacing rhythm

4 / 8 / 12 / 16 / 24 / 40 / 64 / 96px. Every step is on the 4px grid and the
scale widens the way the radius scale widens, so the page has the same habit at
both ends: small increments where things touch, large jumps where things
separate.

| Token | Value | Where it goes |
| --- | --- | --- |
| `--space-1` | 4px | Inside a badge, the focus-ring offset, icon to text. |
| `--space-2` | 8px | Gap between a label and its value. |
| `--space-3` | 12px | Between stacked lines of metadata. |
| `--space-4` | 16px | Paragraph spacing, gutter at 390px. |
| `--space-5` | 24px | Card padding at 390, grid gap. |
| `--space-6` | 40px | Card padding at 1440, space under a heading block. |
| `--space-7` | 64px | Padding inside a colour field, section break at 390. |
| `--space-8` | 96px | Between sections at 1440, and the page's top and bottom air. |

The scale used to start at 8px, which meant the direction had no small
increment at all: badge internals, icon-to-text and focus offsets all wanted 4
and had to take 8 or a literal. 4px is added at the bottom and 144px comes off
the top, since a section break at 96px against a 64px field inset is already
the widest ratio on the page.

The rhythm is deliberately uneven: prose blocks sit at `--space-3`, section
breaks at `--space-7` or `--space-8`. A page that uses one gap everywhere has no
rhythm, and this direction depends on the fields having air around them.

## Signature move

**A large flat colour field at a 112px radius, sitting on warm off-white, with
warm near-black ink for every word that is not on the field.**

The play is entirely in the field: its size, its flatness and its radius. No
gradient, no shadow, no border, no illustration inside it. One field opens the
page, at most two more appear later, and the rest of the page is warm paper.

What stops it reading as childish is the pair the reference chose and this
direction keeps exactly: the ground is `#f9f4f2`, warm off-white rather than
white, and the ink is `#2d2c2b`, warm near-black rather than black or grey. Swap
either one for a neutral and the same layout, the same radii and the same five
colours become a children's app. That is the whole reason the ink is specified to
four decimal places in `## Ground and ink`. The colour is the play; the warmth of
the ground and the ink is the adult in the room.

## Avoid list

1. **Pure `#000`, pure `#fff`, or any neutral-grey ink.** The warm near-black
   `#2d2c2b` is what holds the colour fields down. A neutral or true black turns
   the identical layout into a kids' app, and pure white loses the warm ground
   that the fields are read against.
2. **A second family anywhere.** The reference is one family across every role
   including UI. A display serif or a second grotesque next to Hanken Grotesk
   reintroduces exactly the editorial voice this direction does not have, and it
   is the fastest way to make the page look assembled rather than designed. IBM
   Plex Mono is not an exception: it is only ever a literal command, never a
   label, heading or caption.
3. **A radius outside the four tokens.** The character is the jump between
   steps. Adding 12 or 16 back closes the gap between small and medium until
   everything is merely "a bit rounded", which is the AI default this direction
   is furthest from. `--radius-lg` is a clamp, not a number: never hardcode
   112px, or the field breaks at 390.
4. **The same radius on everything.** Cards, code blocks, buttons and fields at
   one value flattens the one axis the direction plays on, and it is the third
   entry in the anti-pattern list's Page group.
5. **Small or narrow colour fields.** A field has to be large and flat to read
   as paint rather than as a coloured box. Under roughly 200px tall, or narrower
   than the measure, the same five colours read as primary-bright decoration.
   That is the childish failure, and it comes from field *size*, not from the
   hues.
6. **More than three flat colour fields on screen at once.** Past three, colour
   stops being a decision and becomes a palette being shown off. The reference
   paints one field per viewport and lets the warm ground carry the rest.
7. **The accent as body text, as a hairline or as a border.** It is a field
   colour. At 1px the chroma is invisible and wasted; at paragraph length the
   measured 0.227 chroma fatigues the eye. Links in running text are the only
   ink use it gets.
8. **A weight outside 400 / 500 / 700.** The reference has exactly three. A 300
   or a 600 slipping in makes the type read as drifting rather than set, and with
   one family the weights are the only hierarchy signal there is.
9. **A second blurred shadow.** `--shadow-1` at `0 1px 8px` and 20% is the
   entire depth budget, and `--shadow-press` is not a second one: its blur is
   zero and it is an affordance on a button, not a layer. Fields are painted and
   carry neither. A second *blur* claims a layer that does not exist, and the
   measured finding is that six of the seven references use no blur at all.
10. **A field colour used without its paired ink.** Every field ships as a
    `--field-*` / `--field-*-ink` pair because the correct ink flips with the
    field's lightness: yellow and pink take the warm near-black, blue, purple
    and green take the warm near-white. Reaching for the fill alone and
    inheriting whatever ink was in scope is how a field ends up at 1.47:1.

Cool grey in the neutral ladder is also out. The reference's own body ink is
faintly cool and it is the one measured value worth correcting: a cool grey
beside a warm ground reads as a theme somebody half-finished.

## Token map

35 properties, in the shared order. Everything here is live; **this is the only
one of the four directions whose `--shadow-1` is not `none`**, because Headspace
is one of only two of the seven references that blurs anything, and the blur is
measured rather than assumed.

| Token | Value | Meaning in this direction |
| --- | --- | --- |
| `--ground` | `oklch(0.9705 0.006 43)` | The warm off-white page. Every other neutral sits on its hue. |
| `--ground-2` | `oklch(0.993 0.0035 43)` | Raised card, aliased `--surface-raised`. Reads as white, is not `#fff`, and unlike 0.9945 it does not clip sRGB. |
| `--ground-3` | `oklch(0.9385 0.0095 43)` | Sunk block for literals, aliased `--surface-sunk`. Darker than the ground: the ladder reverses here. |
| `--ink` | `oklch(0.2938 0.0023 68)` | Warm near-black. Display, headings, and ink on light fields. |
| `--ink-2` | `oklch(0.416 0.006 62)` | Body prose. Measured lightness, rewarmed hue. |
| `--ink-3` | `oklch(0.500 0.008 62)` | Metadata and captions. 5.01 on the worst surface, with headroom rather than on the line. |
| `--hair` | `oklch(0.855 0.013 43)` | Soft warm rule, used sparingly: the reference separates with space and fields, not lines. Derived. |
| `--accent` | `oklch(0.525 0.220 260.5)` | The measured blue, darkened until it is legal on every surface. Primary colour field and link colour. Never a border. |
| `--accent-ink` | `oklch(0.993 0.0035 43)` | Ink on the accent and on the other dark fields. Same value as `--ground-2`. |
| `--field-*` | five measured hues | The measured palette, in the token set rather than in the artifact. |
| `--field-*-ink` | near-black or near-white | Each field's own ink, so the pair cannot drift apart. |
| `--ring` | `oklch(0.2938 0.0023 68)` | The `:focus-visible` ring. The warm near-black, because the accent is a field. |
| `--ring-offset` | `0.25rem` | Clearance around the ring, filled with the surface underneath. |
| `--radius-sm` | `8px` | Code, badges, inputs. |
| `--radius-md` | `24px` | Cards and panels, and the one-sided `24px 24px 0 0`. |
| `--radius-lg` | `clamp(40px, 8vw, 112px)` | Colour fields only. The signature, and it has to survive 390. |
| `--radius-pill` | `9999px` | Buttons. A true capsule at any height. |
| `--font-display` | Hanken Grotesk stack | Same family as body. Single-family is the constraint. |
| `--font-body` | Hanken Grotesk stack | Identical to `--font-display` on purpose, not by omission. |
| `--font-mono` | IBM Plex Mono stack | Literal commands and identifiers only. |
| `--text-base` | `1rem` | 16px, the measured body size. |
| `--text-h1` | `clamp(2.375rem, 1.6rem + 3.9vw, 4.5rem)` | 38px at 390, 72px at 1440. Far enough above h2 to be a level. |
| `--text-h2` | `clamp(1.875rem, 1.45rem + 2.1vw, 3.25rem)` | 31.4px at 390, 52px at 1440. The 52px is measured. |
| `--text-h3` | `1.5rem` | 24px, weight 500. |
| `--leading-h3` | `1.25` | The h3, which the display leading would close up. |
| `--text-small` | `0.8125rem` | 13px. Eyebrow, badge, metadata, code. |
| `--leading-body` | `1.5` | Opened from the measured 1.15, which was set for fragments not paragraphs, and matched to the 60ch measure. |
| `--leading-display` | `1.1` | The measured 57.2 ÷ 52. |
| `--track-display` | `-0.03em` | Measured at 52px. The tightest of the four, and clamped looser as the display sizes shrink. |
| `--track-body` | `0em` | Body is untracked. The eyebrow's positive tracking is a local override, not a token. |
| `--measure` | `60ch` | Prose column. Generous rather than dense, in keeping with the ground. |
| `--space-1` | `0.25rem` | 4px. Badge internals, focus-ring offset. |
| `--space-2` | `0.5rem` | 8px. Label to value. |
| `--space-3` | `0.75rem` | 12px. Stacked metadata. |
| `--space-4` | `1rem` | 16px. Paragraph spacing, gutter at 390. |
| `--space-5` | `1.5rem` | 24px. Card padding at 390, grid gap. |
| `--space-6` | `2.5rem` | 40px. Card padding at 1440. |
| `--space-7` | `4rem` | 64px. Padding inside a colour field, section break at 390. |
| `--space-8` | `6rem` | 96px. Section break at 1440, page top and bottom air. |
| `--shadow-1` | `0 1px 8px oklch(0.188 0.002 17 / 0.2)` | The measured `rgba(20,19,19,.2)` card lift, in OKLCH. Live, not inert. Cards only, never fields. |
| `--shadow-press` | `0 2px 0 oklch(0.3670 0.0145 308 / 0.2)` | The measured `rgba(65,61,69,.2)` button affordance. Zero blur, so it is not a second depth level. |

Nothing is left for the artifact to declare. The five fields, their five inks,
the press affordance and the focus ring are all tokens, because each one was
previously specified in prose and therefore had to arrive in the artifact as a
hardcoded value — the exact thing hard rule 4 exists to catch.

Three fields remains the ceiling for a whole artifact. Five tokens exist so the
choice is made from a named set, not so five appear on one page.

`font-variant-numeric: tabular-nums` on any table or stat block, and
`color-scheme: light` on `:root`.
