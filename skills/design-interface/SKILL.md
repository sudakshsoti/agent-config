---
name: design-interface
description: "Use when designing or reviewing interactive controls, forms, lists, dashboards, settings, documentation, or non-happy-path screen states: structure, labels, focus, hit areas, field states. Not for marketing or brand pages (frontend-design), type scale (design-typography), or visual styling (design-visual-system)."
---

# design-interface

Styling of a control comes from `design/decisions.md`; this skill owns structure, behaviour, states and the accessibility thresholds below.

## When to invoke

Building or reviewing any interactive control, form, list, or a screen that has states beyond the happy path.

## Inputs to inspect

- The rendered surface at keyboard focus, walking tab order.
- Every control's disabled, loading and error variant, not just default.
- Real content at its extremes: empty list, one item, an overfull list, the longest realistic string.
- The DOM/accessibility tree, not just the visual render.

## Surface intent gate

Before layout, write one line with: `class | primary job | new or repeat use | scan or read | narrowest viewport`. If the class is unclear, infer it from the task and existing product context; ask only when two classes imply materially different structures.

Marketing/brand may spend the opening viewport on positioning. Reference/lookup-documentation, task utility, dashboard/data, and settings/form surfaces spend it on use. Tutorials, essays, and sequential guides classify as content/editorial rather than lookup documentation. On a repeat-use surface, onboarding and explanation move out of the normal path unless they are needed to prevent an error.

## Surface layout

- For reference/lookup-documentation, utility, dashboard, and settings surfaces at `390 × 844` CSS pixels, the first task-bearing control, data region, setting group, or reference entry starts within the top 40% of the viewport, and at least one complete useful unit is visible without scrolling. Verify from the rendered bounding boxes.
- Count every block before the first useful unit. Identity/navigation needed for wayfinding may precede it; promotional copy, a restatement of the page purpose, duplicate prefix/key explanations, and generic “Start here” panels may not. Any other pre-content block must name the user error or decision it prevents.
- A screen needs an accessible name, not automatically a large visible heading. If the shell, title bar, or navigation already names the current view, do not repeat it as a display heading. If a visible heading is needed, size it within the compact UI scale unless the surface is marketing/brand or content/editorial and display treatment serves the reading job.
- First-run help is a state, not permanent page furniture. Verify the repeat-use state separately and confirm learned guidance no longer pushes the primary task down.
- For frequently used surfaces, state a viewport utility target: which task-bearing units must be fully visible at the narrowest target width and height. Render and count them before completion.

## Focus and keyboard

- Every interactive element has a visible focus indicator reachable by keyboard alone, drawn with `:focus-visible`; an outline is never removed without a replacement indicator. Verify by focusing every interactive element by keyboard and diffing its computed outline, box-shadow and border against its resting state.

## Read the branch reference

Read only the file for the branch the surface reaches, before building or reviewing that part:

- Forms, labels, validation, submit, error copy → `references/forms-validation.md`; field attributes (`autocomplete`, `inputmode`, `type`) → `references/form-attributes.md`.
- Toasts, status messages, `aria-live` → `references/live-regions-toasts.md`.
- Dialogs, drawers, sheets, grids, trees, listboxes, menus, hidden content, focus-ring colour, skip link → `references/focus-dialogs-composites.md`.
- Disabled, loading or unavailable controls → `references/disabled-state.md`.
- Tap/click target size, text and boundary contrast, 320px reflow → `references/target-contrast-reflow.md`; undersized-target exceptions → `references/target-size-exceptions.md`.
- Loading, skeletons, spinners, progress (a control acknowledges a press within 100ms) → `references/loading-states.md`.
- Offline, over-quota, logout, permission-denied, stale states → `references/state-qa.md`.
- Tooltip, popover, badge, tag, sheet, or other easily confused components → `references/component-confusables.md`.
- Long lists (density register), headings, hover, z-index, navigation labels, wayfinding, feedback kinds → `references/layout-navigation-feedback.md`.

## Escalation triggers

These are review thresholds this skill owns — `vibe` and other review flows defer to this list rather than re-deriving it. Any one of them is a blocker on sight, whatever else the change gets right:

- An interactive control with no accessible name.
- A keyboard-reachable control with no visible focus indicator.
- Content or a control clipped, overlapped, or unreachable at 320px width or 200% zoom.
- State or meaning carried by colour alone.
- A destructive action with neither confirmation nor undo.
- An error that names no way to recover from it.
- A semantic colour used against its meaning, such as a danger hue on a non-destructive action.
- A state change signalled only by motion, with no colour, icon, or label left behind when the animation does not run.

## States nobody demos

Walk the surface against these twelve recurring states before calling it done: loading, empty, partial, error, offline, permission-denied, stale, over-quota, maintenance, onboarding, power-user, sync conflict. This is a checklist, not a rule list; it carries no verify clauses.

## Completion

Done when every rule that applies has been applied and its verify step run, with the results listed in the reply.
