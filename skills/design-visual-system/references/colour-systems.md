# Colour systems

Ramp formation, token architecture and contrast thresholds that support `../SKILL.md`. A colour system is ramps named by role, not colours picked in isolation.

## Ramp formation

A correct ramp, checkable in any notation:

- Steps land evenly in perceived lightness, not in whatever the format calls lightness. HSL's lightness is not perceptual; evenly spaced HSL values bunch at one end.
- Hue stays constant end to end.
- Vividness peaks mid-ramp and falls off at both ends; a `50` at full vividness glows, a `950` at full vividness looks like ink.
- Steps sit denser at the light end than the dark end: keep `50`-`200` close together, `800`-`950` further apart. Even spacing across the whole range makes `50` and `100` stop reading as two surfaces.
- Both ends stop short of pure black and white, which cannot carry hue.

Never compute a ramp by hand or by eye. Use a perceptual-interpolation library (`culori`, `colorjs.io`, `chroma.js`), read the brand colour in whatever format it arrives, interpolate in a perceptual space (`lab` or `oklab`), and emit the project's own notation:

```js
import { formatHex, interpolate, samples } from 'culori'
const ramp = interpolate(['#eff6ff', '#3b82f6', '#172554'], 'lab')
const steps = samples(11).map((t) => formatHex(ramp(t)))
```

## Radix versus Tailwind step models

Radix defines its 12 steps **by role**: step 9 is "the solid fill" in every ramp and every appearance, and the dark scale reuses the same numbers, so `--accent-9` is the fill in both and component CSS never changes between themes.

Tailwind defines its 11 steps **by lightness**: `50` is light, `950` is dark. The role mapping below holds in light mode and inverts in dark, so components either swap step numbers per appearance or read a semantic token that swaps once.

| Role | Tailwind | Radix |
| --- | --- | --- |
| Page background | `50` | `1` |
| Subtle background | `50` | `2` |
| Component background | `100` | `3` |
| Component hover | `200` | `4` |
| Component active / selected | `200` | `5` |
| Subtle border | `200` | `6` |
| Border, separator | `300` | `7` |
| Strong border, focus ring | `400` | `8` |
| Solid fill | `500` | `9` |
| Solid fill hover | `600` | `10` |
| Low-contrast text | `700` | `11` |
| High-contrast text | `900` | `12` |

Tailwind's 11 steps cover 12 roles, so some double up; where the table repeats a step, a design needing those two roles distinguishable needs a 12-step ramp. For a new system, prefer the Radix role-defined model: a role-defined step survives a theme change that a lightness-defined step does not. On an existing Tailwind project keep `50`-`950` and put the role mapping in the semantic tier rather than fighting the convention.

## Token grammar and tiering

Two tiers, never one:

- **Primitives** name a value by hue and step (`--blue-500`, `--neutral-200`). Never applied directly in a component.
- **Semantics** name a job (`--color-text-secondary`), point at a primitive, and are the only tier components reference.

```css
:root {
  --blue-500: #3b82f6;
  --neutral-700: #374151;

  --color-accent-solid: var(--blue-500);
  --color-text-secondary: var(--neutral-700);
}
```

Grammar: `--color-{role}-{variant}-{state}` (`--color-bg-surface`, `--color-accent-solid-hover`). Pick one word per concept and never mix synonyms: `text` not `fg`/`foreground`/`ink`; `bg` not `background`/`fill`; `border` not `stroke`/`outline`/`line`; `accent` not `primary`/`brand`/`theme`. Reserve `primary` for "most prominent of its group", never for the brand colour, so `--color-text-primary` and `--color-accent-solid` cannot collide.

A third, component-level tier (`--color-button-danger-bg`) is a documented exception for one component's genuine divergence. Twenty component tokens means the semantic tier is missing roles.

Two tiers versus three: keep two-tier as the default and add the third only when a component cannot be served by any semantic role, not when a component merely wants a different value today.

Anti-patterns: `--color-blue-button` (appearance named at the semantic tier, lies when the brand changes), `--color-sidebar-gray` (named for first use), `--color-light-gray` (lies in dark mode), `--color-text-2` (numbered semantics carry no meaning), `--blue-500` used directly in a component (skips the theming seam).

## Contrast: APCA alongside WCAG, never replacing it

**WCAG 2.2 is the conformance check.** Report APCA Lc only as an additional perceptual measure, never as a substitute for a WCAG conformance claim (see `../SKILL.md` §2). Where a project must claim formal WCAG 2.x conformance, WCAG is the gate and APCA is the tiebreaker for anything already passing WCAG.

WCAG 2 thresholds:

| Content type | AA | AAA |
| --- | --- | --- |
| Normal text (<24px / <18.5px bold) | 4.5:1 | 7:1 |
| Large text (≥24px / ≥18.5px bold) | 3:1 | 4.5:1 |
| UI components and graphical objects | 3:1 | n/a |

APCA Lc thresholds, used as the supplementary perceptual measure:

| Content type | Minimum | Preferred |
| --- | --- | --- |
| Body text | Lc 75 | Lc 90 |
| Non-body text (labels, headlines) | Lc 60 | Lc 75 |
| Large text (≥36px) | Lc 45 | Lc 60 |
| UI components | Lc 30 | n/a |

Lc 30 is also APCA's minimum for disabled and placeholder text; Lc 15 is the floor for a non-text element to be discernible at all.

Lc is signed and polarity-aware: positive is dark text on light, negative is light text on dark, and mirrored pairs do not score identically, so compare the absolute value against the threshold and recheck both appearances independently.

Quick approximation for a first pass, always verified by measuring before reporting: on a light background above ~90% perceived lightness, body text needs a foreground below ~35% to clear Lc 75; on a dark background below ~25%, a foreground above ~90%. The light/dark crossover for which text colour scores higher sits around 73% perceived lightness, higher than intuition suggests.

To fix a failing pair, change lightness first, holding hue and saturation; hue and saturation move the measured value far less. Report the pair, its measured value and the threshold it misses, and leave it unchanged unless asked to fix it.

## Never quietly darken the brand

A brand colour that fails contrast is still the brand colour. Two decisions come first: which step it occupies (the solid-fill step, `500`/`9`, so `bg-brand-500` renders the real value), and whether it is pinned or snapped.

- **Pin** a contractually fixed brand colour: it stays exact, the ramp builds outward from it, and that one step spaces slightly unevenly.
- **Snap** it onto the ramp otherwise: every step spaces evenly and nobody notices without a swatch held to the screen.

State which was done. If the pinned brand step fails contrast against white text, use a darker step for interactive fills; never darken the brand step itself to make it pass.

## Per-hue vividness and status collisions

Hues do not share a maximum vividness: yellow and cyan peak far lower than red and blue. Copying a saturation number across hues leaves yellow and cyan washed out relative to red and blue at the "same" step. Match each ramp to the same *proportion* of its own hue's maximum, not the same absolute number, and match perceived lightness exactly step for step across hues so `danger-500` and `brand-500` read equally bright.

Status hues must stay distinct from the accent: if the brand is red, the danger ramp cannot also be red. Move danger toward a deeper crimson and check the two side by side. Status ramps carry fewer steps than the accent, typically four roles (background, border, solid fill, text) rather than the full range, generated in full only where the product styles status components across the whole range.

## Dark mode and switching mechanism

Reversal is a starting point, not the output. Swap semantic roles first, then hand-tune: bring vividness down (a colour confident on white reads neon on near-black), widen separation at the dark end (steps distinguishable as pale backgrounds collapse into each other as dark surfaces), and recheck every pair, since contrast is not symmetric and a passing light-mode pair can fail reversed.

Pick one switching mechanism and use it throughout the project:

- `prefers-color-scheme` alone, correct with no theme toggle.
- A `.dark` class, required once users can override the system setting.
- `light-dark()`, the least code when the project also sets `color-scheme`; it reads that property rather than a class, so a class-based toggle must set `color-scheme` too.

```css
:root {
  color-scheme: light dark;
  --color-bg: light-dark(#ffffff, #172554);
}
```

Mixing mechanisms, a media query setting some tokens and a class setting others, gives a half-themed interface the moment a user overrides their system preference.

## Neutrals

Pure grey is a perfectly good default neutral ramp. Tinting warm (toward orange, reads approachable/editorial) or cool (toward blue, reads technical/precise) is a stylistic option, not a correction; hold whichever choice across the whole ramp so a warm border never sits on a cool background. Neutrals carry the most roles in the system, so they need at least as many steps as the accent ramp, never fewer.

## Palette audit procedure

1. Grep for every colour literal: hex, `rgb(`, `hsl(`, `oklch(`, and the project's utility-class colour prefixes. Include SVG `fill`/`stroke`, chart configs and email templates; colours hide outside stylesheets.
2. Sort survivors by perceived lightness within each hue family; duplicates surface as near-identical neighbours.
3. Collapse near-duplicates: two colours closer than about one ramp step are one colour that drifted. Keep the most-used one and retire the rest. Never average two duplicates into a third value.
4. Assign each survivor a role from the token-grammar role inventory above. A colour matching no role is either a missing token or a mistake; decide which and say so.
5. Count what is left: more than one ramp per role means the palette outgrew its structure. Report the inventory before changing anything, since consolidating touches rendered output nobody asked to change.
