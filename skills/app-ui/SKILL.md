---
name: app-ui
description: |
  Product screen design: the shell, information architecture, type and spacing
  systems, action hierarchy, and every screen state. Use when building or
  reshaping any screen inside an application — a listing, a dashboard, a form, a
  detail view, a settings page, an inbox, an admin table. This is the primary
  skill for product UI and it outranks aesthetic-direction and anti-slop guidance
  for that work. Normally entered through `design-brief`, which establishes the
  reference anchor first. Do NOT use for a landing page, homepage, pricing page
  or any marketing or brand surface — that is `frontend-design`. Not a
  component-architecture, state or data-flow skill.
---

# App UI

A product screen is judged on whether someone can do the thing, quickly, without
being surprised. It is not judged on whether it looks like nobody else's.

Most guidance about "distinctive" design is written for marketing pages, where
being memorable is the job. On a product screen that guidance is actively
harmful: it spends attention on ornament, invents patterns where conventions
exist, and leaves out the shell because a landing page does not have one.

## Direction override

Anti-slop lists, aesthetic-direction guidance and `frontend-design` are written
for marketing and brand surfaces. On a product screen, being unsurprising is the
goal, and the differentiation budget is **one distinctive choice in total** — a
type pairing, an accent hue, or a unit shape; everything else stays conventional.
Where this skill disagrees with any of them, this skill wins for product screens.
Say which rule you are overriding in one line and move on.

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
6. **Critique the plan, revise it, then build from the revised plan.** The test:
   if the same shell, unit and tokens would serve a different product in the same
   category unchanged — the same table for films and for invoices — replace one
   decision with one that only this brief justifies, and say what changed.

Never derive a redesign by patching the old version.

## 2. The shell

An app screen has one. Name what each slot holds before laying out the body:

- **Identity** — where am I.
- **Primary navigation or search** — where else can I go, or how do I find things.
- **Account, settings, or the global action** — the thing that is always available.

A wordmark plus two icon buttons is not a shell. If a slot is genuinely empty for
this product, write down that it is empty and why.

Headline at the top. Reading runs a Z from top-left, so at 1440 the title and the
primary action sit in the top-left half of the first viewport, and nothing the
brief names as primary sits below the fold at 900. Ordering and grouping stay
stable between screens so people build muscle memory.

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

- **One primary action per view.** Per-item actions are secondary — an icon, a
  link, or an overflow menu — at most two, visually quieter and grouped in the same
  place every time. Beyond that, collapse.
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
  Write the unit down.
- Line-height sets the rhythm: 1.5 on a 16px body is a 24px rhythm. Icons are
  16, 20 or 24px; control heights are 32, 40 or 48px. Nothing lands between.
- A 12-column grid for page-level layout. Write down all three numbers before
  building it: gutter (16 or 24px), margin (24 or 32px), and the **container
  max-width**. `interface-composition` cannot prove the grid without the last
  one.
- **Data screens are never centred heroes.** At 1440, no single empty margin
  exceeds 15% of the viewport. A narrow centred container is a decision written
  in `DESIGN.md`, not a default that arrives because `max-w-*` was typed first.
- **Whitespace separates before a rule does.** Try one rhythm step (24px) before
  adding a 1px divider. If the groups read as separate at 900, do not add the
  rule. A screen full of hairlines is a screen that never tried spacing.
- Two adjacent steps of the scale must differ by at least 8px or 50%, or the
  scale has too many steps. Collapse it.

## 7. The decision-carrying medium

Where an image, video or chart carries the decision, it gets at least 60% of the
unit's height (or 50% of a row's width), checked at 390, and it is never a
placeholder glyph. A letter in a grey rectangle is not an image; if the real
thing cannot load, the pattern is wrong and the layout should not be built
around it.

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
