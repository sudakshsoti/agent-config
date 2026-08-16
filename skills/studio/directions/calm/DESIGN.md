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

1. **Body leading opens from 1.15 to 1.55.** The reference's 16/18.4 works
   because its body text arrives in one and two-line fragments beside
   illustrations. A studio artifact carries real paragraphs at a 60ch measure,
   where 1.15 is unreadable. The tight figure is kept where it was earned, on
   display: `--leading-display: 1.1` is the measured 57.2 ÷ 52.
2. **`#fff` becomes a warm near-white**, `oklch(0.9945 0.0035 43)` = `#fffdfb`.
   The card still reads as white against the warm ground and the artifact
   contains no pure `#fff`, which the anti-pattern list bans. The difference
   next to `--ground` is invisible; the difference from a literal `#fff` is that
   the whole ladder is one temperature.
3. **The body ink is rewarmed.** Measured `#4b4c4d` is `oklch(0.416 0.002 248)`,
   which is faintly *cool* while the display ink `#2d2c2b` is warm at hue 68.
   `--ink-2` keeps the measured lightness and moves to hue 62, so nothing in the
   neutral ladder fights the ground. The display ink stays exactly as measured.
4. **The eight-step radius scale becomes four tokens**, 8 / 24 / 112 / 800. The
   character of the reference is the *jump* between steps, and 12, 16, 30 and 32
   sit close enough to 8 and 24 that eight steps blur into "everything is a bit
   rounded". The one-sided `24px 24px 0 0` survives as
   `var(--radius-md) var(--radius-md) 0 0`.
5. **Hanken Grotesk replaces Apercu**, which is not licensed here. It holds the
   single-family constraint: one grotesque across display, body and UI, at 400 /
   500 / 700. Mono is IBM Plex Mono, used only for literal commands.
6. **`--ground-3`, `--ink-3` and `--hair` are derived, not measured.** The
   reference signals almost everything with fields and cards and barely uses a
   rule, so it gives no hairline and no third surface. All three are interpolated
   along the ground's own hue (43) and checked for contrast rather than guessed.
7. **The blue accent is kept at full measured chroma**,
   `oklch(0.5401 0.2271 260.5)` = `#0061ef`. The anti-pattern list warns off
   saturated accents at reading lengths; the discipline here is not to desaturate
   but to restrict where the colour lands. See `## Accent policy`.

## Ground and ink

Four surfaces and three inks, every one on the ground's warm hue. Contrast is
WCAG 2.2, computed against `--ground` unless noted.

| Token | OKLCH | Hex | On `--ground` |
| --- | --- | --- | --- |
| `--ground` | `oklch(0.9705 0.006 43)` | `#f9f4f2` | — |
| `--ground-2` | `oklch(0.9945 0.0035 43)` | `#fffdfb` | 1.06 (raised card) |
| `--ground-3` | `oklch(0.9385 0.0095 43)` | `#f1e9e6` | 1.10 (sunk block) |
| `--ink` | `oklch(0.2938 0.0023 68)` | `#2d2c2b` | 12.78 |
| `--ink-2` | `oklch(0.416 0.006 62)` | `#4e4b49` | 7.93 |
| `--ink-3` | `oklch(0.525 0.008 62)` | `#6e6966` | 4.97 |
| `--hair` | `oklch(0.855 0.013 43)` | `#d7cdc9` | 1.43 (non-text) |

`--ink-3` is set at the lightness where it still clears 4.5 against every
surface in the ladder, including `--ground-3` at 4.53, because small metadata is
normal-size text as far as WCAG is concerned. There is no lighter warm grey
below it; if something needs to recede further it gets less prominence, not less
contrast.

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

The reference's second shadow, `0 2px 0 rgba(65,61,69,.2)`, is a flat 2px offset
with zero blur — a pressable affordance, not elevation. It belongs on a button
and nowhere else, and where a button exists it is written as a literal rather
than a token, because there is one shadow token and depth gets it.

## Type roles

One family, Hanken Grotesk, at 400 / 500 / 700. IBM Plex Mono appears only where
the content is a literal command or identifier.

| Role | Family | Size | Weight | Line-height | Tracking |
| --- | --- | --- | --- | --- | --- |
| h1 | Hanken Grotesk | `--text-h1` 40.5px → 64px | 700 | 1.1 | −0.03em |
| h2 | Hanken Grotesk | `--text-h2` 31.4px → 52px | 700 | 1.1 | −0.03em |
| h3 | Hanken Grotesk | `--text-h3` 24px | 500 | 1.25 | −0.02em |
| lead | Hanken Grotesk | 20px | 400 | 1.45 | 0 |
| body | Hanken Grotesk | `--text-base` 16px | 400 | 1.55 | 0 |
| eyebrow | Hanken Grotesk | `--text-small` 13px | 500 | 1.2 | 0.08em, uppercase |
| meta | Hanken Grotesk | `--text-small` 13px | 400 | 1.4 | 0 |
| badge | Hanken Grotesk | `--text-small` 13px | 500 | 1 | 0 |
| button label | Hanken Grotesk | 16px | 500 | 1 | 0 |
| code | IBM Plex Mono | 13px | 400 | 1.6 | 0 |

`--text-h2` tops out at exactly the measured 52px. `--text-h1` is derived above
it at 64px, and both clamp so 390px and 1440px hold without a media query:
`--text-h1` lands at 40.5px on a 390 viewport, `--text-h2` at 31.4px.

The eyebrow is the only positive tracking in the direction, and only because
13px uppercase closes up without it.

## Radius scale

| Token | Value | What it is for |
| --- | --- | --- |
| `--radius-sm` | 8px | Code blocks, badges, inputs. Anything holding a literal. |
| `--radius-md` | 24px | Cards and panels. The characteristic card radius. |
| `--radius-lg` | 112px | Colour fields only. The signature. |
| `--radius-pill` | 800px | Buttons and pills. The measured pill value, not `9999px`. |

The gaps are the design. 8 to 24 to 112 is three unmistakably different shapes,
where the reference's eight steps include four values inside a 24px span. Dropped
from the measured scale: 12, 16, 30, 32.

The one-sided form is written as
`border-radius: var(--radius-md) var(--radius-md) 0 0` and is only correct where
the block's bottom edge meets the bottom of its container, with
`overflow: hidden` on the parent so the square corners are clipped by the
parent's own radius. Anywhere else it is a rounded rectangle with two corners
forgotten.

At 390px a 112px radius consumes 224 of roughly 358 available pixels and the
field reads as a soft slab. That is intended, and it is why `--radius-lg` is
reserved for full-width fields; on anything narrower than about 320px it becomes
a pill by accident.

## Accent policy

`--accent` is `oklch(0.5401 0.2271 260.5)`, the measured blue `#0061ef`. It is
the action colour and the primary field. `--accent-ink` is the warm near-white,
the same value as `--ground-2`, which clears 5.23 on the accent.

The measured palette has seven fields. One token can hold one. So:

- **`--accent` is the only field colour in the token set.** A second or third
  field is declared in the artifact, next to the inlined token block, as
  `--field-2` and `--field-3`, drawn only from the measured five: blue
  `#0061ef`, yellow `#ffce00`, pink `#ffa1cc`, purple `#3b197f`, green
  `#02873e`.
- **Three fields is the ceiling for a whole artifact**, not per screen. Past
  three the colours stop being deliberate and start being a palette on display.
- **Ink on a field is chosen per field, not inherited.** The light fields need
  the warm near-black; the dark ones need the near-white. Measured ratios:

  | Field | Hex | With `--ink` | With `--accent-ink` |
  | --- | --- | --- | --- |
  | blue | `#0061ef` | 2.63 fail | **5.23 pass** |
  | purple | `#3b197f` | 1.08 fail | **12.68 pass** |
  | green | `#02873e` | 3.01 fail | **4.56 pass** |
  | yellow | `#ffce00` | **9.35 pass** | 1.47 fail |
  | pink | `#ffa1cc` | **7.45 pass** | 1.84 fail |

- **The accent is a field, not an ink.** It may set a link in running text,
  where it clears 4.87 on the ground, and it may not set a paragraph, a heading,
  a hairline or a border. At 1px the chroma is wasted; at paragraph length it
  fatigues, which is the anti-pattern list's actual objection.
- **No accent on `--ground-3`.** 4.43 is under AA for normal text. Links live on
  `--ground` and `--ground-2`.

## Spacing rhythm

8 / 12 / 16 / 24 / 40 / 64 / 96 / 144px. Every step is on the 4px grid and the
scale widens the way the radius scale widens, so the page has the same habit at
both ends: small increments where things touch, large jumps where things
separate.

| Token | Value | Where it goes |
| --- | --- | --- |
| `--space-1` | 8px | Inside a badge, gap between a label and its value. |
| `--space-2` | 12px | Between stacked lines of metadata. |
| `--space-3` | 16px | Paragraph spacing, gutter at 390px. |
| `--space-4` | 24px | Card padding at 390, grid gap. |
| `--space-5` | 40px | Card padding at 1440, space under a heading block. |
| `--space-6` | 64px | Padding inside a colour field. |
| `--space-7` | 96px | Between sections at 390. |
| `--space-8` | 144px | Between sections at 1440, and the page's top and bottom air. |

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
3. **A radius outside 8 / 24 / 112, plus the 800px pill.** The character is the
   jump between steps. Adding 12 or 16 back closes the gap between small and
   medium until everything is merely "a bit rounded", which is the AI default
   this direction is furthest from.
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
9. **A second blurred shadow.** `0 1px 8px` at 20% is the entire depth budget.
   Fields are painted and carry none; a second blur claims a layer that does not
   exist, and the measured finding is that six of the seven references use no
   blur at all.
10. **Cool grey in the neutral ladder.** The reference's own body ink is faintly
    cool and it is the one measured value worth correcting. A cool grey beside a
    warm ground reads as a theme somebody half-finished.

## Token map

35 properties, in the shared order. Everything here is live; **this is the only
one of the four directions whose `--shadow-1` is not `none`**, because Headspace
is one of only two of the seven references that blurs anything, and the blur is
measured rather than assumed.

| Token | Value | Meaning in this direction |
| --- | --- | --- |
| `--ground` | `oklch(0.9705 0.006 43)` | The warm off-white page. Every other neutral sits on its hue. |
| `--ground-2` | `oklch(0.9945 0.0035 43)` | Raised card. Reads as white, is not `#fff`. |
| `--ground-3` | `oklch(0.9385 0.0095 43)` | Sunk block for literals: commands, code. Derived. |
| `--ink` | `oklch(0.2938 0.0023 68)` | Warm near-black. Display, headings, and ink on light fields. |
| `--ink-2` | `oklch(0.416 0.006 62)` | Body prose. Measured lightness, rewarmed hue. |
| `--ink-3` | `oklch(0.525 0.008 62)` | Metadata and captions. The lightest ink that still clears AA. Derived. |
| `--hair` | `oklch(0.855 0.013 43)` | Soft warm rule, used sparingly: the reference separates with space and fields, not lines. Derived. |
| `--accent` | `oklch(0.5401 0.2271 260.5)` | The measured blue. Primary colour field and link colour. Never a border. |
| `--accent-ink` | `oklch(0.9945 0.0035 43)` | Ink on the accent and on the other dark fields. Same value as `--ground-2`. |
| `--radius-sm` | `8px` | Code, badges, inputs. |
| `--radius-md` | `24px` | Cards and panels, and the one-sided `24px 24px 0 0`. |
| `--radius-lg` | `112px` | Colour fields only. The signature. |
| `--radius-pill` | `800px` | Buttons. The measured pill, not `9999px`. |
| `--font-display` | Hanken Grotesk stack | Same family as body. Single-family is the constraint. |
| `--font-body` | Hanken Grotesk stack | Identical to `--font-display` on purpose, not by omission. |
| `--font-mono` | IBM Plex Mono stack | Literal commands and identifiers only. |
| `--text-base` | `1rem` | 16px, the measured body size. |
| `--text-h1` | `clamp(2.375rem, 1.75rem + 3.2vw, 4rem)` | 40.5px at 390, 64px at 1440. Derived above the measured h2. |
| `--text-h2` | `clamp(1.875rem, 1.45rem + 2.1vw, 3.25rem)` | 31.4px at 390, 52px at 1440. The 52px is measured. |
| `--text-h3` | `1.5rem` | 24px. Weight 500, the only place the middle weight leads. |
| `--text-small` | `0.8125rem` | 13px. Eyebrow, badge, metadata, code. |
| `--leading-body` | `1.55` | Opened from the measured 1.15, which was set for fragments not paragraphs. |
| `--leading-display` | `1.1` | The measured 57.2 ÷ 52. |
| `--track-display` | `-0.03em` | Measured. The tightest of the four directions. |
| `--track-body` | `0em` | Body is untracked. The eyebrow's positive tracking is a local override, not a token. |
| `--measure` | `60ch` | Prose column. Generous rather than dense, in keeping with the ground. |
| `--space-1` | `0.5rem` | 8px. |
| `--space-2` | `0.75rem` | 12px. |
| `--space-3` | `1rem` | 16px. Paragraph spacing. |
| `--space-4` | `1.5rem` | 24px. Card padding at 390, grid gap. |
| `--space-5` | `2.5rem` | 40px. Card padding at 1440. |
| `--space-6` | `4rem` | 64px. Padding inside a colour field. |
| `--space-7` | `6rem` | 96px. Section break at 390. |
| `--space-8` | `9rem` | 144px. Section break at 1440, page top and bottom air. |
| `--shadow-1` | `0 1px 8px oklch(0.188 0.002 17 / 0.2)` | The measured `rgba(20,19,19,.2)` card lift, in OKLCH. Live, not inert. Cards only, never fields. |

Two values the artifact declares itself, because the token set has room for one
field and the direction allows three: `--field-2` and `--field-3`, taken from the
measured five and paired with the ink from the table in `## Accent policy`. The
button's flat `0 2px 0` affordance is likewise a literal, since the one shadow
token belongs to depth.
