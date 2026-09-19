# Surfaces and icons

Concentric radius, shadow-as-border, image outlines, optical alignment and icon mechanics that support `../SKILL.md`.

## Concentric border radius

`outerRadius = innerRadius + padding`. Mismatched radii on closely nested surfaces are the most common thing that reads as off.

```css
.card { border-radius: 20px; padding: 8px; }     /* 12 + 8 */
.card-inner { border-radius: 12px; }
```

Past `24px` of padding, treat the layers as separate surfaces and pick each radius independently rather than forcing the maths.

## Shadow as border

Where a border exists only for depth, not structure, replace it with layered `box-shadow`. Never apply this to dividers, table boundaries, or any border whose job is layout separation; those stay borders.

Light mode, three layers: a 1px ring, subtle lift, ambient depth.

```css
--shadow-border:
  0px 0px 0px 1px oklch(0 0 0 / 0.06),
  0px 1px 2px -1px oklch(0 0 0 / 0.06),
  0px 2px 4px 0px oklch(0 0 0 / 0.04);
--shadow-border-hover:
  0px 0px 0px 1px oklch(0 0 0 / 0.08),
  0px 1px 2px -1px oklch(0 0 0 / 0.08),
  0px 2px 4px 0px oklch(0 0 0 / 0.06);
```

Dark mode collapses to one ring, since layered depth shadows are invisible on dark backgrounds:

```css
--shadow-border: 0 0 0 1px oklch(1 0 0 / 0.08);
--shadow-border-hover: 0 0 0 1px oklch(1 0 0 / 0.13);
```

## Image outlines

`1px` outline at `-1px` offset (`outline`, not `border`, so it adds no layout width and hugs the corner radius). Pure black at 10% in light, pure white at 10% in dark:

```css
img { outline: 1px solid oklch(0 0 0 / 0.1); outline-offset: -1px; }
```

```css
/* dark mode */
img { outline: 1px solid oklch(1 0 0 / 0.1); outline-offset: -1px; }
```

Never a near-black or near-white from the project palette (slate-900, zinc-900, `#0a0a0a`) and never the accent or ink colour. A tinted outline picks up the surface underneath and reads as dirt on the image edge.

## Optical alignment

**Icon-side button padding**: `icon-side padding = text-side padding - 2px`. Where equal padding on both sides of a button with a trailing icon looks like the icon is pushed too far out, trim its side by 2px.

**Play triangles**: the geometric centre of a triangle is not its visual centre. Shift right with `transform: translateX(2px)` on the glyph.

**Asymmetric icons** (stars, arrows, carets): fix the SVG viewBox or path directly so the component needs no extra margin. A margin-based nudge (`translate-x-px`) is the fallback, not the first move.

## Icon stroke weight

Match stroke to the adjacent text weight, on a 24px grid:

| Adjacent text | Stroke width |
| --- | --- |
| Regular (400), 14-16px | `1.5px` |
| Medium/Semibold (500-600) | `2px` |
| Bold (700), or emphasised standalone | `2.5px` |

One icon library and one stroke convention per surface; never mix libraries with incompatible strokes on one toolbar.

## Icon sizing

Size inline icons relative to the text's cap height, `1em` to `1.25em`, so the pair scales together. Test every icon at the smallest size it will render, typically `16px`; thin interior lines and tight counters blur or alias below that. Use the icon set's native grid sizes (`16`, `20`, `24`) rather than arbitrary fractional scales, and always ship SVG, never raster.

## One SVG, recoloured per state

One asset drawn with `currentColor`; state comes from CSS colour and opacity, never from separate asset files or hardcoded fills (`fill="#666"`). Strip hardcoded fills on import.

Where an icon set offers outline and filled variants, use them as a state pair, not interchangeably: outline is the default (toolbars, list rows, inline with text), fill marks selected or active (the active tab, a toggled bookmark, a liked heart). The swap between the two is a contextual icon animation; see `motion-values.md`.

## Icons in RTL

Flip icons whose meaning is tied to reading direction; leave the rest alone.

| Flip | Never flip |
| --- | --- |
| Back/forward arrows, navigation chevrons | Logos and brand marks |
| Text-block glyphs (alignment, lists, indent) | Checkmarks |
| Speaker/volume waves | Physical objects: clocks, cups, pencils |
| "Send"-style directional glyphs | Media playback (play/rewind refer to tape direction by convention and stay LTR) |

```css
[dir="rtl"] .icon-directional { scale: -1 1; }
```

Analyse composite icons part by part: a badge or slash overlay on a base glyph may keep its position even when the base flips.
