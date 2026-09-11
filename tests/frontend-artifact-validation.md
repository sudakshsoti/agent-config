# Frontend artifact v1 validation

Run on 2026-09-12 with `gpt-5.6-luna` at high reasoning through Codex and Pi. Every build ran in an isolated temporary directory with closed stdin, the selected language explicitly approved and the same content brief in both harnesses. The generated artifacts remain in `/tmp/frontend-artifact-validation/` on the validation machine; they are evidence rather than maintained fixtures.

## Comparison builds

| Brief and language | Codex | Pi |
| --- | --- | --- |
| Streaming latency, technical-field-guide | Passed | Passed |
| Streaming latency, visual-essay | Passed | Passed |
| Research-list utility, personal-software | Passed | Passed after a focused QA follow-up supplied the initially omitted report |

All six artifacts expose useful content immediately and remain free of horizontal overflow at 390 and 1440 CSS px. The two latency explainers show the six supplied stages, label values as illustrative, total 150 ms initially and update to 210 ms when the jitter buffer changes to 120 ms. Both sliders have accessible names. The two utilities support title/tag search, a tag filter, live result counts and a recoverable empty state. Browser verification found no console errors.

Rendered screenshots were inspected at narrow and wide widths. Technical-field-guide used a sectional, annotated mechanism; visual-essay used narrative pacing, stronger prose/display contrast and evidence integrated into its reading sequence. Personal-software kept the list and controls immediate with little chrome. These results validate the three selected profiles, not the five profiles outside the approved generated-output set.

Pi's first personal-software run produced the artifact and screenshots but omitted `QA.md`. A focused follow-up inspected the existing output, exercised the states, corrected `scroll-behaviour` to `scroll-behavior`, captured final evidence and supplied the report without rebuilding the artifact.

## Behavioural probes

| Case | Codex | Pi |
| --- | --- | --- |
| No language named | Recommended technical-field-guide, asked for confirmation and wrote no artifact | Initially wrote an artifact; after the hard-gate correction, recommended technical-field-guide, asked for confirmation and wrote nothing |
| Requested interaction conflicts with a stated static-page decision | Surfaced the conflict and wrote nothing | Surfaced the conflict and wrote nothing |
| Image inspection explicitly unavailable during review | Reported that pixel-level quality remained unverified and left the page unchanged | Reported that pixel-level quality remained unverified and left the page unchanged |

The initial Pi confirmation failure led to the explicit no-write gate in `skills/frontend-artifact/SKILL.md` and a contract assertion in `scripts/test-design-instructions.py`. The targeted retry passed from an empty workspace. Raw probe prompts, command arguments, output and judgements remain under `/tmp/frontend-artifact-validation/probes/` on the validation machine.

## Installation checks

The focused installer linked the skill and its three companion design skills from the durable agent-config checkout without touching model settings or unrelated links. Fresh Codex and Pi sessions each reported exactly one `frontend-artifact` entry. The installed paths expose all eight note/image pairs, and the ZIP integrity check found all 16 reference files without errors.

Repository validation: `scripts/check.sh` passes skill lint, ZIP parity, Codex config tests, design instruction tests and all eight selected-installer isolation tests.
