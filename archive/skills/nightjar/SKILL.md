---
name: nightjar
description: >
  NIGHTJAR house style — the visual language for one-off generated artifacts:
  decks, dashboards, documents and reports, mockups, diagrams and infographics.
  Use whenever producing or publishing an artifact, an HTML page, a deck, a
  dashboard, a mockup, a report, a chart or a diagram, and whenever the user
  says "nightjar", "house style", or "our usual style". Supplies surfaces,
  accent, status colour, type, spacing, controls, per-artifact rules and a
  self-check. For a product UI's own living visual system in its codebase — its
  tokens, CSS and component styling — use `frontend-craft` instead. Pairs with
  `artifact-design`, which decides how much design a request warrants; Nightjar
  decides what it looks like. Not a code-quality, component-architecture or
  copywriting skill.
disable-model-invocation: true
---

# NIGHTJAR — house style

The style specification for generated design artifacts. It governs every deck,
dashboard, prototype, document, and diagram produced in this house.

The intent is to escape default-LLM visual output: gradient hero backgrounds,
Inter, purple-to-pink washes, rounded cards with a left accent border, emoji
bullets, drop shadows everywhere, three-column feature grids with icons in
circles. None of that appears in Nightjar.

Nightjar is derived from four observed systems: Linear (structure, density, icon
language), Resend (restraint, mono discipline), Fey (numerals, data panels),
Chronicle (card strategy, radius discipline). It is not a clone of any of them.

**How to read this spec:** rules and ratios bind; specific hex values are a
reference implementation, not a mandate. When a rule and a hex conflict, follow
the rule. Every value marked `ref` is one valid answer, not the only one.

**Precedence, when two rules disagree:** the rejection list wins over
everything. Per-artifact rules win over the general sections. A rule wins over a
`ref` value. Where the medium cannot carry a rule at all — no CSS, no hover, no
viewport — state that in one line and stop. Do not substitute an invention.

## Applying this

The rules are short; guessing which one applies is what produces default output.

Order of work:

1. **Read `references/spec.md`.** All of it, once, before deciding anything.
2. **Name the artifact class** — deck, dashboard, app UI, document, or diagram.
   §10 opens with a matrix saying which rule families bind for that class. A
   family marked `n/a` has no target in that medium; it is not permission to
   improvise.
3. **Declare the tokens first** for dashboards and app UI, before any component.
   Everything downstream references them by name.
4. **Write the artifact.**
5. **Walk `references/self-check.md`** line by line before returning. Walk it,
   do not paraphrase it.

Alongside the `Artifact` tool: load `artifact-design` for how much design the
request warrants, then apply Nightjar for what it looks like. Where they
disagree on appearance, Nightjar wins. Where they disagree on effort or format,
`artifact-design` wins.

When the user asks for something this spec forbids, name the rule it hits in one
line and offer the nearest compliant version. Do not silently comply, and do not
silently refuse.

---

## 1. The one-paragraph brief

Neutral dark grey, never pure black. Containers earn their edge by a fill step,
not by a border or a shadow. One cool accent, used only for selection and focus.
Two type families with a strict division of labour: humanist sans for language,
monospace for machine output. Density comes from row count, not from tightness.
Nothing glows, nothing gradients, nothing floats.

---

## Where the rest lives

Two reference files. Both are read in full, not skimmed.

- **`references/spec.md`** — §2 surfaces, §3 accent, §4 status and data colour,
  §5 type, §6 space and radius, §7 iconography, §8 controls, §9 light
  counterpart, §10 per-artifact rules. **Read before writing any markup.** §10
  opens with the capability matrix naming which families bind for the artifact
  class in hand.
- **`references/self-check.md`** — §11 rejection list and §12 self-check. **Read
  and walk this before returning the artifact.**

Section numbers are stable across both files, so a `§5` or `§12` reference in
either one resolves as written.
