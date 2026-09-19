# Tailwind v4 declaration mapping

On a React 19 + Vite + TypeScript + Tailwind v4 + shadcn/ui stack, use this to find the utility behind a declaration, or the declaration behind a utility, without guessing at a lookalike.

| Declaration | Effect | Tailwind |
| --- | --- | --- |
| `font-family: sans-serif` / `serif` / `monospace` | Family stack | `font-sans` / `font-serif` / `font-mono` |
| `font-size` | Size from the type scale | `text-*` |
| `font-weight` | Any value 1 to 1000 | `font-*` |
| `font-style: italic` | Switch to italic | `italic` |
| `-webkit-font-smoothing` + `-moz-osx-font-smoothing` | Smooth macOS rendering; apply once at the root | `antialiased` |
| `font-synthesis: none` | Disable synthesized forms after verifying every fallback and emphasis state | `[font-synthesis:none]` |
| `font-variation-settings` | Tune a custom variable axis with no property of its own | `[font-variation-settings:"GRAD"_80]` |
| `font-optical-sizing` | Adjust letterforms per rendered size | `[font-optical-sizing:auto]` |
| `font-variant-caps` | Real small capitals from the font | `[font-variant-caps:small-caps]` |
| `font-variant-position` | Real superscript and subscript glyphs | `[font-variant-position:super]` |
| `font-variant-numeric: tabular-nums` | Equal-width digits for changing values | `tabular-nums` |
| `font-variant-numeric: slashed-zero` | Distinguish `0` from `O` | `slashed-zero` |
| `letter-spacing` | Space between letters | `tracking-*` |
| `line-height` | Space between lines | `leading-*` |
| `font-kerning` | Kerning on or off | `[font-kerning:none]` |
| `text-box: trim-both cap alphabetic` | Trim the reserved space above and below glyphs | `[text-box:trim-both_cap_alphabetic]` |
| `max-width` on a text column | Cap the measure at roughly 60-75 characters per line | `max-w-xl` / `max-w-2xl` / `max-w-[65ch]` |
| `text-align` | Where lines start and end | `text-start` / `text-center` |
| `text-wrap: balance` | Even heading lines | `text-balance` |
| `text-wrap: pretty` | Avoid an orphaned final word | `text-pretty` |
| `text-overflow: ellipsis` | Ellipsis on clipped text | `truncate` |
| `line-clamp` | Cut off after N lines | `line-clamp-*` |
| `overflow-wrap: break-word` | Break a long string before it escapes its container | `break-words` |
| `white-space: nowrap` | Stop wrapping | `whitespace-nowrap` |
| `text-transform` | Change the displayed case without touching the stored copy | `uppercase` / `capitalize` |
| `text-decoration-color` | Underline colour, the only part that animates reliably | `decoration-*` |
| `text-decoration-thickness` | Underline thickness | `decoration-1` / `decoration-2` |
| `text-underline-offset` | Push the underline down | `underline-offset-*` |
| `text-underline-position: from-font` | Underline position from the font's own metrics | `[text-underline-position:from-font]` |
| `text-decoration-style` | Dotted, dashed, or wavy | `decoration-dotted` / `decoration-wavy` |
| `text-decoration-thickness: from-font` | Underline thickness from the font | `decoration-from-font` |
| `text-decoration-skip-ink` | Gaps around descenders | `[text-decoration-skip-ink:auto]` |
| `user-select: none` | Suppress selection, only on a verified drag or gesture conflict | `select-none` |
| `background-clip: text` | Clip a background or gradient to the letterforms | `bg-clip-text` |
| `initial-letter` | Size a drop cap | `[initial-letter:3]` |
