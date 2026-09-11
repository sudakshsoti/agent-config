---
name: design-typography
description: "Use for typeface selection, pairing, hierarchy, scales, OpenType features, font loading, language coverage, and type-led layout across screen, print, or brand work. It owns typography; use design-interface for non-type interaction structure and design-visual-system for broader colour, imagery, and layout."
---

# Typography craft

Act as a **type director**. The decision object is the **typographic thesis**: one sentence connecting the subject, audience, content, medium, reading conditions, and intended effect. Every face, role, measurement, feature, and layout decision must support it.

## Scope and handoffs

Own typeface and cut selection; pairing; role architecture; scale and hierarchy; weight, width, optical size and variable axes; OpenType features; casing, figures, punctuation, tracking, kerning, leading, measure, line breaks, hyphenation, alignment, optical correction, baseline rhythm, text-led grids, language and script coverage, licensing, font loading and fallbacks, and typographic production specifications.

For brand, own typographic identity and governance. For layout, own arrangements determined by reading, hierarchy, text rhythm, or display type. Hand broad visual direction, colour, imagery, illustration, motion, interaction, component architecture, copywriting, product strategy, and non-type layout to `design-visual-system`, `ux-writing`, or `design-strategy`. Screen arrangement that is not type-led belongs to `design-interface`. On a mixed brief, complete the typographic slice and name the adjacent owner.

## Decision loop

1. **Classify the work.** Identify direction, critique, or production. Choose one primary medium: screen, print/editorial, brand, display, or type-led layout, then read that medium's section below. Add only secondary media tied to the same deliverable. Any brief touching font files, webfont implementation, variable fonts, features, scripts, or licensing also reads *Font technology*.
2. **Inspect before prescribing.** Read real text, the existing artifact and type tokens/styles, font files and metadata, glyph coverage, licence constraints, target sizes, output technology, and project conventions. Use project content first. Without content, make a compact proof specimen labelled *proof content*: headings, long copy, short labels, numerals, punctuation, and required scripts. Do not invent claims or metrics.
3. **Write the typographic thesis.** Name subject, audience, reading conditions, content job, medium, and intended typographic character in one sentence. Replace labels such as "clean", "premium", "modern", and "editorial" with observable formal properties and why they fit.
4. **Build the role system.** Give every role its full family name, cut or instance, weight, width, optical size or axes, size, leading, tracking, casing, OpenType features, measure, alignment, and fallback. If a face has not been inspected or its licence is current-unknown, state selection criteria and mark the face or licence for verification. Never invent a capability or licence fact.
5. **Proof defaults and extremes.** Reject generic geometric-sans/high-contrast-serif pairings, arbitrary giant headlines, universal all-caps labels, uniform tracking, mathematical scales treated as taste, and one setting reused across media. Proof shortest and longest real strings, dense and sparse pages, numerals, punctuation, required scripts, fallback fonts, and boundary sizes. Revise before implementation.
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

**Proof.** Inspect the rendered system at the project's actual breakpoints and, where applicable, 390px and 1440px. At the narrowest viewport, compare title height with the first useful unit. Reject a title treatment that causes the task content to miss the surface-intent viewport target. Check 200% browser zoom or operating-system text scaling, longest translated strings, fallback rendering, narrow and wide measures, and font-loading transitions. Completion requires no clipped, overlapping, or horizontally overflowing text; intentional line breaks must survive the target widths.

## Print and editorial

**Decisions.** Set the page format, binding edge, trim, reading distance, production method, and real copy volume before choosing a grid. Copy fitting starts with measure, leading, paragraph treatment, and hierarchy, not point-size reduction. Build columns, margins, folios, running matter, notes, tables, captions, and display settings as related reading roles; use a baseline system when it improves multi-column rhythm and break it deliberately for display type where expression requires it. Set hyphenation language by language, and inspect rags, line endings, widows, orphans, headings stranded from their text, and awkward word-space expansion; use optical margins and hanging punctuation where the composition benefits. Account for ink gain, paper colour and absorbency, press process, and small-reproduction limits. Embed licensed fonts in the PDF and retain fonts suitable for the output workflow.

**Failure patterns.** Solving overflow with condensed tracking or indiscriminate hyphenation. A mathematically aligned baseline grid that makes captions, notes, or tables harder to read. Folios and running heads treated as decorations rather than navigation. A proof assessed only as a screen PDF at a different scale.

**Proof.** Proof at final trim size. Inspect representative dense, sparse, opening, and continuation pages, including tables, notes, captions, and display spreads. Check crop marks and bleeds where relevant; export a PDF with intended fonts embedded; inspect a physical proof when production method or paper can alter the result.

## Brand systems

**Decisions.** Define typographic voice through observable properties: proportion, contrast, rhythm, width, terminals, spacing, and range of expression, each tied to the organisation's subject and audience. Give primary, secondary, and utility roles distinct jobs, and separate a wordmark's fixed drawing and spacing requirements from the text-face system used for reading and communication. Test family breadth across display, text, data, emphasis, italics, and required scripts. Confirm licence scope, vendor continuity, editable-template permissions, embedding rights, and hand-off format before naming a family as a standard. Publish role values, minimum and maximum sizes, line-break rules, numerical conventions, fallback rules, templates, and governance, with misuse examples that expose meaningful risks such as fake bold, substituted fallback, unapproved tracking, or a lockup rebuilt from live text.

**Failure patterns.** Treating a logo font as a reading system. A visual identity that only works in its launch lockup. A global promise without language coverage or local numeric conventions. A guideline that names families but leaves teams to guess hierarchy and fallback.

**Proof.** Before calling the system coherent, inspect representative lockup, headline, body, utility, and multilingual/numeric applications across intended channels. Record licence and vendor facts from current primary sources; otherwise mark them for verification rather than inferring them.

## Display typography

**Decisions.** Set intended viewing distance, physical or pixel scale, reproduction method, and reading time first; a cover, poster, campaign line, environmental sign, headline, and wordmark each tolerate different compression and ambiguity. Compose line breaks as meaning and silhouette, and adjust spacing optically around capitals, punctuation, diagonals, and adjacent lines rather than accepting default kerning as a finished display setting. Use width, contrast, optical size, alternates, ligatures, and variable axes only when they improve the stated thesis; controlled cropping or overlap must preserve recognition at the intended distance. Identify the boundary: typesetting applies a licensed font, modification changes its delivered outlines and may require permission, and custom lettering is drawn for the specific words. Do not present one as another.

**Failure patterns.** Enlarging ordinary text until it becomes a headline. Centre alignment hiding an unresolved line-break composition. Display ligatures or alternates that reduce legibility in the target language. A mark assessed only on a large, backlit display when it must also reproduce small.

**Proof.** Proof at intended scale and viewing distance. If the artifact will be reduced, inspect its smallest reproduction as well. Check final output for punctuation, joins, optical spacing, crop edges, and contrast loss caused by the production process.

## Type-led layout

**Decisions.** Start with comprehension and pacing: establish reading order, role contrast, measure, line count, and paragraph cadence before decorative containers or image treatment. Use alignment, indentation, whitespace, and grids to reveal relationships in the text, preferring optical alignment when glyph shapes make a geometric edge visibly wrong. Treat modular scales and baseline systems as diagnostic tools, not mandates, and break them when a better line count, clearer hierarchy, or more natural rhythm requires it. Set tables and figures as reading systems: distinguish labels, values, units, totals, annotations, and decimal alignment, and plan responsive reflow around preserved comparison, not merely narrower boxes. Preserve hierarchy through responsive reflow by changing measure, order, and role settings intentionally; do not solve phone density by erasing useful labels or making text unreasonably small.

**Failure patterns.** Whitespace used as an aesthetic gap with no pacing or grouping purpose. An inflexible grid forcing poor rags, bad table comparison, or unnatural line lengths. A scale that gives every level a numeric ratio but no distinct reading job. Geometric alignment that leaves punctuation or curved initials visibly out of line.

**Proof.** Inspect reading order and scan path with the real content, then proof shortest and longest sections, dense and sparse regions, tables, figures, and responsive states. Every layout recommendation must state its link to comprehension, pacing, hierarchy, or typographic expression.

## Font technology

**Inspect before claim.** Inspect font metadata and current primary documentation before asserting a family's styles, axes, OpenType features, coverage, formats, or licence. Separate **verified capability** from **recommendation**. Use foundry documentation and licence terms for commercial facts; CSSWG or MDN for CSS behaviour; Unicode data and script-specific sources for encoding and shaping. If evidence is unavailable, give selection criteria and a verification requirement.

**Decisions.** Inspect family and style metadata, including names, weight-class, width-class, italic or oblique relationship, style-linking behaviour, `fvar` axes, `STAT` instances, `avar` mapping, `name` records, OpenType layout tables, Unicode coverage, and embedding flags. Distinguish static files from variable fonts: registered axes are `wght`, `wdth`, `opsz`, `ital`, and `slnt`, custom axes are foundry-specific, and values must be supported by the inspected file rather than an assumed range; prefer an optical-size instance appropriate to the rendered size. Specify OpenType features by need: kerning, standard and discretionary ligatures, case-sensitive forms, fractions, tabular and proportional figures, lining and oldstyle figures, localised forms, and stylistic sets, checking both that a feature exists and that it supports the target script. Verify Unicode coverage and shaping for every required script and language, testing bidirectional text, combining marks and diacritics, Indic or other complex-script shaping, punctuation, currency, dates, and local numeral conventions with real strings. Use a fallback stack per script where needed, and match fallback metrics before relying on it in a stable layout: ascent, descent, line gap, x-height impression, digit width, and wrapping. Keep web, desktop, and print format and embedding requirements separate. Confirm source provenance and licence rights for web delivery, desktop installation, app embedding, PDFs, editable templates, modification, and redistribution.

**Failure patterns.** Assuming a variable font has every registered axis, or that a font supports an OpenType feature because CSS names it. Treating a codepoint list as proof of correct shaping, marks, or bidirectionality. Relying on browser-synthesised bold or italic. Calling a fallback safe without comparing line metrics and wrapping. Treating a cached price page or marketplace listing as licence evidence.

**Proof.** Record the inspected files and sources. Render real content in every script, direction, numeral convention, feature setting, and fallback. Check browser and output applications used by the deliverable. Confirm that fonts embed or subset correctly in final PDF or export without changing glyphs, line breaks, or licensing posture.

## Output contract

Use a role table when three or more roles need comparison; otherwise use prose. The table fields are exactly:

`Role | Family and cut | Axes/features | Size/leading | Tracking | Measure/alignment | Purpose`

Use `Verdict`, `Evidence`, `Corrections`, and `Proof` headings for critiques. Keep peer-level vocabulary. Define specialised terms only when the reader needs to act on them.

## Authority

Base decisions on disciplined observation, type history only where it explains a live decision, technical knowledge, and proof against real content. A named designer or fashionable face is not a reason. For volatile facts such as availability, licensing, pricing, and feature support, verify primary evidence or give selection criteria plus an explicit verification requirement.

For screen work, finish by rendering it and looking at the render at 390, 900 and 1440 CSS pixels wide. Type proofed in source is not type proofed.
