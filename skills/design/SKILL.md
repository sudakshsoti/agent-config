---
name: design
description: >
  Single entry point for design work. Classifies the request, loads the right
  skills in the right order, and runs the gate at the end. Use for any design ask
  when you do not already know which specific skill you want: building or
  reshaping a UI, an artifact, a brand, a critique, interface copy. Invoking a
  specific design skill directly is still fine and skips this router.
disable-model-invocation: true
---

# Design

Route, then run. Do not answer the brief from this file.

## 1. Establish the anchor first

Before anything else, find or ask for the **reference anchor**: one real product,
site, or printed artifact whose design language this work follows.

- Read the project's `DESIGN.md` if it has one. If it names an anchor, use it and
  say which. Do not re-derive a direction that is already recorded.
- If there is no anchor, ask for one in a single question, offering two or three
  candidates grounded in the subject's own world: what the subject's practitioners
  actually read, print, or use.
- Record the answer in the project's `DESIGN.md`, and inline the binding rules
  into the project's `AGENTS.md` or `CLAUDE.md`. A doc nothing auto-loads is not
  memory, so the reasoning lives in `DESIGN.md` and the rules live where the tools
  read them.

This step is why one-shots come out inconsistent between sessions. Without an
anchor the direction is re-invented each time, and the average of all design is
the thing everyone recognises as generated.

## 2. Classify and load

| The work is | Load, in this order |
|---|---|
| Product UI inside a codebase | `interface-composition`, then `frontend-craft`, then `design-review` |
| Type-primary: selection, pairing, scales, typesetting, font engineering | `typography-craft`, then `design-review` |
| One-off artifact: deck, dashboard, report, mockup, diagram | `nightjar` |
| Identity, naming, positioning, brand system | `brand-studio` |
| Strategy, product critique, audit, journey map, teardown | `design-foil`, or `vbc-design` for US healthcare |
| Interface copy, labels, errors, empty states | `ux-writing` |
| Charts and data visualisation | `dataviz` |

Load only what the row names. Loading a strategy skill for a layout problem spends
a slot on something that cannot change pixels.

Where rows overlap, the arrangement decision comes before the aesthetic one, and
the aesthetic one before the typesetting. Composition failures are not visible in
a palette and will survive any amount of type work.

## 3. Run the gate

Product UI and artifact work both finish in `design-review`, against a render at
390 / 900 / 1440. The work is not done until its P0 count is zero.

## 4. Boundaries

Not a code-quality, component-architecture, state or data-flow skill. A task that
touches React, Vue or Svelte is not by itself a design task.
