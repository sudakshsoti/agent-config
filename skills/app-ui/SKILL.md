---
name: app-ui
description: >
  Product screen design: the shell, information architecture, type and spacing
  systems, action hierarchy, and every screen state. Use when building or
  reshaping any screen inside an application — a listing, a dashboard, a form, a
  detail view, a settings page. This is the primary skill for product UI and it
  outranks aesthetic-direction and anti-slop guidance for that work. For a
  marketing or brand page use `frontend-design`; for a one-off deck or report use
  `artifact-design`. Not a component-architecture, state or data-flow skill.
disable-model-invocation: true
---

# App UI

A product screen is judged on whether someone can do the thing, quickly, without
being surprised. It is not judged on whether it looks like nobody else's.

Most guidance about "distinctive" design is written for marketing pages, where
being memorable is the job. On a product screen that guidance is actively
harmful: it spends attention on ornament, invents patterns where conventions
exist, and leaves out the shell because a landing page does not have one.

## Direction override

Anti-slop and aesthetic-direction guidance applies to marketing and brand
surfaces. On a product screen, being unsurprising is the goal, and the
differentiation budget is **one element**. Where this skill disagrees with a slop
list or an aesthetic-direction skill, this skill wins. Say which rule you are
overriding and move on.

## 1. Plan the whole screen before writing code

The single most common failure is deriving a screen by fixing defects in a
previous version. That preserves every wrong decision underneath. Plan first:

1. **Brief.** One sentence: who is here, what they are deciding, what they do
   next.
2. **Shell.** What each slot holds (below).
3. **Unit.** Row, card, table or detail, with the reason (below).
4. **Tokens.** The base spacing unit, the type scale ratio, the families, the
   palette as 4–6 named values, the two radii.
5. **Layout.** An ASCII wireframe. Draw a second, different one. Compare them
   against the brief rather than against taste.
6. **Critique the plan, revise it, then build from the revised plan.** Anything
   that would be the generic answer for any similar screen gets revised, and you
   say what changed.

Never derive a redesign by patching the old version.

## 2. The shell

An app screen has one. Name what each slot holds before laying out the body:

- **Identity** — where am I.
- **Primary navigation or search** — where else can I go, or how do I find things.
- **Account, settings, or the global action** — the thing that is always available.

A wordmark plus two icon buttons is not a shell. If a slot is genuinely empty for
this product, write down that it is empty and why.

Headline at the top. Reading runs a Z from top-left, so nothing that matters sits
below or right of the first scan. Ordering and grouping stay stable between
screens so people build muscle memory.

## 3. Choosing the unit

- **Homogeneous, sortable, comparable content → rows or a table.** Cards are the
  wrong pattern for it: they scatter comparable values to different offsets and
  repeat every label once per item.
- **A card grid earns its place** when the job is visual browsing, the item
  carries an image that drives the decision, and the card holds enough metadata to
  evaluate without opening it. All three, not one.
- **One item, many attributes → a detail view.**
- The unit itself is normally the primary click target.

State the choice with the counts that justify it: "five films compared on four
rating sources, so rows with one header."

## 4. Actions

- **One primary action per unit**, at most two secondary, visually quieter and
  grouped in the same place every time. Beyond that, an overflow menu.
- Destructive and dismissive actions never carry the affirmative action's weight.
- A form control repeated once per unit is a column, not a control. Reconsider.
- **Filters report the result count**, so the effect of a filter is visible
  without counting.

## 5. Type

- Build a **modular scale** from a 16px base at a stated ratio — 1.125, 1.25 or
  1.333. Write down which ratio and why. Sizes come off the scale, not from taste.
- **Two families is the normal answer**, paired by contrast: display against body,
  or serif against sans. One family across several weights is equally valid and
  often calmer. Three needs a structural reason, such as display, UI, and
  long-form body. **Never two families inside body copy.**
- Hierarchy comes from weight, size and colour before any ornament.
- Body measure 60–75 characters. Tabular numerals wherever figures align.
- No family choice survives without a rendered proof at the smallest and largest
  size it will actually be set at.

## 6. Space

- **One base unit**, 4px or 8px. Every padding and margin is a multiple of it.
- Line-height anchors the vertical rhythm; icon and control sizes map onto it.
- A 12-column grid with consistent gutters and margins for page-level layout.
- **Whitespace separates before a rule does.** Reach for a divider only when
  spacing has already failed. A screen full of hairlines is a screen that never
  tried spacing.
- Two adjacent steps of the scale must be visibly different, or the scale has too
  many steps.

## 7. The decision-carrying medium

Where an image, video or chart carries the decision, it gets the dominant share of
the unit, and it is never a placeholder glyph. A letter in a grey rectangle is not
an image; if the real thing cannot load, the pattern is wrong and the layout
should not be built around it.

Reserve the aspect ratio from first paint so nothing reflows when it arrives.

## 8. Every state is designed

Empty, loading, error, first-run, and the state after the user's own action. Each
occupies the populated state's region and does not shift its surroundings when it
swaps. A screen with only a happy path is half a screen.

## 9. Words are design material

- Name things by what people control, never by how the system is built. A person
  manages notifications, not webhook config.
- A control says what happens: **"Save changes", not "Submit"**. An action keeps
  the same name through the whole flow, so a button that says "Publish" produces a
  toast that says "Published".
- Errors state cause and fix, in the interface's voice. They do not apologise and
  they are never vague about what happened.
- An empty screen invites an action.
- Sentence case, plain verbs, no filler. Each element does one job.

## 10. Before handing over

Run `interface-composition` for the arithmetic — container maths, action counts,
label repetition, shared axes. It catches defects; this skill decides the design,
so it runs first and that one runs after.

Then `design-review` against a render and the project's reference images. The work
is not done until its P0 count is zero.

## Boundaries

Product screens only. A task that touches React, Vue or Svelte is not by itself a
design task. Interface copy at length goes to `ux-writing`; type-primary work goes
to `typography-craft`; marketing and brand pages go to `frontend-design`.
