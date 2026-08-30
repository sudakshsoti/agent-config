---
name: design-brief
description: >
  Single entry point for design work. Establishes the project's reference anchor,
  classifies the request, loads the right skills in the right order, and runs the
  gate at the end. Use for any design ask when you do not already know which
  specific skill you want: building or reshaping a UI, a marketing page, an
  artifact, a brand, a critique, interface copy. Invoking a specific design skill
  directly is still fine and skips this router.
disable-model-invocation: true
---

# Design brief

Establish the anchor, route, build, gate. Do not answer the brief from this file.

Named `design-brief` rather than `design` because Claude Code ships a bundled
`design` skill that opens a canvas artifact. Different job; do not confuse them.

## 1. The anchor comes first, and it is a file, not a word

A named anchor carries almost nothing. "Make it feel like a repertory programme"
is an adjective wearing a proper noun, and it is how a screen ends up with no
navigation. An **image** in context is a dense brief, and it turns the work from
generation into matching, which models are far better at.

So the anchor is files on disk, per project. **No anchor is ever named in a
skill** — the skill carries the procedure, the project carries the choice.

### Once per project, committed to the repo

1. **Choose an anchor**: a shipping product, **in the same medium, doing the same
   job**. Not a printed artifact for an interactive product. Not a company you
   admire for unrelated reasons. If the screen is a listing, the anchor is
   something with a listing.
2. **Extract what can be extracted.** `npx getdesign list` offers ~70 products
   with a ready-made `DESIGN.md`; `npx getdesign add <slug>` writes it to the
   project root. Know its limit: it extracts **marketing-site** tokens, so it
   gives palette, type scale and radii, and it does not give application
   information architecture.
3. **Capture the screens.** 2–3 screenshots of that product doing the same job — a
   listing, a detail, a filter panel — into `design/reference/`, using
   `design-review/scripts/shoot.mjs`. Committed, not gitignored. **This is where
   the information architecture comes from**, and it is the half step 2 cannot
   give you.
4. **Write the brief** into `DESIGN.md` beneath the extracted tokens: what the
   screen is, what its shell carries, the reading order, the states. Then inline
   the binding rules into the project's `AGENTS.md` or `CLAUDE.md`, because a doc
   nothing auto-loads is not memory. `DESIGN.md` holds the reasoning; the
   instruction file holds the rules.

### Every UI session

The first instruction is literally: **`Read design/reference/*.png`.** Before any
plan, before any code. Then read `DESIGN.md`.

**No anchor, no build.** If `design/reference/` is empty or missing, stop and
establish it. Ask which product to anchor on, offering two or three candidates
that do the same job. Do not proceed on a description.

## 2. Classify and load

| The work is | Load, in this order |
|---|---|
| A screen inside an application | `app-ui`, then `interface-composition`, then `design-review` |
| A marketing, landing or brand page | `frontend-design`, then `design-review` |
| Type-primary: selection, pairing, scales, typesetting, font engineering | `typography-craft`, then `design-review` |
| A one-off deck, report, mockup or diagram | `artifact-design` |
| Identity, naming, positioning, brand system | `brand-studio` |
| Strategy, product critique, audit, journey map, teardown | `design-foil`, or `vbc-design` for US healthcare |
| Interface copy at length | `ux-writing` |
| Charts and data visualisation | `dataviz` |

Load only what the row names. A strategy skill cannot change pixels; loading one
for a layout problem spends a slot on nothing.

Order matters and is not negotiable: **the design decision comes before the
arithmetic, and both come before the typesetting.** Composition failures are
invisible in a palette and survive any amount of type work.

## 3. Which doctrine wins

Product screens and marketing pages want opposite things. A landing page should be
memorable; a product screen should be unsurprising. When both kinds of guidance
are loaded, `app-ui` wins for application screens and `frontend-design` wins for
marketing surfaces. Name the rule being overridden in one line rather than
silently picking.

## 4. Run the gate

Every visual deliverable finishes in `design-review`, against a render at
390 / 900 / 1440 **and** the project's reference images. Not done until P0 is zero
and the comparison question can be answered honestly.

## Boundaries

Not a code-quality, component-architecture, state or data-flow skill. A task that
touches React, Vue or Svelte is not by itself a design task.
