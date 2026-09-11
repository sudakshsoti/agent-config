---
name: frontend-artifact
description: "Build standalone browser explainers, visual documents and small tools with a selected visual language, annotated references and rendered visual review. Reuses the shared design skills; not a marketing-page or native-slide workflow."
---

# Frontend artifact

Choose the artifact's job before its visual language. This skill supplies an editable language library and a build/review loop; `design-interface`, `design-visual-system` and `design-typography` remain the owners of their design rules. Vibe or another workflow can invoke this skill without changing its own orchestration.

## 1. Establish the brief and authority

Read project instructions, `design/decisions.md` if present, existing tokens and the nearest comparable screen. State a compact brief: primary job/surface class, audience, expected use frequency, scan-versus-read mode, narrowest target viewport, density, interaction level and proposed language. Use the existing six surface classes; an explainer or visual essay is a content form, not permission to replace the primary job.

If no language is named, recommend one from the table with a sentence explaining its fit, then wait for confirmation before coding. Do not generate a preview or start a design-grill interview unless asked. If the user already named or confirmed a language, proceed with its documented defaults and routine choices within them; do not ask for the same approval again. Record the selection as `[stated]` in the project's design decisions when that file is used.

Approval covers visual choices only. It cannot add features, invent evidence, rewrite the content's purpose or override accessibility, applicable `[stated]` decisions, existing tokens or the artifact's job. Resolve compatible project constraints directly; ask when a real conflict cannot be resolved within the chosen language. A visual reference is evidence, not an instruction to copy a brand.

## 2. Load one language

| Language | Prefer when the brief needs |
| --- | --- |
| [technical-field-guide](references/languages/technical-field-guide.md) | Sectional explanation, labelled mechanisms and diagrams beside relevant text |
| [personal-software](references/languages/personal-software.md) | A small direct utility with immediate actions, lists or links |
| [precision-software](references/languages/precision-software.md) | A structured workspace, aligned records and controlled interface layers |
| [editorial-modernist](references/languages/editorial-modernist.md) | Sustained reading with clear headline, prose and caption contrast |
| [swiss-graphic](references/languages/swiss-graphic.md) | A taxonomy or concept whose alignment, scale and geometry convey structure |
| [visual-essay](references/languages/visual-essay.md) | A sequential argument with evidence and visuals embedded in the narrative |
| [industrial-instrument](references/languages/industrial-instrument.md) | Controls beside measured outputs, real units and explicit operational state |
| [quiet-catalogue](references/languages/quiet-catalogue.md) | Considered browsing of objects or topics with consistent metadata |

Read only the selected profile, its linked screenshot notes and the image itself. Reference notes live at `<skill-root>/screenshots/<language>/notes.md`; resolve every Markdown link relative to the file containing that link, so `../../screenshots/` from `references/languages/` returns to the skill root. Images do not enter model context merely because they are stored here: open the image with a vision tool or attach it to an image-capable model. If the image cannot be inspected, say so and use the written notes without claiming visual-reference inspection.

Load `design-typography` for the type decisions and `design-interface` for repeated units, controls, responsive structure and states. From `design-visual-system`, apply the production checks and existing-token/accessibility guidance; do not rerun its direction-selection examples, override the selected profile with “compact utility”, or add a signature element unless this brief needs one. This skill remains the outer workflow, so do not re-enter its standalone-artifact route. Resolve sibling skills through the installed catalogue or sibling directories, never by copying their rules into this library.

## 3. Establish direction, then implement

Before markup, name the typefaces and roles, palette roles, spacing/token approach, main composition and three defining features from the selected profile. Their values should suit this content and the existing system; profiles are directions, not templates. For new artifacts without tokens, define a small local set of CSS custom properties for the actual roles needed.

Use semantic HTML, plain CSS and minimal JavaScript for a new standalone artifact. Preserve an existing project's stack. Interaction must answer a question or support an action in the brief. Keep real content and requested functions intact; label illustrative data explicitly. Do not introduce a framework, component library or dependency merely to reproduce this skill's references.

## 4. Render, inspect, correct

Follow [visual-qa.md](references/visual-qa.md). Run locally, capture and inspect narrow and wide views, exercise the actual controls, and assess the profile's visible criteria. Apply at most two correction passes, capturing and inspecting again after each change. Report remaining failures rather than treating a completed loop as a pass.

Finish with the artifact location, selected language, views/interactions actually checked and any unresolved limitations. Do not claim visual quality from source inspection or a screenshot command alone.

For invocation examples, reference curation and adding a language, read [usage.md](references/usage.md). For shared browser commands, read [browser.md](references/browser.md).
