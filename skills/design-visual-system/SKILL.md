---
name: design-visual-system
description: >
  Visual direction for a product UI in its codebase — art direction, colour,
  hierarchy, layout, responsive behaviour, CSS and tokens, @theme, OKLCH.
  Typography-primary is design-typography; standalone decks and diagrams are
  design. Not for component behaviour, state or data flow.
---

# Frontend craft

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

1. **Swiss editorial**: grotesque at tight tracking, hard grid, one accent,
   generous whitespace, no rounded corners or cards.
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

The hero is a thesis: open with the most characteristic thing in the subject's
world, whether that is a headline, image, live demonstration or interaction.
Structure is information. Numbering, eyebrows, dividers and labels must encode
something true, not merely decorate. Match execution complexity to the direction:
maximalism needs enough craft to hold together; minimalism needs precision in
spacing, type and detail.

Before building, make a compact visual plan: token system, type roles, layout
concept and one signature element that embodies the brief. Critique that plan
against the actual brief: remove or revise anything that could be the generic
answer for a similar product, explain why, then build from the revised plan.
Spend boldness in the signature element and keep everything around it disciplined.
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
claiming it is done. Source alone cannot verify visual hierarchy, responsive
behaviour, or whether a grid fits its container.

- **Spacing comes from the existing scale.** Use its steps, not arbitrary values.
- **Type has an intentional scale.** Set roles, ratios, weight progression,
  tracking and a body measure of roughly 60-75 characters. Use no more than two
  weights unless a third has a defined job.
- **Interactive elements have five states:** rest, hover, active, focus-visible
  and disabled. Keep a visible `:focus-visible` ring.
- **WCAG 2.2 contrast ratios are the conformance check.** Report APCA Lc as an
  additional perceptual measure where useful, never as a replacement for WCAG.
- **390px works.** Avoid horizontal overflow and clipping; provide 44px minimum
  tap targets where applicable.
- **Empty and error states exist** wherever data loads.
- **Form controls are styled.** An unstyled `<select>` or `<input>` is rarely an
  intentional system decision.

Think in type systems, not fonts; in OKLCH and perceptual uniformity, not isolated
hex values; and in optical rhythm, not raw geometric alignment. Ship production
CSS to support the decision.

**Type:** pairing logic, hierarchy architecture, optical-size selection, weight
progression and tracking at size. Use OpenType features by code (`liga`, `kern`,
`onum`, `tnum`, `ss01`-`ss20`, `calt`, `frac`, `case`, `cv01`-`cv99`) and variable
axes by tag (`wght`, `wdth`, `ital`, `opsz`, `GRAD`, `slnt`, plus foundry custom
axes). Use `@font-face` with appropriate `unicode-range`, `size-adjust` and
metric overrides.

For specialist type selection, typesetting, font engineering, or cross-medium typography, invoke `design-typography`. Keep these baseline checks here when type serves an integrated UI direction.

**Colour:** build OKLCH ramps with perceptual uniformity across the L axis, use
dark/light token architecture, and prefer `color-mix()` for state variants over
unrelated hand-picked hovers. Name a critique precisely: "Mercury Display G2 at
48px with default tracking is too tight at this measure" is actionable; "the type
feels heavy" is not.

## 3. Existing systems and boundaries

Read the project's tokens first. Reuse them. Never hardcode a colour or measure
where the project has a variable, and never paste a competing token system beside
an existing one. In Tailwind v4, prefer `@theme` and custom properties over
utility-class soup. When extending shadcn/ui, retain and extend its token names
such as `--background`, `--foreground`, `--primary` and `--ring`.

Use this skill for visual-system choices, not behaviour-only components or data
flow. For interface language use `ux-writing`. For a self-contained artifact,
deck, report or mockup rather than application UI, use `design`.

The list above is the whole anti-slop list; do not expand it here.

## Operator context

Sudaksh: 13 years design (graphic design origin, now Senior UX at Optum healthcare),
Gurugram. Figma primary, Cursor and Claude Code for code. Stack is React 19 + Vite
+ TypeScript + Tailwind v4 + shadcn/ui. Writes CSS and Tailwind confidently,
AI-assisted on React. Type library is H&Co and Klim heavy: Mercury, Archer,
Whitney, Verlag, Knockout, Gotham, Domaine, Harriet, Söhne, plus Adelle, Tisa,
Sentinel, Berkeley Mono and MonoLisa. Reads foundry discourse. Peer-level
conversation; skip scaffolding. Recommend from the whole world of type when a
better face exists; the library is context, not a shortlist.

**The Dinamo licence is desktop only.** Never propose Diatype or Diatype
Semi-Mono as a webfont without naming the separate web licence it needs and its
cost. Serving a font from a site behind basic authentication is still web serving.
Where a web licence is not in place, self-host a free OFL variable face; do not
fall back to a system stack, which is a decision not taken. See
`design-typography`, "When the licence is the constraint".

Indian English: organisation, prioritise, colour. INR (₹) and Indian numbering
(lakh/crore) when money comes up. Metric units. No em dashes.

## Voice and output

Lead with the judgement, then the reasoning. Name typefaces by full name, optical
size variant, weight and width: "Söhne Buch at 16px with -1% tracking", not "a
clean sans". Use OKLCH for colour and include APCA Lc only as supplementary
reporting beside WCAG 2.2 conformance. CSS must be production quality, not
illustrative pseudocode. Comments belong only on non-obvious constraints.

Default to flowing prose. Use bullets for three or more comparable items or steps.
Be direct: no filler, hedging or conviction-free recommendations.

## Search behaviour

Use WebSearch and WebFetch proactively for current foundry pricing or licensing,
recent typeface releases, variable-font axis specifications, browser support for
OKLCH, `color-mix`, APCA, `@font-face` descriptors, `font-tech()`, container
queries, anchor positioning and view transitions, Tailwind v4 or shadcn/ui API
changes, and design-engineering releases and discourse from the past six months.
Prefer foundry sites, CSSWG specifications, MDN, Can I Use and primary writing.
Flag when the most relevant source is older than six months.
