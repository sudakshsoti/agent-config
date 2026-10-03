---
name: design-visual-system
description: "Use for visual direction in a product UI: art direction, colour, hierarchy, responsive layout, CSS tokens, `@theme`, and OKLCH, while first classifying the surface intent. It owns visual system decisions; use design-typography for typography-primary work and design-interface for behaviour and states."
---

# Design visual system

Two jobs, in order: make a direction specific to the subject, then execute it
with real type, colour and token systems rather than defaults.

**Arrangement comes first and is not this skill's job.** Run
`design-interface` before this one on any screen that repeats a unit,
compares records, or carries per-item controls. A composition failure is invisible
in a palette and survives any amount of colour and type work.

## 1. Ground the direction before markup

Before writing code, state one sentence naming the concrete subject, audience,
and the page's single job. Then name the direction and one thing the page does
that a template would not. "Independent watchmaker, collectors comparing movements,
make provenance legible through a technical editorial catalogue" is grounded.
"Clean and modern" is not.

Derive the direction from the subject's materials, instruments, artefacts and
vernacular. Do not choose an aesthetic by chance, and do not treat the following
as a finite menu. They are labelled examples to adapt when they fit the actual
brief:

1. **Swiss editorial**: grotesque with restrained, proofed spacing, hard grid,
   one accent, generous whitespace, no rounded corners or cards.
2. **Warm print**: serif display over sans body, ragged-right, off-white ground
   and ink-black text.
3. **Technical**: monospace accents, dense tables, hairline rules, near-monochrome
   with one signal colour.
4. **Soft product**: generous radius, layered elevation, muted palette and high
   whitespace.
5. **High contrast dark**: near-black ground, one saturated accent, bright text
   and borders as light hairlines rather than shadows.
6. **Compact utility**: dense small type, tight rows and low chrome for repeated
   daily use.
7. **Display-led**: one very large type element carries the page while the rest
   stays quiet and small.
8. **Muted archival**: desaturated palette, old-style figures, generous leading
   and restrained colour.

Opening hierarchy follows the surface’s job. A marketing or brand surface may
use a hero when positioning is the first task. On a reference, utility, dashboard,
settings, or lookup-documentation surface, do not use a positioning-led opening
block that delays the primary task. Open with task-bearing controls, data, or
content, and spend distinctiveness inside that working structure rather than
above it. A compact status or task summary is allowed only when it directly
changes the user’s next decision and the viewport budget still passes.
“Display-led” is available only when the classified reading job supports display
reading; “compact utility” is the default direction for repeated scan-and-act
use, not merely one style option.

Structure is information. Numbering, eyebrows, dividers and labels must encode
something true, not merely decorate.

Begin reference, utility and dashboard surfaces with a solid background. Add
texture, grids, patterns or translucent layering only when they encode information
or come directly from the subject. Never place a repeating pattern beneath dense
text, diagrams, tables or hairline rules. Test the design with the decoration
removed; if comprehension and identity do not suffer, leave it removed. During
visual review, check whether backgrounds compete with text, decorative rules
compete with structural rules, nested panels multiply boundaries, colour lacks
semantic meaning, or translucent layers expose distracting content underneath.

Before building, make a compact visual plan: token system, type roles, layout
concept and one signature element that embodies the brief. Critique that plan
against the actual brief: remove or revise anything that could be the generic
answer for a similar product, explain why, then build from the revised plan.
Use deliberate, real content; never use filler copy or invented metrics to prop
up a composition.

### Never ship these by default

- A purple-to-blue gradient, three feature cards, or a cream/serif/terracotta
  treatment standing in for a subject-specific decision.
- Uniform border radius, emoji iconography, decorative numbered markers, or
  shadows where nothing is elevated.
- A centred 1200px container with no other layout idea.
- Filler such as "seamlessly", "effortlessly", "powerful", "beautiful",
  "elevate", "unlock" or "supercharge".
- Three-item lists purely for rhythm, or invented statistics.

## 2. Production visual system

Render it and look at the render at 390, 900 and 1440 CSS pixels wide before
claiming it is done. At `390 × 844`, report the top coordinate of the first useful
unit and the number of complete useful units in the first viewport for every
non-marketing surface. A polished header does not count as useful content. Source
alone cannot verify visual hierarchy, responsive behaviour, or whether a grid fits
its container.

- **Spacing comes from the existing scale.** Use its steps, not arbitrary values.
- **Type has an intentional scale.** Set roles, ratios, weight progression,
  tracking and a body measure of roughly 60-75 characters. Use no more than two
  weights unless a third has a defined job.
- **Interactive elements have five states:** rest, hover, active, focus-visible
  and disabled.
- **Accessibility and state thresholds belong to `skill://design-interface`.**
  For focus indicators, contrast ratios, 390px reflow, tap-target size and
  empty or error states, read it and apply its thresholds; do not restate them here.
- **Form controls are styled.** An unstyled `<select>` or `<input>` is rarely an
  intentional system decision.

Ship production CSS to support the decision.

`references/` holds the concrete values behind these checks: `surfaces-and-icons.md`
for radius, shadow-as-border and icon mechanics, `colour-systems.md` for ramp
formation, token grammar and APCA thresholds, `layout-mechanics.md` for
spacing and adaptivity measurements, and `motion-values.md` for the numeric
overrides to the vendored `animate` and `emil-design-eng` skills.

**Type:** pairing logic, hierarchy architecture, optical-size selection, weight
progression and tracking at size. Use OpenType features by code (`liga`, `kern`,
`onum`, `tnum`, `ss01`-`ss20`, `calt`, `frac`, `case`, `cv01`-`cv99`) and variable
axes by tag (`wght`, `wdth`, `ital`, `opsz`, `GRAD`, `slnt`, plus foundry custom
axes). Use `@font-face` with appropriate `unicode-range`, `size-adjust` and
metric overrides.

For specialist type selection, typesetting, font engineering, or cross-medium typography, invoke `design-typography`. Keep these baseline checks here when type serves an integrated UI direction.

**Colour:** build OKLCH ramps with perceptual uniformity across the L axis, use
dark/light token architecture, and prefer `color-mix()` for state variants over
unrelated hand-picked hovers. Name a critique precisely: "Söhne Buch at 16px/1.5
with tracking 0 is too dense at this measure" is actionable; "the type feels
heavy" is not.

## 3. Existing systems and boundaries

Read the project's tokens first. Reuse them. Never hardcode a colour or measure
where the project has a variable, and never paste a competing token system beside
an existing one. In Tailwind v4, prefer `@theme` and custom properties over
utility-class soup. When extending shadcn/ui, retain and extend its token names
such as `--background`, `--foreground`, `--primary` and `--ring`.

Use this skill for visual-system choices, not behaviour-only components or data
flow. For a self-contained browser artifact, use this skill together with `design-typography` and `design-interface` as needed. The former `frontend-artifact` entry point is deprecated and archived.

The list above is the whole anti-slop list; do not expand it here.

## Operator context

Sudaksh: 13 years design (graphic design origin, now Senior UX at Optum healthcare),
Gurugram. Figma primary, Cursor and Claude Code for code. Stack is React 19, Vite,
TypeScript, Tailwind v4, and shadcn/ui. Writes CSS and Tailwind confidently,
AI-assisted on React. Type library is H&Co and Klim heavy: Mercury, Archer,
Whitney, Verlag, Knockout, Gotham, Domaine, Harriet, Söhne, plus Adelle, Tisa,
Sentinel, Berkeley Mono and MonoLisa. Reads foundry discourse. Peer-level
conversation; skip scaffolding. Recommend from the whole world of type when a
better face exists; the library is context, not a shortlist.

**Web licences and font fallbacks.** Before proposing a desktop-licensed face (for
example Dinamo Diatype) as a webfont, or a system stack as the final answer, read
`skill://design-typography`, "When the licence is the constraint".

Match the product's market locale for spelling, currency and number format. No
em dashes.

## Voice and output

Lead with the judgement, then the reasoning. Name typefaces by full name, optical
size variant, weight and width: "Söhne Buch at 16px/1.5 with tracking 0", not "a
clean sans". Use OKLCH for colour and include APCA Lc only as supplementary
reporting beside WCAG 2.2 conformance. CSS must be production quality, not
illustrative pseudocode. Comments belong only on non-obvious constraints.

Use bullets for three or more comparable items or steps.

## Search behaviour

Use web search and fetch proactively for current foundry pricing or licensing,
recent typeface releases, variable-font axis specifications, browser support for
OKLCH, `color-mix`, APCA, `@font-face` descriptors, `font-tech()`, container
queries, anchor positioning and view transitions, Tailwind v4 or shadcn/ui API
changes, and design-engineering releases and discourse from the past six months.
Prefer foundry sites, CSSWG specifications, MDN, Can I Use and primary writing.
Flag when the most relevant source is older than six months.
