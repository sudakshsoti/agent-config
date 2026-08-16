---
name: studio
description: |
  Build a standalone HTML artifact — a document or a landing/overview page — against
  one of four named design directions, then render it at 390 and 1440, score it, and
  revise before handing it over. Use when the user asks for "a report", "write this
  up", "a brief", "an explainer", "as HTML instead of markdown", a landing page, a
  one-pager, or types /studio. Directions: editorial (light, two families, no negative
  tracking), instrument (white ground, one accent, bordered cards, zero shadow),
  product-dark (near-black, alpha-tint elevation, hairline borders), calm (warm ground,
  one family, flat colour fields, large radii). Asks which direction, or suggests one.
  For typeface selection, typesetting, print or brand identity use typography-craft;
  for motion use motion-craft; for React/Tailwind/shadcn app UI use shadcn — studio
  builds one self-contained HTML file, not application UI.
user-invocable: true
---

# Studio

Studio builds one self-contained HTML file against a named design direction and
proves it by rendering it. Two artifact shapes: `document` (a report, brief or
explainer, read start to finish) and `page` (a landing or overview page, browsed
rather than read). Not application UI — React, Tailwind and shadcn work belongs
to `shadcn`.

## Hard rules

1. **One file.** All CSS inline in one `<style>`. No `<script src>`, no remote
   images, no build step. A remote webfont `<link>` is allowed and the check
   script WARNs on it; base64-embedding the subset `woff2` is better for
   anything shareable.
2. **Never invent data.** No placeholder metrics, no illustrative sparkline, no
   lorem, no fake testimonial, no rounded-up figure. If a number is not in the
   source, it is not in the artifact.
3. **Never rewrite the source.** Reorganise into headings, tables and callouts
   freely; preserve code, links, citations, dates, numbers and names
   byte-for-byte. The layout never wins an argument against the content.
4. **Tokens come from the direction.** Copy `directions/<name>/tokens.css`
   into the `<style>` block unedited and author every rule below it against
   those custom properties. A hardcoded colour or size that a token already
   covers is a bug.
5. **Visual complexity follows informational complexity.** A 400-word note
   gets a header and prose and nothing else. A TOC past roughly six sections.
   Stat blocks only for measured numbers.
6. **Update in place.** If the output file exists, `Edit` it. Regenerating
   discards the operator's own edits.
7. **The gate is not optional and never delegated.** Phase 3 runs in the main
   agent. A subagent's Playwright launch fails with sandbox `EPERM`. Never
   claim a pass that was not observed.

## Directions

| Direction | Ground | Character | Suits |
| --- | --- | --- | --- |
| `editorial` | light paper | two families, no negative tracking, almost no radius | long reads, essays, explainers, reports |
| `instrument` | white | one grotesque, one accent, bordered cards, zero shadow | pricing, comparisons, technical product pages |
| `product-dark` | near-black | alpha-tint elevation, white-alpha hairlines, tight tracking | developer tools, dashboards-as-marketing |
| `calm` | warm off-white | one family, large flat colour fields, large radii | consumer, wellbeing, onboarding, anything friendly |

**There is no default.** Ask which direction. If the operator does not care,
suggest one from the "Suits" column and name the reason in one line. (Kohra
becomes the default later; it has no type scale, spacing, radius or surface
ladder yet.)

The full spec for a direction is `directions/<name>/DESIGN.md`, read in Phase 1.

## Artifact shapes

Rules that do not change between directions, stated once here rather than
four times in the `DESIGN.md` files:

- `document`: one `h1`, no hero, measure constrained by `--measure`, a
  `@media print` block, primitives from the document vocabulary. It is read
  start to finish by someone who already wants the content.
- `page`: one `h1` in the masthead or hero, full-width sections allowed,
  prose still constrained to `--measure`, no print block required.
- Both: `lang` on `<html>`, `<meta charset>`, `<meta name="viewport">`, a
  non-empty `<title>`, a visible `:focus-visible` ring, 44px minimum tap
  targets, no horizontal overflow at 390, WCAG 2.2 contrast as the
  conformance check with APCA Lc only as supplementary reporting.
- Interactive elements carry five states: rest, hover, active, focus-visible,
  disabled.
- Diagrams are inline SVG or nothing. No mermaid — a bare browser opening a
  local file has no renderer for it.

## Workflow

**Phase 0 — Brief.** In one message: state the inferred shape and output
path, ask which direction (or propose one), and ask the font question
verbatim: *"Free fonts (safe to share) or your licensed set (this machine
only)?"* with free pre-selected. At most those two questions, then proceed.
Completion: shape, direction, font mode and output path all fixed.

**Phase 1 — Read.** Read `directions/<name>/DESIGN.md` and
`directions/<name>/tokens.css`, then `references/anti-patterns.md`, then the
matching half of `references/vocabularies.md`. Read `references/fonts.md`
only if the operator chose the licensed set or asked for a face the
direction does not name. Completion: the direction's avoid-list is in
context before any markup exists.

**Phase 2 — Build.** Write the file: `tokens.css` inline first, then the
artifact. Completion: the file exists and declares no colour or size the
tokens already cover.

**Phase 3 — Gate.** Both commands, in the main agent:

```bash
STUDIO="$(ls -d ~/.claude/skills/studio ~/.agents/skills/studio 2>/dev/null | head -1)"
bash "$STUDIO/scripts/render.sh" <output.html>
python3 "$STUDIO/scripts/check.py" --shape <document|page> <output.html>
```

Read all three screenshots. Score out of 100: 40 universal (five criteria at
0-8 each — hierarchy, measure and vertical rhythm, colour discipline,
integrity at 390, zero anti-pattern hits) and 60 for the direction's
avoid-list, scored `60 × (items respected ÷ items in the list)`. The
avoid-list carries the larger weight on purpose: the universal rubric is
what makes everything average. Completion: a number, and `check.py` exit 0
or its failures named.

**Phase 4 — Revise once.** Below 80, or any `check.py` FAIL: fix, re-run
both commands. On a second failure ship the file and name every failing
check and the score out loud. A silent pass is the one failure nobody can
see. Completion: second gate run recorded.

**Phase 5 — Hand off.** Absolute path, the `open <path>` command, the
direction used, the score, and anything the vocabulary could not represent.
Nothing committed, nothing staged, nothing pushed.

## Anti-scope

Never commit, stage or push. No content generation — this skill formats and
designs, it does not research or draft. No multi-file output. No publishing
to claude.ai. React/Tailwind/shadcn app UI is not a studio artifact.

## Routing

Typeface selection, typesetting, print, brand identity, display type →
`typography-craft`. Motion, gestures, springs → `motion-craft`; motion audits
→ `motion-review`. Interface copy → `ux-writing`. Product/design strategy and
critique → `design-foil`. Several genuinely different versions behind a
picker → `prototype`. A guide to a repo → `orient`. A session handoff →
`handoff`. Component library work → `shadcn`.

## Operator context

Sudaksh: 13 years design (graphic design origin, now Senior UX at Optum
healthcare), Gurugram. Figma primary, Cursor and Claude Code for code. Stack
is React 19 + Vite + TypeScript + Tailwind v4 + shadcn/ui. Writes CSS and
Tailwind confidently, AI-assisted on React. Peer-level conversation; skip
scaffolding. Type library is only what `references/fonts.md` actually
inventories as held — not a foundry wishlist.

Indian English: organisation, prioritise, colour. INR (₹) and Indian
numbering (lakh/crore) when money comes up. Metric units. No em dashes.

## Voice

Lead with the judgement, then the reasoning. Name typefaces by full name,
optical size variant, weight and width: "Söhne Buch at 16px with -1%
tracking", not "a clean sans". Use OKLCH for colour and include APCA Lc only
as supplementary reporting beside WCAG 2.2 conformance. CSS must be
production quality, not illustrative pseudocode. Comments belong only on
non-obvious constraints. In a document the voice is the source's voice: no
added introduction, no conclusion restating the body.
