# Artifact essentials

The rules from `design-typography`, `design-interface` and `design-visual-system` that apply to a standalone page, condensed so they fit in one read. Load the full skills only when the artifact has forms, dialogs, composite widgets or a long-lived product context; for a static or lightly interactive document this sheet is enough. Values in bold are the ones `audit.js` measures.

## Start from the skeleton

Copy `skeletons/<language>.html`. Fill the `REPLACE` slots with the real content. Change a token only with a reason you can state in the report ("body at 17px because the content is dense tabular prose"). Do not add a token the skeleton lacks until the content needs it. Delete any skeleton block the content does not use; an empty callout or an unfilled aside is worse than none.

## Type

- One typographic thesis in a sentence: subject, reader, reading conditions, intended character. Every choice below serves it.
- Roles, not sizes: body, small (meta, caption, label), heading, title. Give each role a size, weight and colour once, in tokens, and reuse them.
- **Body 16 to 20px** on a reading page, **14 to 16px** on a utility. **Line-height 1.4 to 1.6** for body. Compact UI rows may use 1.3 to 1.45.
- **Measure 50 to 75ch** for prose. Set `max-width` in `ch` on the prose container, not in pixels.
- **H1 no more than 3.2 times body** on a reading page and **1.6 times on a utility**. Contrast between roles comes from weight, colour and spacing before size.
- `font-kerning: normal`, `letter-spacing: 0` on mixed case. Positive tracking only on a few proofed uppercase labels. **No negative tracking under 24px.**
- Mono is for code, identifiers, values and logs. Not for headings, prose or labels.
- Tabular figures (`font-variant-numeric: tabular-nums`) wherever numbers align in columns.
- Two families at most; a third only as a mono. Pairings and validated links are in `fonts.md`.

## Colour

- Tokens by role: ground, ink, ink-soft, rule, one accent, and semantic status colours only if the page has status. Name the accent by what it means on this page.
- **Body text contrast at least 4.5:1**, 7:1 preferred. Small metadata is still text and still needs 4.5:1. Faint grey is not hierarchy.
- **At most two saturated hues** unless data series need more. Data colours keep the same meaning in every figure.
- Solid backgrounds. No gradients, no textures, no translucent layers. A colour block is a category or an emphasis, never decoration.
- Light by default. Choose dark only for real reading conditions or an existing system, and then set the whole palette for it.

## Structure and spacing

- One spacing base (8px) and multiples of it. Space changes where the content changes; equal gaps everywhere hide the structure.
- Group with alignment, rules and spacing first. A container earns a border when it is an independent object, a bounded control region or an overlapping layer. **One radius value** for controls and bounded regions; zero is a valid choice.
- **No box-shadow** on anything that is not a control, dialog or popover.
- The first useful unit comes first. On a utility, at 390×844 the first control, row or data region starts **within the top 40% of the viewport**. On a reading page the title and first paragraph are the useful unit; a hero is not.
- Headings in document order without skipping levels. The page has one `h1`. A visible title is optional when the context already says where the reader is; an accessible name is not.
- Semantic HTML: `main`, `header`, `section` with headings, `figure` and `figcaption`, `dl` for metadata, `table` for tabular data, `ul` for lists. Divs are for layout only.
- Real content only. Illustrative data is labelled as illustrative in the caption or a note. No lorem ipsum, no invented statistics, no invented quotations.

## Responsive

- Design the phone view first, then let the wide view add columns. **No horizontal overflow at 390px**; a table, diagram or wide figure that needs a second dimension scrolls inside its own container and is named as intentional in the report.
- Do not shrink a desktop composition; change its column count. Preserve the grouping, not the geometry.
- `max-width: 100%` on images and SVG; `width` and `height` attributes on `img` so nothing shifts as it loads. `alt` on every image; empty `alt` for a decorative one.

## Interaction

- Every interactive element has a visible `:focus-visible` outline and a keyboard route. Tab order follows reading order.
- Pointer targets at least 24×24 CSS px; touch targets 44×44. Grow the hit area, not the visual.
- Hover effects only under `@media (hover: hover) and (pointer: fine)`, and **never a transform on hover**.
- A control exists because the brief asked for it or because the explanation needs a variable changed. Feedback appears where the change happens, in an `aria-live="polite"` region if it is text.
- Empty, loading and error states read differently when they exist. An error names what is wrong and what to do.
- Reduced motion: any transition longer than 150ms is disabled under `prefers-reduced-motion: reduce`.

## Before the review

Run `audit.js` at 390×844 and 1440×1000 with the flag for the language (`--compact` for personal-software, precision-software and industrial-instrument; `--display` for swiss-graphic). Fix every FAIL. Explain every WARN you keep. Then answer the three questions at the end of `anti-patterns.md` and only then open the screenshots.
