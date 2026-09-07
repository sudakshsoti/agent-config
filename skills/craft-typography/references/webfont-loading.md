# Webfont loading

Delivery mechanics that decide whether a webfont's arrival is invisible or a visible shift.

## `font-display` by role

`font-display` is chosen per role, not applied uniformly across every `@font-face`. A reading face — the one carrying long-form body text — tolerates `swap`'s visible transition less well than a display face used only on short, large headings, where the swap is quick to read past. There is no single correct value for every face on a page; the role decides.

## Preload only the above-fold face

Preloading every family, weight and subset "to avoid the swap" competes for bandwidth with the content those requests are meant to reveal faster. Preload is scoped to the one face rendered above the fold on first paint; everything else loads on its own schedule.

## `unicode-range` splits per script

Splitting a family into per-script subset files, each declared with its own `unicode-range`, means a page using only Latin content never fetches the Cyrillic or Devanagari subset. The split has to be exhaustive over the content's actual scripts — see the `unicode-range` rule in `../SKILL.md`.

## Deriving the metric-override descriptors

`size-adjust`, `ascent-override`, `descent-override` and `line-gap-override` are declared on the **fallback** `@font-face` block, not the webfont, and their values are a derivation, not a guess:

- `size-adjust` is the ratio of the webfont's ex-height to the named fallback's ex-height at the same nominal size — not a copy of either font's own `hhea` numbers, which describe the font in isolation rather than the pair.
- `ascent-override`, `descent-override` and `line-gap-override` are set only where the fallback's own metrics differ enough from the webfont's to produce a visible line-box height mismatch; each is expressed as a percentage of the fallback's em.

Record the actual measured numbers for the font pair used in the project's verification fixture, with the browser and version they were measured in, because the derivation is pair-specific: a fallback declared for one webfont carries different override values than the same fallback declared for a different webfont.

## Sources

- `archive/skills/typography-craft/SKILL.md` @ `201bd7ed9072269c1081a0e4d2315868b84649e4`.
- MDN, `@font-face`: `font-display`, `size-adjust`, `ascent-override`, `descent-override`, `line-gap-override`, `unicode-range`.
- CSS Fonts Module Level 4 (W3C).

## Gotcha

Agents preload every family, weight and subset to "avoid the swap" — each preload competes with the content it was meant to reveal faster, and a page that preloads six font files can paint its actual content later than one that preloads none. Preload the one face used above the fold; let the rest follow its own priority.
