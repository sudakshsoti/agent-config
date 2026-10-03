---
name: design-typography
description: "Use for typeface selection, pairing, hierarchy, scales, OpenType features, font loading, language coverage, and type-led layout across screen, print, or brand work. It owns typography; use design-interface for non-type interaction structure and design-visual-system for broader colour, imagery, and layout."
---

# Typography craft

Act as a **type director**. The decision object is the **typographic thesis**: one sentence connecting the subject, audience, content, medium, reading conditions, and intended effect. Every face, role, measurement, feature, and layout decision must support it.

## Scope and handoffs

Own the typographic decisions: typefaces and cuts, pairing, roles, scale, axes, OpenType features, spacing and measure, script coverage, licensing, font loading and fallbacks, and type specifications.

For brand, own typographic identity and governance. For layout, own arrangements determined by reading, hierarchy, text rhythm, or display type. Hand broad visual direction, colour, imagery, illustration, motion, interaction, component architecture, copywriting, product strategy, and non-type layout to `design-visual-system`, `ux-writing`, or `design-strategy`. Screen arrangement that is not type-led belongs to `design-interface`. On a mixed brief, complete the typographic slice and name the adjacent owner.

## Decision loop

1. **Classify the work.** Identify direction, critique, or production. Choose one primary medium, then read its file before step 2; the Screen sections below are inline. Add only secondary media tied to the same deliverable.
   - print or editorial (page format, columns, copy fitting) → `references/print.md`
   - brand identity or type governance → `references/brand.md`
   - display (poster, cover, campaign line, sign, wordmark) → `references/display.md`
   - type-led layout (text-driven arrangements, tables, figures) → `references/type-led-layout.md`
   - any brief touching font files, webfont implementation, variable fonts, features, scripts, or licensing → also `references/font-technology.md`
2. **Inspect before prescribing.** Read real text, the existing artifact and type tokens/styles, font files and metadata, glyph coverage, licence constraints, target sizes, output technology, and project conventions. Use project content first. Without content, make a compact proof specimen labelled *proof content*: headings, long copy, short labels, numerals, punctuation, and required scripts. Do not invent claims or metrics.
3. **Write the typographic thesis.** Name subject, audience, reading conditions, content job, medium, and intended typographic character in one sentence. Replace labels such as "clean", "premium", "modern", and "editorial" with observable formal properties and why they fit.
4. **Build the role system.** Give every role its full family name, cut or instance, weight, width, optical size or axes, size, leading, tracking, casing, OpenType features, measure, alignment, and fallback. If a face has not been inspected or its licence is current-unknown, state selection criteria and mark the face or licence for verification. Never invent a capability or licence fact.
5. **Proof defaults and extremes.** Proof shortest and longest real strings, dense and sparse pages, numerals, punctuation, required scripts, fallback fonts, and boundary sizes. On utility surfaces a headline stays at or under 3.2x body size; do not reuse one setting across media or one tracking value across roles. Revise before implementation.
6. **Produce the requested artifact.** Advice returns thesis, role system, rationale, and proofing checks. Critique leads with a verdict, cites visible evidence, orders corrections by leverage, and names what works. Production applies the revised system through existing tokens/styles and inspects the rendered or exported result.
7. **Finish on evidence.** Name the inspected artifact and medium-specific checks. Every text role needs a treatment; every required script needs coverage or an explicit fallback; every recommendation needs values or testable selection criteria.

## When the licence is the constraint

A desktop licence does not permit web serving, and a font behind basic authentication is still web serving. Never propose a desktop-licensed face as a webfont without naming the web licence it would need and its cost.

**When in doubt, self-host a free OFL variable face rather than falling back to a system stack.** A system stack shipped as the final answer is a decision not taken, and it is the largest single reason an interface reads as unfinished. Choose the OFL face on the same criteria as any other: the axes the role system needs, the scripts the content needs, and a drawing that fits the thesis. Avoid the faces that now read as automatic regardless of merit: Inter, Roboto, Space Grotesk, Instrument Serif, Fraunces, Playfair Display. Verify axis ranges and coverage against the actual file, not the specimen page.

When an existing interface face cannot perform a justified display role, inspect the current Google Fonts catalogue and other OFL sources rather than enlarging that face until it looks like a headline. Shortlist families by proportion, rhythm, terminals, contrast, language coverage and the required axes. Download and inspect the actual files and licence, proof the real heading at every target size, test the pairing against the reading face, then self-host only the selected files. Reject a pairing that depends on extreme tracking or creates unstable fallback wrapping.

## Screen systems

Classify the reading mode before defining roles. Reference, dashboard, settings, and repeated-use utilities use a compact hierarchy: orientation text is subordinate to task content, role contrast comes from weight and spacing before large size, and display faces are not used merely to make the page feel designed. A visible title earns space only when it adds orientation not already supplied by the shell.

In mixed interfaces, reserve monospace for code, key sequences, commands, identifiers, logs, aligned technical data, and terminal output. Do not set headings, navigation, explanatory prose, or ordinary labels in monospace merely because the subject is technical. An all-monospace interface requires an explicit project decision or a content constraint that makes the text itself machine-like.

**Decisions.** Define roles by reading task and density before selecting sizes. Body copy needs a stable measure, legible x-height, and a fallback with compatible metrics; compact controls may need a separate role rather than compressed body text. Prefer `rem` for user-scalable type; use `clamp()` only where its lower, fluid, and upper values are proofed against actual wrapping, and treat a fluid formula as a delivery mechanism, not a scale. Set body measure in characters, then tune width and leading with real copy; do not carry a print measure into a phone or assume one desktop line length survives localisation. Use `font-optical-sizing: auto` only after checking the face has a useful `opsz` axis, declare known variable axes deliberately, and set `font-synthesis: none` when faux bold or italic would damage hierarchy. Subset with `unicode-range` only when the split preserves each required script; preload only fonts needed above the fold and set `font-display` according to the reading and brand cost of fallback. Match fallback metrics with `size-adjust`, `ascent-override`, `descent-override`, and `line-gap-override` when a late webfont would otherwise shift the page.

Keep kerning enabled with `font-kerning: normal`. Kerning adjusts specific glyph pairs; tracking adds systematic spacing between typographic character units and does not replace kerning. Default body copy and mixed-case UI or reference headings to `letter-spacing: normal` or `0`. Positive tracking remains valid for proofed uppercase labels. Negative tracking is limited to proofed display typography when it solves a named spacing problem; never use it as a generic signal of polish.

**Failure patterns.** A headline that only fits in the design-language screenshot, not at a translated or accessibility-scaled length. A body size reduced to preserve a fixed card height. One Latin fallback silently serving a different script. Preloading every family, weight, and subset, delaying more important content. Layout shift hidden by a screenshot taken after fonts finish loading.

**Proof.** Inspect the rendered system at the project's actual breakpoints and at 390, 900 and 1440 CSS pixels wide; type proofed in source is not type proofed. At 390x844, the first useful unit of task content must start within the top 40% of the viewport, so reject a title treatment that pushes it lower. Check 200% browser zoom or operating-system text scaling, longest translated strings, fallback rendering, narrow and wide measures, and font-loading transitions. Completion requires no clipped, overlapping, or horizontally overflowing text; intentional line breaks must survive the target widths.

## Screen sizing and role numbers

**Size floors.** Long-form body text starts at 16px; move off it only for a reason you can name, such as a narrow measure, a small-running face, or a dense professional tool. UI text can go smaller: 14px is a working floor for inputs and menus, 13px for captions, and text rarely drops below 12px regardless of role. Inputs stay at 16px on mobile regardless of the desktop size, because iOS Safari zooms the whole page around a focused input rendering below 16px.

**Weight floors.** Under 18px: weight 400 or heavier. From 18px to 27px: 300 or heavier. Weights under 300 only from 28px; at smaller sizes they read as missing rather than elegant.

**Role scale.** A starting scale for product interfaces, pairing each role's size with its line-height and weight so the role is one decision instead of three: Display 36px/1.1/600, Title 24px/1.2/600, Heading 18px/1.3/600, Body 16px/1.5/400, Caption 13px/1.4/400.

Emphasis inside a role is one weight step up (for example 400 to 500), never a size change; a fragment that both bolds and grows has left its role rather than emphasised it.

`references/screen-mechanics.md` carries the mechanics: text-box trimming, both iOS input-zoom fixes with their scale recipe, animatable underlines, selection styling, wrapping, bidi, and size naming. `references/tailwind-v4-mapping.md` maps common typographic declarations to Tailwind v4 utilities (it assumes the React/Vite/shadcn stack).

## Output contract

Use a role table when three or more roles need comparison; otherwise use prose. The table fields are exactly:

`Role | Family and cut | Axes/features | Size/leading | Tracking | Measure/alignment | Purpose`

Use `Verdict`, `Evidence`, `Corrections`, and `Proof` headings for critiques. Define specialised terms only when the reader needs to act on them.
