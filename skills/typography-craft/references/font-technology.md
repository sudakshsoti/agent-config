# Font technology

## Inspect before claim

Inspect font metadata and current primary documentation before asserting a family’s styles, axes, OpenType features, coverage, formats, or licence. Separate **verified capability** from **recommendation**. Use foundry documentation and licence terms for commercial facts; CSSWG or MDN for CSS behaviour; Unicode data and script-specific sources for encoding and shaping. If evidence is unavailable, give selection criteria and a verification requirement.

## Decisions

- Inspect family and style metadata, including names, weight-class, width-class, italic or oblique relationship, style-linking behaviour, `fvar` axes, `STAT` instances, `avar` mapping, `name` records, OpenType layout tables, Unicode coverage, and embedding flags.
- Distinguish static files from variable fonts. Registered axes include `wght`, `wdth`, `opsz`, `ital`, and `slnt`; custom axes are foundry-specific. Set values supported by the inspected file, not assumed ranges. Prefer an optical-size instance appropriate to the rendered size.
- Specify OpenType features by need: kerning, standard/discretionary ligatures, case-sensitive forms, fractions, tabular/proportional figures, lining/oldstyle figures, localised forms, and stylistic sets. Check whether a feature exists and whether it supports the target script.
- Verify Unicode coverage and shaping for every required script and language. Test bidirectional text, combining marks and diacritics, Indic or other complex-script shaping, punctuation, currency, dates, and local numeral conventions with real strings.
- Use a fallback stack per script where needed. Match fallback metrics before relying on it in a stable layout; test ascent, descent, line gap, x-height impression, digit width, and wrapping. Keep web, desktop, and print format and embedding requirements separate.
- Confirm source provenance and licence rights for web delivery, desktop installation, app embedding, PDFs, editable templates, modification, and redistribution.

## Failure patterns

- Assuming a variable font has every registered axis or a font supports an OpenType feature because CSS names it.
- Treating a codepoint list as proof of correct shaping, marks, or bidirectionality.
- Relying on browser-synthesised bold or italic.
- Calling a fallback safe without comparing line metrics and wrapping.
- Treating a cached price page or marketplace listing as licence evidence.

## Proof

Record the inspected files and sources. Render real content in every script, direction, numeral convention, feature setting, and fallback. Check browser and output applications used by the deliverable. Confirm that fonts embed or subset correctly in final PDF/export without changing glyphs, line breaks, or licensing posture.