# Screen systems

## Decisions

- Define roles by reading task and density before selecting sizes. Body copy needs a stable measure, legible x-height, and a fallback with compatible metrics; compact controls may need a separate role rather than compressed body text.
- Prefer `rem` for user-scalable type. Use `clamp()` only where its lower, fluid, and upper values are proofed against actual wrapping. Treat a fluid formula as a delivery mechanism, not a scale.
- Set body measure in characters, then tune width and leading with real copy. Do not carry a print measure into a phone or assume one desktop line length works in localisation.
- Use `font-optical-sizing: auto` only after checking the face has a useful `opsz` axis. Declare known variable axes deliberately. Set `font-synthesis: none` when faux bold or italic would damage hierarchy.
- Subset with `unicode-range` only when the split preserves each required script. Preload only fonts needed above the fold; use `font-display` according to the reading and brand cost of fallback.
- Match fallback metrics with `size-adjust`, `ascent-override`, `descent-override`, and `line-gap-override` when a late webfont would otherwise shift the page.

## Failure patterns

- A headline that only fits in the design-language screenshot, not at a translated or accessibility-scaled length.
- A body size reduced to preserve a fixed card height.
- One Latin fallback silently serving a different script.
- Preloading every family, weight, and subset, delaying more important content.
- Layout shift hidden by a screenshot taken after fonts finish loading.

## Proof

Inspect the rendered system at the project’s actual breakpoints and, where applicable, 390px and 1440px. Check 200% browser zoom or operating-system text scaling, longest translated strings, fallback rendering, narrow and wide measures, and font-loading transitions. Completion requires no clipped, overlapping, or horizontally overflowing text; intentional line breaks must survive the target widths.