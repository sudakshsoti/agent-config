# Layout mechanics

Grouping, spacing, adaptivity and internationalisation measurements that support `../SKILL.md`.

## Group gap versus intra-group gap

The gap between groups is at least 2x the gap within one group: `8px` intra-group needs `16px`+ inter-group, or the eye cannot tell where one group ends. Space is the first grouping tool, background shapes second for units that must read as one (a selectable row, a draggable card), separator lines last and only where space costs too much (dense tables, long settings lists).

Between adjacent bordered or filled controls (buttons, inputs), start at `12px`. Around borderless controls (text buttons, icon buttons), start at `24px`, since nothing but space marks where one target ends and the next begins. Unrelated control groups take `24px`+, consistent with the 2x rule above. These are starting points for a project with no density scale; a compact professional tool may use less as long as hit areas stay distinct and never overlap.

## Logical properties, not physical

Direction-dependent horizontal position is expressed as leading/trailing so layout mirrors automatically under `dir="rtl"`.

| Physical (avoid) | Logical (use) |
| --- | --- |
| `margin-left` | `margin-inline-start` |
| `padding-right` | `padding-inline-end` |
| `left: 0` | `inset-inline-start: 0` |
| `text-align: left` | `text-align: start` |
| `border-right` | `border-inline-end` |

Physical properties break the moment the layout mirrors: a hardcoded `margin-left` stays on the same physical side in RTL, landing on the wrong logical edge. Reserve physical properties for things that refer to physical screen sides regardless of language, such as positioning against a device notch or matching a gesture direction. Sequences that encode progression (star ratings, step indicators, progress bars) mirror in RTL too, filling from the trailing side; flexbox and grid with logical properties mirror automatically, hand-positioned elements do not.

## Container queries for components, media queries for pages

Prefer container queries where a component must adapt to the column or panel it sits in, not the viewport:

```css
.card-list { container-type: inline-size; }
@container (max-width: 400px) {
  .card { grid-template-columns: 1fr; }
}
```

A viewport media query on a component breaks it inside a narrow sidebar, since the query fires on the whole viewport regardless of the component's actual width. Reserve viewport media queries for page-level layout decisions: breakpoints belong to where the content stops fitting, not to `768px`/`1024px` device presets, and the expanded layout should hold as long as it genuinely fits rather than collapsing early.

## Peeking scroller

A horizontally scrollable row needs a visible affordance that more content exists, without relying on motion. Size items so the next one peeks `16-32px` past the container edge; a row of cards that ends exactly at the edge looks complete and nobody scrolls it.

```css
.scroller {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-inline: 24px;
  scroll-padding-inline: 24px;
  scroll-snap-type: x mandatory;
}
.scroller > * {
  flex: 0 0 calc(100% - 48px - 24px); /* container minus margins minus peek */
  scroll-snap-align: start;
}
```

The container's own padding creates the peek; snap points stay on the content edge.

## Pseudo-localisation and content bleed

Translated strings grow, and short source strings grow proportionally more than long ones, so a one-word button label is the riskiest thing on the screen. Test with pseudo-localisation or a genuinely long-string locale rather than budgeting a fixed percentage. No fixed widths sized to the English label; use `max-width` and let rows wrap. No fixed heights on text containers; use `min-height` where a floor is needed. Size buttons from their label's `padding-inline`, never a hardcoded width.

Content and controls behave differently at the edges: backgrounds, hero media and scrollable lists bleed to the viewport edges; text and controls stay inside the layout margins and safe areas (`env(safe-area-inset-*)`), floating above the content layer rather than being clipped by it.
