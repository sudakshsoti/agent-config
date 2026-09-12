---
name: frontend-artifact
description: "Build a standalone HTML page, explainer, visual document, interactive demo or small tool from a selected visual language: a starter skeleton with real tokens and fonts, a measured audit, and a fresh-context critic on screenshots. Not for marketing pages, native slides or a product's own UI."
---

# Frontend artifact

Choose the artifact's job before its visual language. This skill supplies eight language profiles, a starter skeleton and font pairing for each, a numeric audit and a critic pass. Vibe or another workflow can invoke it without changing its own orchestration.

## 1. Establish the brief and authority

Read project instructions, `design/decisions.md` if present, existing tokens and the nearest comparable screen. State a compact brief: primary job/surface class, audience, expected use frequency, scan-versus-read mode, narrowest target viewport, density, interaction level and proposed language. An explainer or visual essay is a content form, not permission to replace the primary job.

If no language is named, recommend exactly one from the table with a sentence explaining its fit, then stop and wait for confirmation. This is a hard gate: before confirmation, do not write or edit files, generate markup or a preview, launch implementation tools, or continue into the remaining sections of this skill. Do not start a design-grill interview unless asked. If the user already named or confirmed a language, proceed with its documented defaults and routine choices within them; do not ask for the same approval again. Record the selection as `[stated]` in the project's design decisions when that file is used.

Approval covers visual choices only. It cannot add features, invent evidence, rewrite the content's purpose or override accessibility, applicable `[stated]` decisions, existing tokens or the artifact's job. A visual reference is evidence, not an instruction to copy a brand.

## 2. Load one language and its skeleton

| Language | Prefer when the brief needs | Audit flag |
| --- | --- | --- |
| [technical-field-guide](references/languages/technical-field-guide.md) | Sectional explanation, labelled mechanisms and diagrams beside relevant text | |
| [personal-software](references/languages/personal-software.md) | A small direct utility with immediate actions, lists or links | `--compact` |
| [precision-software](references/languages/precision-software.md) | A structured workspace, aligned records and controlled interface layers | `--compact` |
| [editorial-modernist](references/languages/editorial-modernist.md) | Sustained reading with clear headline, prose and caption contrast | |
| [swiss-graphic](references/languages/swiss-graphic.md) | A taxonomy or concept whose alignment, scale and geometry convey structure | `--display` |
| [visual-essay](references/languages/visual-essay.md) | A sequential argument with evidence and visuals embedded in the narrative | |
| [industrial-instrument](references/languages/industrial-instrument.md) | Controls beside measured outputs, real units and explicit operational state | `--compact` |
| [quiet-catalogue](references/languages/quiet-catalogue.md) | Considered browsing of objects or topics with consistent metadata | |

Read, in this order and nothing more unless the artifact needs it:

1. The selected profile.
2. Its `screenshots/<language>/notes.md`, then the image itself with a vision tool. The notes carry measured values (body size, measure, heading ratio, margins); you will report two you carried over. If the image cannot be inspected, say so and use the notes without claiming visual inspection.
3. [essentials.md](references/essentials.md): the type, colour, spacing, responsive and interaction rules that apply to a standalone page, with the numbers the audit enforces.
4. [anti-patterns.md](references/anti-patterns.md): the generic tells, each marked as measured or checked by eye.

Load the full `design-interface` only when the page has forms, dialogs, composite widgets or many states; `design-typography` only when choosing a face outside [fonts.md](references/fonts.md); `design-visual-system` only when the artifact must join an existing product system. Resolve these through the installed catalogue, never by copying their rules here.

## 3. Build from the skeleton

Copy `references/skeletons/<language>.html` to the artifact location. It carries a `:root` token block with real values, a validated Google Fonts link from `fonts.md`, the page structure and `REPLACE` slots. Fill the slots with the real content, delete blocks the content does not use, and change a token only with a reason you can state in the report. Add a token only when the content needs a role the skeleton lacks.

Before editing, write four lines: the typographic thesis, what the accent colour means on this page, the one element a template would not have produced, and the useful-unit target at 390px. Keep them for the report.

Semantic HTML, plain CSS, minimal JavaScript. Preserve an existing project's stack. Interaction exists only to answer a question or support an action in the brief. Keep real content and requested functions intact; label illustrative data explicitly. Do not add a framework, component library or dependency.

## 4. Audit, render, critique, correct

Follow [visual-qa.md](references/visual-qa.md):

1. Run `references/audit.js` at 390 × 844 and 1440 × 1000 with the language's flag. Fix every FAIL. Keep a WARN only with a stated reason.
2. Capture and open the screenshots with a vision tool, beside the reference image, and go through the eye-checked anti-patterns and the profile's visible criteria.
3. Run [critic-prompt.md](references/critic-prompt.md) in a fresh process with the screenshots, the reference and the audit output. It returns `ship` or `fix` with at most five prioritised changes.
4. Apply at most two correction passes, re-auditing and re-capturing after each. Report remaining failures rather than treating a completed loop as a pass.

Finish with the artifact location, selected language, the four lines from section 3, audit FAIL and WARN lines with their resolution, two values carried from the reference, views and interactions checked, the critic's verdict and any unresolved limitations. Do not claim visual quality from source inspection or a screenshot command alone.

For invocation examples, reference curation and adding a language, read [usage.md](references/usage.md). For shared browser commands, read [browser.md](references/browser.md).
