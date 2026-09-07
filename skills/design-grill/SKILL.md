---
name: design-grill
description: >-
  Relentless interview on how something should look, feel and behave, round by
  round until nothing is assumed. New screens or pressure-testing decisions;
  records settlements in design/decisions.md. Technical grilling is grilling.
disable-model-invocation: true
---

Call the Skill tool for `grilling` and run its loop unchanged — the design tree, the frontier, one round of numbered questions each carrying a recommended answer, wait, recompute.

The four rules below are what make it a design grill rather than a technical one. Nothing here replaces the loop; it constrains what the tree branches on, what you look at, and what you write down.

## The tree branches on the interface

Every node is a decision about what the user of this thing sees, feels or does: purpose, who it is for, how often they come back, what they must be able to do, what it sits beside, what one screen carries the weight, density, colour, type, motion, the states nobody demos.

Architecture, data model, framework and implementation are out of scope. When a node genuinely needs one — a platform constraint that forecloses a visual option, say — settle just that fact and move on; do not let the tree drift into a technical grilling.

## Look first, when there is something to look at

Before round 1, look at the real thing. Screenshot the running app, read an image the user pasted, open a URL they gave you. Seeing it settles nodes for free — dark mode, density, type scale and containment are all visible — so the first round starts further out.

When nothing exists yet, skip this and open with questions. Never ask the user to produce a screenshot of a thing that does not exist, and never fill the gap by generating a mockup.

**Do not generate HTML, prototypes or visual comparisons unless the user asks for one in that turn.** Producing them is slow and is almost never what unblocks the frontier. Consuming visuals is cheap; producing them is not.

## Decompose every reference

A reference is one sentence carrying ten decisions. "Make it feel like Linear" left unhandled becomes eight silent inferences, which is the exact failure the `[inferred]` rule below exists to stop — arriving all at once.

Never fetch a reference's real values and copy them; that produces a clone the user never chose. Name what you think they meant, as separate attributes, and put each back as its own numbered question with its own recommended answer:

```
You said Linear. What I think you mean, as separate decisions:

❓ **Q1** - **Density**: tight vertical rhythm, rows around 32px, very little padding.
➡️ yes, this reads as the main thing you meant

❓ **Q2** - **Colour**: near-monochrome, one accent used sparingly.
➡️ yes

❓ **Q3** - **Containment**: no card borders, structure carried by spacing alone.
➡️ yes

❓ **Q4** - **Type**: one sans at two or three sizes, no display face.
➡️ probably not what you meant
```

The user almost never means the whole reference. The attributes they do *not* want are invisible until you name them.

This applies to any reference: a named app, a site, a pasted screenshot, a competitor, a past project.

## Write design/decisions.md as each decision settles

Append to `design/decisions.md` at the repo root, creating it if absent, the moment a decision settles — not at the end of the session. The user contradicts themselves often, and a file written only at the end loses the earlier position that the contradiction is worth seeing against.

Tag every line with where it came from:

```markdown
- [stated] Dark by default, no light mode. — "I only ever use dark"
- [inferred] The accent stays warm across both surfaces. Why: follows from the warm neutral base. NOT CONFIRMED.
```

**An inference never settles a node.** If an answer is derived rather than said, it does not close and the frontier does not advance past it. It becomes a question in the next round with the inference as the recommended answer. Skipping the question because you are confident is the single failure that costs the most: the wrong turn is silent, and by the time the user sees the result it is four decisions back.

**Surface contradictions out loud.** When a new answer conflicts with a settled line, quote the line, say what conflicts, and ask which holds. Never silently overwrite, and never silently keep the old one:

> Round 3 Q2 conflicts with a settled line: *"[stated] Dark by default, no light mode."* You have now said the marketing page should be light. Which holds — does the rule apply to the app only, or was it wrong?

Nothing in the file is frozen. Reopening a decision is a normal move: rewrite the line and flag what downstream of it now needs rechecking.
