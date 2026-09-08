# Utility-first interface instruction plan

## Context

Agents are applying marketing-page composition to reference tools and product interfaces. The tmux cheatsheet exposed the failure: settled context called for a compact mobile header and balanced density, yet the result added a display headline, introductory copy, a prefix block, and a “Start here” panel before the useful rows.

### Likely causes

1. **The active visual-system skill universalises the hero.** `skills/design-visual-system/SKILL.md` names “Compact utility” as one optional aesthetic, then says “The hero is a thesis” for all product UI. It does not classify the surface before layout.
2. **The external skill is broad at discovery time and marketing-led in its body.** `vendor/anthropics-claude-code/plugins/frontend-design/skills/frontend-design/SKILL.md` describes new UI generally and says the hero is the first thing viewers see. Codex sees it through `~/.agents/skills`; Claude’s `name-only` override does not apply to Codex, opencode, omp, or pi.
3. **The product-UI counterweight was archived.** `archive/skills/app-ui/SKILL.md` distinguishes memorable marketing from fast, unsurprising product UI and says data screens are not centred heroes. Active comments in `plugins.txt` still route product screens to this unavailable skill.
4. **Structure rules begin too late.** `skills/design-interface/SKILL.md` tests controls, states, accessibility, and large-list density, but has no surface-intent gate, first-use-versus-repeat-use distinction, heading-necessity test, or mobile time-to-content budget.
5. **Typography advice rejects giant headings without defining the compact default.** `skills/design-typography/SKILL.md` says roles follow reading task and density and rejects arbitrary giant headlines, but does not state what reference, settings, dashboard, and utility hierarchies should do instead. It also does not explicitly reserve monospace in mixed UI.
6. **Context is required but not operationalised.** `global-agents.md` says to read `design/decisions.md`, but does not block markup until the agent names the relevant settled decisions and checks its hierarchy against them. The tmux plan cited the file while routing the work through `frontend-design`, and the result contradicted explicit decisions in that file.
7. **Repository guidance is internally stale.** `skills/README.md` says `design-visual-system` and `design-typography` are archived even though both are active, while `plugins.txt` says product UI goes to archived `app-ui`. This makes correct skill selection less likely.

### Intended outcome

Every harness classifies the artifact’s job and reading mode before choosing hierarchy, typography, layout, or visual direction. Marketing may still use a hero or display type when justified. Reference, utility, dashboard, settings, and lookup-documentation surfaces default to fast access, compact hierarchy, and early useful content.

This task changes instructions, skills, tests, and generated skill zips only. It must not edit `desktop-tmux-cheatsheet.html` or `design/decisions.md`. Preserve the user’s existing uncommitted cheatsheet change.

## Approach

Put the shortest and highest-authority rule in `global-agents.md`, which is symlinked to the global instruction path for Codex, Claude, omp, opencode, and pi. Reinforce it in the descriptions and bodies of the three active repo-owned design skills so the right rules are visible both during skill discovery and after loading.

Keep the user-selected external `frontend-design` skill unchanged. Its broad discovery description cannot be technically narrowed without owning or shadowing it, so the cross-harness control is an explicit always-loaded applicability rule: `frontend-design` is marketing/brand only even when its own description appears to match a non-marketing UI request. The contract is authoritative guidance, not a mechanical route blocker; this limitation is accepted in exchange for retaining upstream updates.

Use numeric, render-checkable viewport guardrails instead of taste language. Add a contract smoke test that checks the shared wording, absence of known contradictions, routing, and four stored cases. Per the user’s choice, do not spend model quota on live cross-harness prompt runs; keep those prompts as future manual acceptance cases.

## Proposed wording

### `global-agents.md`

Replace the current `## Interface design` section with the existing decisions-file precedence plus this compact gate:

> Before any interface design, classify the surface by its primary job: **marketing/brand**, **reference/documentation**, **task utility**, **dashboard/data**, **settings/form**, or **content/editorial**. State the class, expected use frequency, scan-versus-read mode, and narrowest target viewport before choosing hierarchy. “Distinctive”, “bold”, or “polished” never changes the class.
>
> Read `design/decisions.md`, project instructions, existing tokens, and the nearest comparable screen before proposing layout or type. Name the applicable `[stated]` decisions in the plan or working notes. Do not build on an `[inferred]` decision until I confirm it. If the implementation conflicts with a stated decision, stop and surface the conflict instead of following a generic skill.
>
> `frontend-design` is for marketing and brand surfaces only, even when its broad description appears to match a non-marketing UI request. Reference, utility, dashboard, settings, and lookup-documentation surfaces are not landing pages: do not add a positioning-led opening block that delays the primary task. Their first viewport prioritises the task, controls, data, or reference content. A compact task summary may lead only when it directly helps the current decision and still meets the viewport budget. A visible page heading is optional when the shell already answers “where am I”; an accessible name is still required.

Replace the current precedence sentence with: accessibility requirements first; then applicable `[stated]` project decisions; then these surface-intent rules and the active design skills; then personal preference. An `[inferred]` decision never outranks confirmed guidance until the user confirms it.

### `skills/design-interface/SKILL.md`

Expand the frontmatter description so it triggers for “reference, utility, dashboard, settings, documentation, list, form, or interactive screen” and says it classifies intent before structure.

Add `## Surface intent gate` before the current rules:

> Before layout, write one line with: `class | primary job | new or repeat use | scan or read | narrowest viewport`. If the class is unclear, infer it from the task and existing product context; ask only when two classes imply materially different structures.
>
> Marketing/brand may spend the opening viewport on positioning. Reference/lookup-documentation, task utility, dashboard/data, and settings/form surfaces spend it on use. Tutorials, essays, and sequential guides classify as content/editorial rather than lookup documentation. On a repeat-use surface, onboarding and explanation move out of the normal path unless they are needed to prevent an error.

Add these testable rules:

- For reference/lookup-documentation, utility, dashboard, and settings surfaces at `390 × 844` CSS pixels, the first task-bearing control, data region, setting group, or reference entry starts within the top 40% of the viewport, and at least one complete useful unit is visible without scrolling. Verify from the rendered bounding boxes.
- Count every block before the first useful unit. Identity/navigation needed for wayfinding may precede it; promotional copy, a restatement of the page purpose, duplicate prefix/key explanations, and generic “Start here” panels may not. Any other pre-content block must name the user error or decision it prevents.
- A screen needs an accessible name, not automatically a large visible heading. If the shell, title bar, or navigation already names the current view, do not repeat it as a display heading. If a visible heading is needed, size it within the compact UI scale unless the surface is marketing/brand or content/editorial and display treatment serves the reading job.
- First-run help is a state, not permanent page furniture. Verify the repeat-use state separately and confirm learned guidance no longer pushes the primary task down.
- For frequently used surfaces, state a viewport utility target: which task-bearing units must be fully visible at the narrowest target width and height. Render and count them before completion.

### `skills/design-visual-system/SKILL.md`

Change the discovery description to say the skill classifies product surfaces before visual direction and does not apply marketing hierarchy to utilities.

Replace the unconditional hero paragraph with:

> Opening hierarchy follows the surface’s job. A marketing or brand surface may use a hero when positioning is the first task. On a reference, utility, dashboard, settings, or lookup-documentation surface, do not use a positioning-led opening block that delays the primary task. Open with task-bearing controls, data, or content, and spend distinctiveness inside that working structure rather than above it. A compact status or task summary is allowed only when it directly changes the user’s next decision and the viewport budget still passes. “Display-led” is available only when the classified reading job supports display reading; “compact utility” is the default direction for repeated scan-and-act use, not merely one style option.

Add to production checks:

> At `390 × 844`, report the top coordinate of the first useful unit and the number of complete useful units in the first viewport for every non-marketing surface. A polished header does not count as useful content.

### `skills/design-typography/SKILL.md`

Expand the discovery description to mention compact UI hierarchy and choosing whether a visible heading is needed.

Add under `## Screen systems`:

> Classify the reading mode before defining roles. Reference, dashboard, settings, and repeated-use utilities use a compact hierarchy: orientation text is subordinate to task content, role contrast comes from weight and spacing before large size, and display faces are not used merely to make the page feel designed. A visible title earns space only when it adds orientation not already supplied by the shell.
>
> In mixed interfaces, reserve monospace for code, key sequences, commands, identifiers, logs, aligned technical data, and terminal output. Do not set headings, navigation, explanatory prose, or ordinary labels in monospace merely because the subject is technical. An all-monospace interface requires an explicit project decision or a content constraint that makes the text itself machine-like.

Add to screen proof:

> At the narrowest viewport, compare title height with the first useful unit. Reject a title treatment that causes the task content to miss the surface-intent viewport target.

### Routing and repository guidance

- `plugins.txt`: replace “Product screens go to `app-ui`” with “`frontend-design` is marketing/brand only. Product, reference, utility, dashboard, settings, and lookup-documentation surfaces follow the always-loaded interface-intent contract plus `design-interface`, `design-visual-system`, and `design-typography` as relevant.”
- `skills/README.md`: replace stale archived-pipeline text with the actual active trio and their boundaries; retain the historical note without claiming active directories are archived.
- Do not change `settings.json`: its `skillOverrides` are Claude-only and the tracked copy is overwritten from the live file, so it cannot provide a cross-harness fix.

## Files to modify

- `global-agents.md`
- `skills/design-interface/SKILL.md`
- `skills/design-visual-system/SKILL.md`
- `skills/design-typography/SKILL.md`
- `plugins.txt`
- `skills/README.md`
- `tests/design-intent-cases.md` (new)
- `scripts/test-design-instructions.py` (new contract smoke test)
- `scripts/check.sh`
- `.githooks/pre-commit`
- `dist/design-interface.zip`
- `dist/design-visual-system.zip`
- `dist/design-typography.zip`

Do not modify the external skill under `vendor/`, `settings.json`, `design/decisions.md`, or `desktop-tmux-cheatsheet.html`. Run implementation from pi, Claude, or another permitted maintainer context: this repository’s `AGENTS.md` explicitly forbids Codex from editing `plugins.txt` and `dist/`, although Codex will consume the resulting instructions.

## Reuse

- Reuse the marketing-versus-product distinction and “data screens are not heroes” principle from `archive/skills/app-ui/SKILL.md`; do not restore the archived monolithic workflow.
- Reuse the density-register and render-verification style already used in `skills/design-interface/SKILL.md`.
- Reuse the reading-task and density-first decision loop in `skills/design-typography/SKILL.md`.
- Reuse the settled-decision precedence already in `global-agents.md`.
- Reuse `scripts/check.sh` as the CI entry point, `scripts/lint-skills.py` for frontmatter validation, `scripts/build-zip.sh` for packaging, and `scripts/check-zips.py` for source/archive parity.

## Steps

- [ ] Add the surface-intent gate and context-use requirement to `global-agents.md`, preserving the file’s under-200-line constraint.
- [ ] Add the exact classification, viewport, heading, repeat-use, and monospace guardrails to the three active design skills; update their discovery descriptions.
- [ ] Repair stale routing in `plugins.txt` and `skills/README.md` without editing or shadowing external `frontend-design`.
- [ ] Add structured prompt cases plus a contract smoke test, and wire the fast test into the pre-commit and CI check paths.
- [ ] Rebuild the three skill zips, run the full checks, inspect the instruction diff with `git diff --word-diff`, and commit without staging or changing `desktop-tmux-cheatsheet.html` or `design/decisions.md`; confirm the task is on an appropriate branch before committing.

## Verification

### Stored prompt cases

`tests/design-intent-cases.md` will contain these prompts and expected structural outcomes:

1. **Cheatsheet:** “Create a distinctive personal tmux cheatsheet used several times a day on a 390px phone. Use bold typography.” Expected: `reference/documentation`; compact title or no repeated visible title; filter/navigation plus at least one complete shortcut row in the first viewport; no hero, eyebrow, intro panel, or permanent “Start here”; monospace only for keys/commands/data.
2. **Settings:** “Design polished account notification settings for weekly use.” Expected: `settings/form`; compact orientation; first setting group and status/save behaviour in the first viewport; no promotional value proposition or onboarding panel in the repeat-use state.
3. **Dashboard:** “Design a distinctive operations dashboard for analysts monitoring incidents all day.” Expected: `dashboard/data`; filters/status/data begin in the first viewport; dense scan hierarchy; no display headline or marketing hero; useful-unit viewport target stated.
4. **Landing page:** “Design a product landing page for an incident-response tool.” Expected: `marketing/brand`; hero and display type are permitted, not mandatory, when they advance positioning and conversion; the non-marketing viewport rule does not apply.

Each case uses stable labelled fields for expected class, frequency, reading mode, narrowest viewport, allowed opening blocks, forbidden defaults, first-viewport target, and typography roles. The adversarial words “distinctive”, “polished”, and “bold typography” test that aesthetic language does not override intent. These four cases intentionally match the four surfaces requested; the taxonomy itself covers additional task-utility and content/editorial work.

### Contract smoke checks

`scripts/test-design-instructions.py` will fail when:

- `global-agents.md` lacks all six classes, project-context precedence, or the marketing-only boundary for `frontend-design`;
- any active repo-owned design skill contains an unconditional hero rule or another known phrase that contradicts the surface gate;
- the three active skill descriptions omit their revised routing terms;
- `plugins.txt` routes product work to archived `app-ui`;
- `skills/README.md` claims an active design skill is archived;
- any of the four prompt cases or expected class labels is missing.

Run:

```bash
./scripts/check.sh
python3 scripts/test-design-instructions.py
python3 scripts/lint-skills.py
python3 scripts/check-zips.py
```

This verifies contract presence, known-conflict removal, routing consistency, structured prompt coverage, and distributable skill parity. It is a smoke test, not behaviour verification: it cannot prove that a model will classify correctly or that a render meets the 40% target. Live model and render probes are intentionally excluded by the user’s verification choice.
