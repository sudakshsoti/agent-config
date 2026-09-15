# Visual review

Three passes, in order: measure, then look, then ask a fresh reviewer. Each pass has to produce evidence the report can quote.

## 1. Measure with audit.js

Run [audit.js](audit.js) against the page at 390 × 844 and 1440 × 1000. Add `--compact` for personal-software, precision-software and industrial-instrument, and `--display` for swiss-graphic. It needs the `playwright` module (the shared Pi package tree at `~/.pi/agent/npm/node_modules` is tried after the normal module path); set `CHROMIUM_PATH` to an installed browser when the module's own build is missing.

```sh
node "$SKILL_ROOT/references/audit.js" http://127.0.0.1:8765/ --width 390 --height 844 | tee audit.txt
node "$SKILL_ROOT/references/audit.js" http://127.0.0.1:8765/ --width 1440 --height 1000 | tee -a audit.txt
```

Thresholds it enforces:

| Check | PASS | WARN | FAIL |
| --- | --- | --- | --- |
| Primary font | named webfont rendering | | generic stack, failed load, fallback rendering, or a banned family |
| Families in use | ≤ 2 | 3 | > 3 |
| Body size | 16–20px (14–20 compact) | | outside |
| Body line-height | 1.4–1.6 | 1.3–1.4, 1.6–1.7 | outside |
| Widest prose measure (wide view) | 40–75ch | 30–40, 75–90 | outside |
| Body contrast | ≥ 7 | 4.5–7 | < 4.5 |
| H1 to body ratio | ≤ 3.2 (1.6 compact, 7 display) | up to +0.6 | beyond |
| Distinct radii | ≤ 3 | | > 3 |
| Shadows on static elements | 0 | | > 0 |
| Gradients | 0 | background | on text |
| backdrop-filter, hover transforms, negative tracking < 24px | 0 | | > 0 |
| Uppercase elements | ≤ 12 | > 12 | |
| Saturated hue buckets | ≤ 2 | 3 | > 3 |
| Horizontal overflow, images without alt, failed requests, console errors | 0 | | > 0 |
| First useful unit, narrow | ≤ 40% of viewport | reading page beyond | utility beyond |

Fix every FAIL before capturing screenshots. A WARN may be kept when the content justifies it; say so in the report. The script does not measure reading order, grouping, meaning of colour or whether the page is longer than its content; those are the next two passes.

## 2. Capture and look

Use the browser commands in [browser.md](browser.md). Capture after fonts and content are ready. Inspect at 390 × 844 and 1440 × 1000 CSS pixels, plus 900 px when applying `design-visual-system`. Include a full-page view for long documents so the opening cannot hide weak later sections.

Open every image you use as evidence — attach the local file to a model whose catalogue reports image input support. Saving a screenshot, reading HTML or obtaining a DOM snapshot is not visual inspection. If image access is unavailable, report "Visual inspection unavailable", identify the missing capability and distinguish any DOM and interaction checks completed. Do not fabricate a visual pass.

Open the language's `reference.png` beside the render. Its `notes.md` records measured relationships (body size, measure, heading ratio, margins); state two values you carried over and one you deliberately changed.

Then go through [anti-patterns.md](anti-patterns.md) items marked **eye** and the language profile's visible review criteria:

- **First useful content:** at 390 × 844 record its top coordinate and how many complete useful units fit. Controls, evidence and explanation count; an ornamental title does not.
- **Typography:** body readability, role contrast, the actual font's spacing. Challenge an oversized title or mechanical tracking.
- **Composition and density:** reading or action order, meaningful grouping, responsive hierarchy. Remove marketing openings, unnecessary cards and empty space that delays the task.
- **Colour and access:** visible focus, non-colour state cues, keyboard access, disabled, empty and error states where they exist, reduced-motion behaviour when motion exists.
- **Character:** the profile's three distinguishing features, visible in the render, explained through structure, type roles or grouping rather than accent colour alone.
- **Behaviour:** every requested interaction, mobile targets, overflow. Illustrative data is labelled.

## 3. Critic pass

Run [critic-prompt.md](critic-prompt.md) in a fresh process with the two screenshots, the reference image and `audit.txt`. It returns three differences from the reference, a feature check, generic tells, a first-useful-unit reading and a `ship` or `fix` verdict with at most five prioritised changes.

## 4. Correct and stop

Record each material weakness as observation → change → result. Apply at most two correction passes; after each, re-run the audit and re-capture the changed views, and run the critic once more after the first. If criteria still fail, preserve the usable artifact and report the unresolved issues; do not silently expand the task or claim completion on quality.

Report: output path, language, viewport sizes, screenshot paths, audit FAIL and WARN lines with their resolution, the two reference values carried over, the critic's verdict and remaining issues. Store QA evidence in the project's normal artifact location, not inside the reusable skill.
