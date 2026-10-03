# Loading states

The duration tree behind a loading-state choice. This is the calibration behind the 100ms feedback rule: a control must acknowledge a press within 100ms. It fills in what happens after that first 100ms.

## The tree

| Expected duration | UI |
|---|---|
| 0–800ms | Nothing. A spinner introduced before this flashes on and off. |
| 800ms–3s | An animated spinner. |
| 3s–15s | A progress bar with a percentage. |
| 15s+ | A progress bar, an estimated time, and a cancel control. |
| Unknown or streaming | Skeleton placeholders matching the layout's shape. |

## Skeletons

A skeleton hints at the shape of the incoming content — rectangles where text will sit, circles where an avatar will sit — not a decorative loading animation. It must match the real layout's item count, widths and gaps, or the layout jumps when content arrives. Skip the skeleton for a load expected under roughly 300ms; the flash reads worse than no treatment.

## Gotcha

Agents read this tree as "always show a spinner" and add one to a state change that resolves in a frame — the first row of the table says nothing, not a spinner, is correct under 800ms.

## Sources

- Retired skill design-engineering, file skills/design-engineering/references/components/empty-loading-states.md @ `81805dc89d40889639a95502bfb578a098266dc8`.
