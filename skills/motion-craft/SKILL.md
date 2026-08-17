---
name: motion-craft
description: >
  Implement web motion, gesture physics, springs, component interaction polish,
  or name a described animation effect. Use for an implementation, gesture, or
  terminology question, not repo-wide motion audits or review verdicts.
---

# Motion craft

Before choosing a pattern, inspect the project's existing motion conventions
and its reduced-motion behaviour. Extend a coherent system; do not introduce a
new motion language for one component.

## Choose one mode

Select modes in this order: choose `terminology` for a naming-only question;
otherwise choose `gesture` whenever the request includes direct manipulation,
drag, swipe, dismissal, velocity, momentum or resistance, even when it asks to
implement; use `implement` only for the remaining motion implementation work.

### `terminology`

Use when the user asks what an effect is called or describes it without knowing
the term. Read [animation-glossary.md](references/animation-glossary.md).

Return the best exact term first, then at most two alternates with one-line
distinctions. Do not give implementation advice unless asked. If the glossary
does not contain an exact match, say so and name the closest approximation.

### `gesture`

Use for direct manipulation, drag, swipe, sheets, momentum, springs or
interruptible interactions. Read [standards.md](references/standards.md) and
[gesture-physics.md](references/gesture-physics.md).

Preserve input agency: give immediate press feedback, track directly while the
gesture is active, carry release velocity into the result, and allow reversal.
Verify keyboard parity and a reduced-motion alternative before shipping.

### `implement`

Use for motion implementation that is not principally a gesture. Read
[standards.md](references/standards.md). Also read
[component-polish.md](references/component-polish.md) only when deciding a
component's API, defaults, naming or documentation.

Start by stating the motion's purpose, frequency cost and interaction path.
Build the smallest pattern that preserves orientation, feedback or continuity;
then measure the rendered result on representative devices and states.

## Boundaries

This skill implements and names motion. Use `motion-review` for repository
audits, opportunity discovery and review findings. Use `frontend-craft` for
typography, colour and visual-system choices; use `design-foil` for broad
product or design-process critique.
