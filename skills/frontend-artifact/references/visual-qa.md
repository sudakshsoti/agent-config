# Visual review

## Capture and inspect

Use the existing local browser setup described in [browser.md](browser.md). Capture after fonts and content are ready. Inspect at 390 × 844 and 1440 × 1000 CSS pixels; also check 900 px when applying `design-visual-system`, which requires that intermediate width. Include a full-page view for long documents so the opening cannot hide weak later sections.

Open every image you use as evidence. Codex uses `view_image` for local files. Pi can attach local images to a model whose catalogue reports image input support. Saving a screenshot, reading HTML or obtaining a DOM snapshot is not visual inspection. If image access is unavailable, report “Visual inspection unavailable”, identify the missing capability and distinguish any DOM/interaction checks completed. Do not fabricate a visual pass.

## Review against the job and profile

- **First useful content:** at 390 × 844 record its top coordinate and how many complete useful units fit. Controls, evidence and explanation count; an ornamental title does not. A narrative may open with its actual argument, while a utility must expose its primary action or useful content immediately.
- **Typography:** check body readability, line length, role contrast and the actual font's spacing. Challenge an oversized title or mechanical tracking. Check computed font loading and apply `design-typography` rather than inventing another type checklist.
- **Composition and density:** verify the reading/action order, meaningful grouping and responsive hierarchy. Remove marketing openings, unnecessary cards and empty space that delays the task. Judge a sparse reading page differently from a repeated-use utility.
- **Colour and access:** verify text/control contrast against the applicable accessibility requirement, visible focus and non-colour state cues. Exercise keyboard access, labels, disabled/empty/error states when they exist, and reduced-motion behaviour when motion exists.
- **Character:** check the profile's three distinguishing features in the render. Can you explain the differences using content structure, type roles or grouping rather than just accent colour? Would this composition fit the brief without the reference brand's assets?
- **Behaviour:** test every requested interaction, mobile targets and overflow. Check the console for errors. For illustrative data, verify visible labels and calculations instead of presenting sample numbers as sourced measurements.

## Correct and stop

Record each material weakness as observation → change → result. Fix concrete problems in at most two passes, then re-render and re-inspect the changed views. Recheck affected interactions. If criteria still fail, preserve the usable artifact and report the unresolved issues; do not silently expand the task or claim completion on quality.

Keep evidence proportional: output path, language, viewport sizes, screenshot paths, checks performed and remaining issues. Store QA evidence in the project's normal artifact location, not inside the reusable skill. Persist exported/shared deliverables where the user can access them; temporary screenshots are not durable proof unless retained with the project.
