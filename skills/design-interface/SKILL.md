---
name: design-interface
description: Testable rules for controls and structure — field states, focus, target size, disabled and error states, labels, hit areas, the states nobody demos, heading order. Does not cover type scale; see craft-typography. Consult when building or reviewing any interactive control or screen state.
---

# craft: interface

## Purpose and scope

Carries no opinion on visual style of a control — that comes from `design/decisions.md`.

## When to invoke

Building or reviewing any interactive control, form, list, or a screen that has states beyond the happy path.

## Inputs to inspect

- The rendered surface at keyboard focus, walking tab order.
- Every control's disabled, loading and error variant, not just default.
- Real content at its extremes: empty list, one item, an overfull list, the longest realistic string.
- The DOM/accessibility tree, not just the visual render.

## Rules (testable)

- Every interactive element must have a visible focus indicator reachable by keyboard alone. Verify by tabbing through the surface and confirming visible focus at each stop.
- Tab order must follow the visual reading order. Verify by tabbing through and comparing against the visual sequence.
- Every form control must have a programmatically associated label. Verify with an accessibility tree inspection, not by eye.
- A pointer target is at least 24 by 24 CSS pixels (WCAG 2.2 SC 2.5.8); a touch target is at least 44 by 44 (Apple Human Interface Guidelines); where a platform specifies larger, the platform governs. Target area is grown with a pseudo-element rather than by resizing the visual, and grown areas must not overlap. Verify by measuring each interactive element's bounding rectangle in the render at the target viewport, and by checking adjacent grown areas do not intersect.
- An error state must name what is wrong and, where fixable by the user, what to do about it. Verify by reading the error copy against those two criteria.
- Heading levels must not skip a level and must appear in document order. Verify with an accessibility tree or heading-outline check.
- Every control that can be disabled or loading must have a visually distinct disabled/loading state, and it must not be reachable by keyboard as if it were active. Verify by inspecting both the render and the focus behaviour.
- Text must reach a 4.5:1 contrast ratio against its background, or 3:1 where it is large scale (24px and above, or 18.66px and above when bold); any non-text boundary that conveys a control's edge or its state must reach 3:1. WCAG 2.2 SC 1.4.3 and SC 1.4.11. Decorative hairlines and dividers, which identify no control, are exempt. Verify by computing the ratio from the resolved foreground and background colours in devtools or a contrast checker, not by eye.
- A surface with a repeating row or item that will carry 50 or more entries must have its density register stated as a number — items fully visible at the target viewport height — and the render must match what was stated within one item. Verify by counting the items fully visible in the render at that viewport; where rows are uniform, dividing the scrollable viewport height by the measured row pitch gives the same answer faster. Variable-height items — cards, grouped lists, kanban columns — are counted directly rather than computed from a pitch. Where the project has no `design/decisions.md` to hold the number, state it in the reply, as with a Quick override. This rule fixes no value: any register is compliant. An unstated register, or a render that misses its own by more than one item, is not.
- A dialog, drawer or sheet that takes over the surface must move keyboard focus into itself when it opens, hold Tab inside it while it is open, and return focus to the element that invoked it when it closes. Verify by opening it from the keyboard, tabbing a full cycle and confirming focus never lands on a control behind it, then closing it and confirming focus returns. Toggling a CSS class is not opening a dialog.
- A composite widget whose rows are themselves selectable or actionable — a grid, tree grid, listbox or menu — must not place one tab stop per row. Traversal inside it is by arrow key with a single tab stop for the whole widget: a roving `tabindex`, one row at `0` and the rest at `-1`, so Tab still reaches whatever follows it. Per-row controls such as selection checkboxes sit inside that scope and are not separately tabbable. This follows the ARIA APG keyboard-interface guidance and applies only to composites. Ordinary collections of independent items — cards with their own links, chat messages, lists of links — keep their native tab stops; forcing roving focus onto those removes reachability rather than adding it. Verify by counting elements matching `a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])` within the composite: the count must not scale with the row count.
- Focus styling uses `:focus-visible`; an outline is never removed without a replacement indicator. Verify by focusing every interactive element by keyboard and diffing its computed outline, box-shadow and border against its resting state.
- Hover affordances are gated behind `@media (hover: hover) and (pointer: fine)`. Verify by emulating a coarse pointer with no hover and confirming no computed style changes on pointer-over.
- Content hidden from view leaves the tab order, via `visibility: hidden`, `display: none` or `inert`. Opacity and off-screen transforms leave it focusable. Verify by tabbing through the surface with the element hidden and confirming focus never enters it.
- Validation runs inline as the user types — soft while typing, hard on blur — rather than being deferred to submit; a failed submit still moves focus to the first invalid field. Verify by submitting an invalid form and reading `document.activeElement`.
- The submit control is not disabled until the form is valid, because disabling it removes the route to the error messages. Verify by loading the empty form and reading the submit control's disabled state.
- An invalid field carries `aria-invalid` and an `aria-describedby` pointing at its message. Verify in the accessibility tree, not the DOM.
- A status region is `aria-live="polite"`; `assertive` is for errors only. Verify in the accessibility tree.
- A decorative image carries an empty `alt`, not a missing one. Verify in the accessibility tree: a missing alt exposes the filename.
- Empty and error are different states and must read differently. Verify by rendering both and diffing their text content.
- A composite of interactive elements uses a documented z-index scale or `isolation: isolate`, not ad-hoc values. Verify by listing every non-auto computed z-index on the surface and checking each against the declared scale.
- Content must reflow to a 320 CSS pixel viewport width without horizontal scrolling, except for parts that need a second dimension to be usable — a data table, a map, a diagram, a toolbar that must stay in view (WCAG 2.2 SC 1.4.10). Where such a part exists, its horizontal scroll is confined to its own container and named as intentional in the reply or in `design/decisions.md`. Verify by rendering at 320px wide with the longest realistic string in place, comparing `document.documentElement.scrollWidth` against its `clientWidth`, and confirming every element whose own `scrollWidth` exceeds its `clientWidth` is one of those named exceptions.
- Feedback comes in four kinds — status, completion, warning, error — and a surface names which kind each feedback event on it produces (Apple Human Interface Guidelines — feedback foundations). Verification: list every feedback event on the surface and confirm each maps to one of the four kinds.
- Every screen answers four wayfinding questions: where am I, where can I go, what is there, and how do I get out (Apple Human Interface Guidelines — navigation foundations). Verification: point at the element answering each of the four on the render; a screen with no exit is a defect.
- A control sits adjacent to what it affects, and proximity encodes the relationship (Apple Human Interface Guidelines — layout foundations). Verification: name the affected element for each control and measure its distance to that element against its distance to the nearest unrelated control; a control that needs a label to explain what it changes has weak mapping.
- A navigation label names its own contents, not an umbrella term (Apple Human Interface Guidelines — navigation foundations). Verification: read each nav label, name what is actually behind it, and confirm a label that could equally sit above any other section fails.

## States nobody demos

A checklist, not a rule list — it carries no verify clauses. Twelve states recur across the source material with zero baseline projects behind the claim yet: loading, empty, partial, error, offline, permission-denied, stale, over-quota, maintenance, onboarding, power-user, sync conflict. Walk a surface against this list before calling it done.

## Open questions / to be evidenced

- Which empty/overflow states recur often enough across projects to deserve a named checklist rather than a general reminder? The twelve-state list under "States nobody demos" is imported unevidenced — which of these recur in real baseline work?
- How much keyboard-order divergence from visual order is tolerable before it counts as a failure, and does that differ by control type?
- What is the right verification method for "long realistic string" — a fixed stress string, or content pulled from the real project?

Measured thresholds, worked examples and cited sources go in `references/` — see `references/README.md`.

## Anti-patterns

- Reviewing only the default, populated, happy-path state.
