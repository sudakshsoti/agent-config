# editorial

## Thesis and fit

**One screen-first reading system keeps prose stable while evidence changes form around it.**

This direction supports reports, essays, culture writing, and data journalism through sustained prose, comparison tables, figures and captions, annotations, and measured data. It does not create separate density presets. The reading system stays stable; the evidence mode changes around the reading column.

Use it when a reader needs to stay with an argument, inspect its evidence, or move between prose and data without changing the page's basic grammar. Do not use it for pricing, feature comparison, onboarding, consumer warmth, or a developer-tool surface whose primary job is operation rather than reading.

The example is an English/Latin proof specimen. The narrative comes first and the token appendix comes last. The publication is the primary artifact; the appendix makes the system inspectable.

## Reference lineage

These references are first-party lessons, not visual imitation:

| Reference | Lesson carried forward |
| --- | --- |
| Paco Coursey, [redesign 2021](https://paco.me/writing/redesign-2021) and [craft](https://paco.me/craft) | Documents-first restraint and typography as the primary visual system. |
| Manuel Moreale, [Typography and spacing in CSS](https://manuelmoreale.com/thoughts/typography-and-spacing-in-css) | Tie spacing to the reading unit and keep the variable set deliberately small. |
| Rauno Freiberg, [Next.js craft](https://rauno.me/craft/nextjs) and [interfaces](https://interfaces.rauno.me/) | Use structural grid lines, fluid type, accessible focus, and static-first sequencing. |
| Rasmus Andersson, [Inter specimen](https://rsms.me/inter/) | Make weights, numerals, punctuation, and long-form behaviour inspectable. |
| Carl Barenbrug, [Taste Matters](https://carlbarenbrug.com/taste-matters) and [Lab](https://carlbarenbrug.com/lab) | Treat editing, comparison, consistency, and intentional white space as design material. |
| Frank Chimero, [What Screens Want](https://frankchimero.com/blog/2013/what-screens-want/) | Treat responsive composition as a property of screens rather than print imitation. |

## Palette and contrast

The palette is warm flat paper, dark ink, and deep ultramarine action colour. It has no gradient, texture, coloured band, or decorative card grid. `--ink-3` and `--hair` are structural or disabled tiers, never live text colours.

| Token | Literal | Role |
| --- | --- | --- |
| `--ground` | `oklch(0.968 0.012 86)` | Reading sheet. |
| `--ground-2` | `oklch(0.940 0.014 84)` | Sunk field for table headers and control states. |
| `--ground-3` | `oklch(0.900 0.016 82)` | Deeper field for disabled and pressed surfaces. |
| `--ink` | `oklch(0.220 0.018 55)` | Body, display, and primary control text. |
| `--ink-2` | `oklch(0.440 0.015 55)` | Captions, utility labels, and secondary information. |
| `--ink-3` | `oklch(0.620 0.012 60)` | Disabled content and structural tiers only. |
| `--hair` | `oklch(0.820 0.012 75)` | Repeated structural rules. |
| `--accent` | `oklch(0.440 0.180 265)` | Links, action fill, and focus ring. |
| `--accent-ink` | `oklch(0.968 0.012 86)` | Text on the accent fill. |

The fixed palette has these verified WCAG contrast ratios. The values were calculated after OKLCH-to-sRGB conversion with the WCAG relative-luminance formula:

- `--ink` on `--ground` / `--ground-2` / `--ground-3`: **15.83:1 / 14.56:1 / 12.88:1**.
- `--ink-2` on `--ground` / `--ground-2` / `--ground-3`: **7.11:1 / 6.54:1 / 5.78:1**.
- `--accent` on `--ground` / `--ground-2` / `--ground-3`: **7.41:1 / 6.82:1 / 6.03:1**.
- `--accent-ink` on `--accent`: **7.41:1**.

Keep the palette literals fixed. Any colour change invalidates these ratios and the approved specimen contract.

## Type roles

Four font token slots resolve to three unique remote families. `--font-display` and `--font-body` both resolve to Newsreader. `--font-utility` resolves to Source Sans 3. `--font-mono` resolves to Source Code Pro. The official sources and SIL OFL 1.1 licences are [Newsreader](https://github.com/productiontype/NewsReader), [Source Sans](https://github.com/adobe-fonts/source-sans), and [Source Code Pro](https://github.com/adobe-fonts/source-code-pro).

Newsreader has no verified Devanagari or Arabic design in the inspected metadata. Future artifacts with unsupported scripts must choose and proof a compatible serif rather than silently claiming coverage.

| Role | Family | Size / leading | Weight | Tracking and behaviour |
| --- | --- | --- | --- | --- |
| Body | Newsreader | `19px / 30px`, `66ch` | 400 | `--track-body`, with `font-optical-sizing: auto`. |
| h1 | Newsreader | `40–64px / 1.05` | 500 | `--track-display`, with `font-optical-sizing: auto`. |
| h2 | Newsreader | `28–40px / 1.05` | 500 | `--track-display`, with `font-optical-sizing: auto`. |
| h3 | Newsreader upright | `22px / 28px` | 500 | `--track-display`, never italic. |
| Emphasis, citations, pull quotes | Newsreader true italic | Inherits its context | 400 | Use the real italic face, not a synthetic slant. |
| Strong | Newsreader | Inherits its context | 600 | Use weight for emphasis, not a new family. |
| Captions and table headings | Source Sans 3 | `14px / 20px` | 400 | Utility family, readable at compact sizes. |
| Navigation and controls | Source Sans 3 | `12px / 16px` | 600 | Minimum 44px target box despite the compact label. |
| Data cells, dates, bylines, token values | Source Code Pro | `14px / 20px` | 400 | `tabular-nums lining-nums`; `font-variant-ligatures: none`. |
| Compact identifiers and code | Source Code Pro | `12px / 16px` | 400 | `tabular-nums lining-nums`; `font-variant-ligatures: none`. |

The example proves reading text, utility text, data, glyphs, numerals, punctuation, italics, and the longest real section heading. Every role records family, weight, size, leading, tracking, measure, optical-sizing behaviour, and fallback. No family is hardcoded outside the four font tokens.

## Text-derived rhythm

The body line box is `19px × 1.57895 = 30px`. The spacing scale derives from that unit:

| Token | Value | Relationship |
| --- | --- | --- |
| `--space-1` | `0.25rem` | Micro control gap. |
| `--space-2` | `0.5rem` | Small control gap. |
| `--space-3` | `0.9375rem` | Half of the 30px body line box. |
| `--space-4` | `1.40625rem` | Three quarters of the body line box. |
| `--space-5` | `1.875rem` | One body line. |
| `--space-6` | `2.8125rem` | One and a half body lines. |
| `--space-7` | `clamp(3.75rem, 2.92rem + 3.4vw, 5.625rem)` | Fluid chapter interval. |
| `--space-8` | `clamp(5.625rem, 4.29rem + 5.5vw, 7.5rem)` | Fluid opening interval. |

Use `--space-1` and `--space-2` only for micro control gaps. Use `--space-3` through `--space-6` for prose, labels, rules, and component relationships. Use `--space-7` and `--space-8` only for fluid chapter and opening intervals. Do not invent another spacing value in the specimen CSS.

## Reading-column and evidence-bay layout

The signature layout is a stable left reading edge plus a functional right evidence bay. At widths of at least `66rem`, use `grid-template-columns: minmax(0, var(--measure)) minmax(12rem, var(--rail))` with `var(--space-6)` between columns. With a 19px Newsreader body, the bay gap resolves to 45px. Below `66rem`, evidence returns inline at its source point.

The bay may contain evidence only, never a decorative label. Source order owns the mobile reflow:

1. Header: h1 and lead first, then the contents `nav`; the nav occupies the bay only at wide width.
2. Thesis: main prose first, then a note naming the four supported composition modes.
3. Typography: main proofs first, then type-role metadata in the bay.
4. Rhythm: spacing proof first, then the grid figure and caption; the figure spans both columns at wide width.
5. Evidence: the comparison and token/key-value tables span both columns.
6. Components: one link, one button, and one text field state matrix spans both columns.
7. Reference appendix: all token proofs and the 41-row index span both columns.

Major `1px solid var(--hair)` chapter rules appear only on `#typography`, `#evidence`, and `#reference`. `#thesis`, `#rhythm`, and `#components` have no leading rule; their hierarchy comes from type and `--space-3` through `--space-6`. Do not repeat a fixed `3rem + rule + 2rem` treatment.

## Responsive behaviour

`.page-header`, `.section`, and `.footer` use a local `--page-gutter: var(--space-5)`, `width: calc(100% - var(--page-gutter) - var(--page-gutter))`, `max-width: calc(var(--measure) + var(--rail) + var(--space-6))`, and automatic inline margins. At `66rem`, `--page-gutter` changes to `var(--space-6)`. These shells do not add padding, so the grid content-box math remains exact.

Below `66rem`, flatten each main/evidence `.grid` in source order. Keep the contents index in two columns, falling to one only below `22rem`. At `66rem` and above, article content occupies column one and its owned evidence occupies column two. There is no sticky positioning, wrapped masthead nav, or horizontal navigation strip. The page itself never scrolls horizontally.

## Surface, radius, and elevation rules

Surfaces are warm flat paper and sunk fields. Use `--radius-sm` for content surfaces and `--radius-md` for controls. Do not apply `--radius-lg` or `--radius-pill` to page content; demonstrate them only as labelled token tiles in the appendix so the interchangeable vocabulary remains inspectable. Apply no shadow. `--shadow-1` is `none`.

No panel, feature card, decorative evidence bay, coloured band, paper grain, or gradient may be introduced. Rules and space carry hierarchy. A content surface has a radius token only because the token is being proved, not because editorial content needs a rounded container.

## Component and table behaviour

The component proof is a compact forced-state matrix for one link, one solid button, and one text input. Each has rest, hover, active, focus, and disabled copies. Do not add select or textarea matrices.

A link uses ink and a 1px ultramarine underline at rest, ultramarine text on hover, a 2px underline on active, and a 2px `--ring` focus outline at `--ring-offset`. The disabled link is `<a aria-disabled="true" tabindex="-1">` with no `href`; it uses `--ink-3` and cannot activate.

The solid button uses ultramarine and `--accent-ink` at rest, ink fill on hover, `--ground-2` with a 2px ultramarine border on active, the shared focus ring, and a real `disabled` attribute with `--ground-3` and `--ink-3`.

The text input uses ground plus an `--ink-3` border at rest, an `--ink-2` border on hover, an ink border on active, the shared focus ring, and a real `disabled` attribute with `--ground-3` and `--ink-3`. Every state has a non-colour cue. There is no transition or animation.

Comparison tables remain semantic tables inside a focusable `.table-wrap` scroll region. They stay comparison tables at every width and never become cards. Inventories marked `data-responsive="stack"` become labelled rows below `48rem`. Keep their real `<thead>` visually hidden rather than `display: none`; use `scope="col"` and `scope="row"`; make every `data-label` exactly match its column header. A table caption is non-empty and labels its `.table-wrap` region.

## Interaction and accessibility

Every interactive target is at least 44px by 44px. Use one selector list per real/forced state: `:hover` with `[data-state="hover"]`, `:active` with `[data-state="active"]`, and `:focus-visible` with `[data-state="focus"]`. Use a shared 2px focus outline with `outline-offset: var(--ring-offset)`. Do not use animation.

Each table has a non-empty `<caption>`, `scope="col"` column headers, and `scope="row"` row headers. Each `.table-wrap` has `tabindex="0"`, `role="region"`, and an accessible label tied to its caption. Keep comparison headers visible. For stacked inventories, visually hide the header row without removing it from the accessibility tree and expose each exact header through `td::before { content: attr(data-label) }`.

Add `@media (forced-colors: active)` mappings: body to `Canvas` and `CanvasText`, links to `LinkText`, controls to `ButtonFace` and `ButtonText`, focus outlines to `Highlight`, disabled content to `GrayText`, and every structural border to `CanvasText`. Do not remove borders or rely on forced colour alone for state.

## Print translation

Print is A4 portrait with `@page { size: A4 portrait; margin: 18mm 16mm; }`. Use white stock and these print overrides:

```css
--ground: #fff;
--ground-2: #f5f5f3;
--ground-3: #ececea;
--ink: #111;
--ink-2: #444;
--ink-3: #767676;
--hair: #b8b8b8;
--accent: #111;
--accent-ink: #fff;
--ring: #000;
```

Set body copy to `10.5pt / 15pt`. The print grid is `minmax(0, 2.25fr) 10rem` with a `12pt` gap. Keep ordinary evidence in the second column; wide figures and tables span both columns. Retain the in-flow contents index, underlined links, and visible rules. Neutralise controls and print only each component's rest-state row. Hide duplicate forced-state rows. Use `break-inside: avoid` on figures and table rows where practical.

## Avoid list

- No cream/terracotta pairing.
- No faux paper grain.
- No broadsheet columns.
- No centred reading column.
- No decorative evidence bay.
- No repeated rule-and-gap formula.
- No sans body.
- No proportional data figures.
- No mono ligatures in data.
- No shadow.
- No radius on editorial content.
- No sticky application navigation.
- No animation.
- No live text in `--ink-3` or `--hair`.
- No uncited invented metric, chart, quote, or image.

## Complete custom-property map

The four token declarations below are the complete interchangeable contract. Keep this table in the same order as the `:root` declarations and the example's token index. `color-scheme` is a normal property and is excluded from the count. There are 41 custom properties, ending with `--shadow-1`.

| Token | Value | Role |
| --- | --- | --- |
| `--ground` | `oklch(0.968 0.012 86)` | Reading sheet. |
| `--ground-2` | `oklch(0.940 0.014 84)` | Sunk field. |
| `--ground-3` | `oklch(0.900 0.016 82)` | Deep field. |
| `--ink` | `oklch(0.220 0.018 55)` | Primary ink. |
| `--ink-2` | `oklch(0.440 0.015 55)` | Secondary ink. |
| `--ink-3` | `oklch(0.620 0.012 60)` | Disabled and structural tier. |
| `--hair` | `oklch(0.820 0.012 75)` | Hairline rule. |
| `--accent` | `oklch(0.440 0.180 265)` | Action and focus colour. |
| `--accent-ink` | `oklch(0.968 0.012 86)` | Text on action colour. |
| `--ring` | `oklch(0.440 0.180 265)` | Focus ring colour. |
| `--ring-offset` | `0.1875rem` | Focus separation. |
| `--radius-sm` | `0` | Content surface radius. |
| `--radius-md` | `0.125rem` | Control radius. |
| `--radius-lg` | `0.25rem` | Appendix-only token proof. |
| `--radius-pill` | `999px` | Appendix-only token proof. |
| `--font-display` | `"Newsreader", Georgia, serif` | Display face. |
| `--font-body` | `"Newsreader", Georgia, serif` | Reading face. |
| `--font-utility` | `"Source Sans 3", system-ui, sans-serif` | Utility face. |
| `--font-mono` | `"Source Code Pro", ui-monospace, SFMono-Regular, Menlo, monospace` | Data face. |
| `--text-base` | `1.1875rem` | Body size. |
| `--text-h1` | `clamp(2.5rem, 1.95rem + 2.25vw, 4rem)` | Main heading size. |
| `--text-h2` | `clamp(1.75rem, 1.48rem + 1.1vw, 2.5rem)` | Section heading size. |
| `--text-h3` | `1.375rem` | Subheading size. |
| `--text-meta` | `0.875rem` | Caption and metadata size. |
| `--text-small` | `0.75rem` | Compact utility size. |
| `--leading-body` | `1.57895` | Body line-height. |
| `--leading-h3` | `1.27273` | H3 line-height. |
| `--leading-display` | `1.05` | Display line-height. |
| `--track-display` | `normal` | Display tracking. |
| `--track-body` | `normal` | Body tracking. |
| `--measure` | `66ch` | Reading measure. |
| `--rail` | `17rem` | Evidence bay width. |
| `--space-1` | `0.25rem` | Micro gap. |
| `--space-2` | `0.5rem` | Small gap. |
| `--space-3` | `0.9375rem` | Half-line rhythm. |
| `--space-4` | `1.40625rem` | Three-quarter-line rhythm. |
| `--space-5` | `1.875rem` | One-line rhythm. |
| `--space-6` | `2.8125rem` | One-and-a-half-line rhythm. |
| `--space-7` | `clamp(3.75rem, 2.92rem + 3.4vw, 5.625rem)` | Fluid chapter interval. |
| `--space-8` | `clamp(5.625rem, 4.29rem + 5.5vw, 7.5rem)` | Fluid opening interval. |
| `--shadow-1` | `none` | No elevation. |
