# Frontend Skills Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce the Codex frontend/design catalogue from 15 exposed skills to
8 without losing useful visual, motion, strategy, writing, prototyping, library
selection, or maintainability behaviour.

**Architecture:** Four canonical expertise skills own visual craft, motion
implementation, motion review, and product/UX strategy. Large source-specific
bodies move into conditional references. Four narrow workflow skills remain
separate. Retired repo skills move under `skills/_archive/`, so they stop loading
but remain recoverable; live Codex changes happen only after tracked changes pass
static checks.

**Tech Stack:** Markdown skills with YAML frontmatter, Git symlinks,
`install.sh`, Python skill linting, Codex plugin configuration.

## Global Constraints

- Scope is the Codex frontend/design subset: 15 exposed skills become 8.
  `html-doc` and `discovery-first` remain installed as adjacent document/process
  skills, so the broader adjacent set contains 10 skills.
- Final catalogue: `frontend-craft`, `motion-craft`, `motion-review`,
  `design-foil`, `prototype`, `ux-writing`, `pick-ui-library`, and
  `maintainability-review`.
- Do not edit Claude-only `agents/`, `settings.json`, `claude-powerline.json`,
  `hooks/`, `plugins.txt`, or `dist/` as Codex.
- Do not install repo-managed skills under `~/.codex/skills`; repo skills are
  linked through `~/.agents/skills`.
- Preserve current useful behaviour unless this plan explicitly names it for
  deletion.
- Use block-scalar YAML descriptions when a description spans multiple lines.
- Keep active `SKILL.md` bodies below the 20,000-byte warning threshold by
  routing specialised material into `references/`.
- Treat APCA as supplementary design guidance. WCAG 2.2 contrast ratios remain
  the conformance check.
- `motion-review opportunities` and `motion-review diff` are read-only.
  `motion-review audit` may create tracked plans but never modify product source.
- No live catalogue mutation before Tasks 1-4 are committed and static checks
  pass.
- Commit once per task. Never push, merge, or open a PR without explicit user
  instruction.

---

## Final skill contracts

| Skill | Loads for | Does not load for |
| --- | --- | --- |
| `frontend-craft` | Visual direction, typography, colour, hierarchy, layout systems, CSS/design tokens | Behaviour-only components, data flow, state management, API wiring |
| `motion-craft` | Implementing motion, gesture physics, springs, component interaction polish, naming an animation effect | Repo-wide audits or review verdicts |
| `motion-review` | Finding justified opportunities, auditing existing motion across a repo, reviewing a motion diff | Implementing fixes in product source |
| `design-foil` | Product strategy, UX critique, design-process artefacts; conditionally loads healthcare/enterprise context | CSS execution, typography systems, motion implementation |
| `prototype` | Explicit multi-variant build-and-select workflow | Ordinary single-direction UI work |
| `ux-writing` | Interface language, errors, empty states, labels, voice and tone | Visual direction |
| `pick-ui-library` | Explicit dependency lookup | General UI design |
| `maintainability-review` | Frontend code structure and long-term maintainability | Visual, accessibility, security, or correctness critique |

## File map

### Create

- `skills/motion-craft/SKILL.md`: mode router for `implement`, `gesture`, and
  `terminology`.
- `skills/motion-craft/references/standards.md`: canonical motion decision,
  timing, easing, accessibility, and performance rules.
- `skills/motion-craft/references/gesture-physics.md`: interruptibility,
  velocity hand-off, momentum, resistance, sheets, drag and swipe.
- `skills/motion-craft/references/animation-glossary.md`: the current exact-term
  reverse-lookup glossary.
- `skills/motion-craft/references/component-polish.md`: retained non-motion
  component API, defaults, naming and documentation material from
  `emil-design-eng`.
- `skills/motion-review/SKILL.md`: explicit `opportunities`, `audit`, and `diff`
  mode contracts.
- `skills/motion-review/references/standards.md`: relative symlink to the
  canonical `motion-craft/references/standards.md`, so filesystem installs share
  one source and packaged skills receive the followed content.
- `skills/motion-review/references/plan-template.md`: self-contained motion
  implementation-plan format retained from `improve-animations`.
- `skills/design-foil/references/healthcare-operator-context.md`: user, product,
  work-machine, prototyping, and career/influence context currently embedded in
  `value-connect`.
- `skills/design-foil/references/healthcare-design-principles.md`: healthcare
  audit principles currently separate from the generic principles.
- `skills/design-foil/references/healthcare-templates-and-prompts.md`: healthcare,
  domain and career-specific artefact templates and challenge prompts.

### Modify

- `skills/frontend-craft/SKILL.md`: narrow trigger, replace random selection,
  add subject grounding and the retained plugin critique loop, correct contrast
  guidance, update motion routing.
- `skills/design-foil/SKILL.md`: add healthcare mode routing and remove the
  retired `value-connect` cross-reference.
- `skills/prototype/SKILL.md`: replace old animation-skill references with
  `motion-craft` and `motion-review`.
- `skills/html-doc/SKILL.md`: route application UI work to `frontend-craft` or
  `prototype`, not the disabled `frontend-design` plugin.
- `skills/README.md`: list the final active catalogue and describe archived
  names.

### Archive

- `skills/animation-vocabulary/`
- `skills/apple-design/`
- `skills/emil-design-eng/`
- `skills/find-animation-opportunities/`
- `skills/improve-animations/`
- `skills/review-animations/`
- `skills/value-connect/`

Move each directory to `skills/_archive/<name>/` only after its retained
material exists in a canonical destination.

### Live changes after tracked work passes

- `/Users/sudakshsoti/.codex/config.toml`: set
  `[plugins."frontend-design@claude-plugins-official"] enabled = false`.
- `/Users/sudakshsoti/.codex/skills/uncodixfy/`: move to a dated Trash location;
  do not merge any content.
- `~/.agents/skills/` and `~/.claude/skills/`: relink/prune through
  `./install.sh --prune --no-plugins`.

---

### Task 1: Make `frontend-craft` canonical

**Files:**

- Modify: `skills/frontend-craft/SKILL.md`

**Produces:** A visual-system skill whose discovery boundary no longer catches
behaviour-only frontend work.

- [x] **Step 1: Rewrite the frontmatter description**

  Name the positive triggers: visual direction, subject-specific art direction,
  typography, colour, hierarchy, layout systems, responsive visual behaviour,
  CSS tokens, `@theme`, `@font-face`, OKLCH and design-system styling. Add the
  negative boundary in the same description: do not load solely because a task
  touches React/Vue/Svelte, component behaviour, state, data flow, API wiring or
  tests.

- [x] **Step 2: Replace random direction selection**

  Delete the `node -e` random picker. Require one sentence naming the concrete
  subject, audience and page job before choosing a direction. Convert the eight
  existing directions into labelled examples, with an explicit instruction to
  derive other directions from the subject's materials, instruments, artefacts
  and vernacular.

- [x] **Step 3: Retain the plugin material worth keeping**

  Add concise rules for hero-as-thesis, structural devices that encode real
  information, complexity matching the chosen direction, deliberate content,
  one signature element, and a pre-build critique against the actual brief.
  Preserve production typography, OKLCH, existing-token discipline,
  interaction states and responsive visual verification.

- [x] **Step 4: Correct accessibility wording and routing**

  Require WCAG 2.2 contrast ratios for conformance and allow APCA Lc as an
  additional perceptual report. Replace `emil-design-eng` and `apple-design`
  links with `motion-craft`; retain `ux-writing` and `html-doc` boundaries.

- [x] **Step 5: Verify and commit**

  Run:

  ```bash
  python3 scripts/lint-skills.py .
  rg -n 'Math\.random|emil-design-eng|apple-design|APCA.*not.*AA|frontend-design' skills/frontend-craft/SKILL.md
  ```

  Expected: lint passes; the search returns no random picker, retired routing,
  or claim that APCA replaces WCAG.

  Commit:

  ```bash
  git add skills/frontend-craft/SKILL.md
  git commit -m "skills: make frontend craft canonical"
  ```

---

### Task 2: Create `motion-craft` and retire implementation sources

**Files:**

- Create: `skills/motion-craft/SKILL.md`
- Create: `skills/motion-craft/references/standards.md`
- Create: `skills/motion-craft/references/gesture-physics.md`
- Create: `skills/motion-craft/references/animation-glossary.md`
- Create: `skills/motion-craft/references/component-polish.md`
- Archive: `skills/animation-vocabulary/`
- Archive: `skills/apple-design/`
- Archive: `skills/emil-design-eng/`

**Produces:** One implementation skill with `implement`, `gesture`, and
`terminology` modes and conditionally loaded source material.

- [ ] **Step 1: Reconcile the canonical standards**

  Build one rule set from the overlapping Emil, Apple and animation-review
  material. Resolve these conflicts rather than copying both sides:

  - Replace “transform and opacity only” with “prefer compositor-friendly
    properties; animate layout dimensions only when the interaction requires
    real spatial continuity and measurement/performance are controlled”.
  - Make duration ranges component-specific; remove the simultaneous absolute
    “under 300 ms” and “drawers up to 500 ms” claims.
  - Remove absolute GPU/browser claims that are not supported by current primary
    browser or Motion documentation.
  - Preserve justification gates, frequency costs, correct transform origins,
    reduced motion, interruption, keyboard parity and performance measurement.

- [ ] **Step 2: Extract conditional references**

  Move the animation glossary verbatim into `animation-glossary.md`. Move Apple
  gesture physics into `gesture-physics.md`. Move Emil's component API,
  defaults, naming and documentation guidance into `component-polish.md`.
  Keep typography and materials out of `motion-craft`; typography belongs to
  `frontend-craft`, while broad product/process critique belongs to
  `design-foil`.

- [ ] **Step 3: Write the three-mode router**

  `terminology` returns the best exact term first and at most two alternates,
  without implementation advice unless asked. `gesture` loads gesture physics
  and standards. `implement` loads standards plus component polish only when
  component API/default decisions are involved. Every mode checks existing
  project motion conventions and reduced-motion behaviour before introducing a
  new pattern.

- [ ] **Step 4: Archive retired sources**

  Use `git mv` for all three source directories after comparing every unique
  section against the new files. The archive is the rollback and provenance
  record; active routing must not point into it.

- [ ] **Step 5: Verify and commit**

  Run:

  ```bash
  python3 scripts/lint-skills.py .
  test -f skills/motion-craft/references/animation-glossary.md
  test -f skills/motion-craft/references/gesture-physics.md
  test -f skills/motion-craft/references/component-polish.md
  test -f skills/_archive/animation-vocabulary/SKILL.md
  test -f skills/_archive/apple-design/SKILL.md
  test -f skills/_archive/emil-design-eng/SKILL.md
  ```

  Expected: all commands exit 0 and `motion-craft` produces no body-size warning.

  Commit:

  ```bash
  git add skills/motion-craft skills/_archive/animation-vocabulary skills/_archive/apple-design skills/_archive/emil-design-eng
  git commit -m "skills: consolidate motion implementation guidance"
  ```

---

### Task 3: Create `motion-review` with safe mode boundaries

**Files:**

- Create: `skills/motion-review/SKILL.md`
- Create: `skills/motion-review/references/standards.md` symlink
- Create: `skills/motion-review/references/plan-template.md`
- Archive: `skills/find-animation-opportunities/`
- Archive: `skills/improve-animations/`
- Archive: `skills/review-animations/`

**Consumes:** `skills/motion-craft/references/standards.md`.

**Produces:** One review skill with three mutually exclusive scopes and no
product-source mutation.

- [ ] **Step 1: Define mode selection**

  Route absent-motion questions such as “what should animate here?” to
  `opportunities`; repo-wide requests about existing motion to `audit`; and an
  explicit changed diff or invocation to `diff`. If a request combines absent
  and existing motion across a repo, select `audit` and include missed
  opportunities as one audit category rather than running two modes.

- [ ] **Step 2: Preserve each mode's output contract**

  `opportunities` remains read-only, caps recommendations at seven, includes
  rejected candidates, and gives exact recipes. `audit` inventories existing
  motion, prioritises findings, and may write self-contained plans under
  `plans/`; it does not modify product source. `diff` returns severity-grouped
  findings and an explicit approve/request-changes verdict.

- [ ] **Step 3: Remove execution from review**

  Delete the old `improve-animations execute` ambiguity. Implementation is a
  separate hand-off to `motion-craft` or a tracked plan executor. State this in
  both the description and body.

- [ ] **Step 4: Link the shared standards and archive sources**

  Create the relative symlink:

  ```bash
  ln -s ../../motion-craft/references/standards.md skills/motion-review/references/standards.md
  ```

  Confirm it resolves, then `git mv` all three retired review skills under
  `skills/_archive/`.

- [ ] **Step 5: Verify and commit**

  Run:

  ```bash
  test -f skills/motion-review/references/standards.md
  python3 scripts/lint-skills.py .
  rg -n 'execute|modify product source|write implementation' skills/motion-review
  ```

  Expected: the standards symlink resolves; lint passes; any search hit clearly
  prohibits execution or product-source mutation.

  Commit:

  ```bash
  git add skills/motion-review skills/_archive/find-animation-opportunities skills/_archive/improve-animations skills/_archive/review-animations
  git commit -m "skills: unify motion review workflows"
  ```

---

### Task 4: Merge `value-connect` into conditional `design-foil` references

**Files:**

- Modify: `skills/design-foil/SKILL.md`
- Create: `skills/design-foil/references/healthcare-domain.md`
- Create: `skills/design-foil/references/healthcare-operator-context.md`
- Create: `skills/design-foil/references/healthcare-design-principles.md`
- Create: `skills/design-foil/references/healthcare-templates-and-prompts.md`
- Archive: `skills/value-connect/`

**Produces:** One strategy skill that stays industry-agnostic by default and
loads the full healthcare/enterprise pack only when relevant.

- [ ] **Step 1: Preserve the generic shell**

  Keep `design-foil`'s business-model grounding, Brainstorm, Audit and Design
  Process modes, generic principles, frameworks and templates. Remove the
  instruction to invoke `value-connect` separately.

- [ ] **Step 2: Build the complete healthcare pack**

  Move durable VBC economics, quality, regulatory, care-delivery and competitor
  material into `healthcare-domain.md`. Move Pop-I/Value Connect operator
  context, work-machine constraints, natural-language prototyping approach, and
  Lead-level career/influence lens into `healthcare-operator-context.md`. Keep
  healthcare audit principles and templates/prompts separate from their generic
  equivalents.

- [ ] **Step 3: Add conditional routing**

  When the request involves US healthcare, value-based care, Optum, UHG,
  Value Connect, Pop-I, payers, providers, registries, quality measures or care
  management, load all four healthcare references. For other industries, do not
  load them. Time-sensitive regulatory, competitor and benchmark claims require
  live primary-source verification.

- [ ] **Step 4: Archive `value-connect` after a destination audit**

  Compare its main file and three references against the new healthcare pack.
  Archive only after every unique operator, domain, career and template section
  has a named destination.

- [ ] **Step 5: Verify and commit**

  Run:

  ```bash
  python3 scripts/lint-skills.py .
  rg -n 'value-connect' skills/design-foil
  for file in healthcare-domain healthcare-operator-context healthcare-design-principles healthcare-templates-and-prompts; do test -f "skills/design-foil/references/$file.md"; done
  test -f skills/_archive/value-connect/SKILL.md
  ```

  Expected: lint and file checks pass; any `value-connect` text is product
  context, never a retired skill-routing instruction.

  Commit:

  ```bash
  git add skills/design-foil skills/_archive/value-connect
  git commit -m "skills: fold healthcare strategy into design foil"
  ```

---

### Task 5: Repair routing, migrate the live catalogue, and verify rollback

**Files:**

- Modify: `skills/prototype/SKILL.md`
- Modify: `skills/html-doc/SKILL.md`
- Modify: `skills/README.md`
- Modify live: `/Users/sudakshsoti/.codex/config.toml`
- Remove from active discovery, recoverably:
  `/Users/sudakshsoti/.codex/skills/uncodixfy/`

**Consumes:** All canonical skills from Tasks 1-4.

**Produces:** Eight discoverable frontend/design skills, no retired-name routes,
and a reversible live migration.

- [ ] **Step 1: Update every active cross-reference**

  Route prototype implementation to `frontend-craft` and `motion-craft`, and
  prototype motion review to `motion-review`. Route HTML application/landing-page
  work to `frontend-craft` or explicit `prototype`, not `frontend-design`.
  Search all active skill files for every retired name and correct each hit.

- [ ] **Step 2: Update the catalogue documentation**

  Replace the seven retired repo-installed names with `motion-craft` and
  `motion-review`; remove `value-connect`; retain the four separate utilities;
  state that `html-doc` and `discovery-first` remain adjacent but outside the
  eight-skill frontend/design count. Update the installed total from 31 to 26.

- [ ] **Step 3: Run tracked static verification and commit**

  Run:

  ```bash
  python3 scripts/lint-skills.py .
  rg -n 'animation-vocabulary|apple-design|emil-design-eng|find-animation-opportunities|improve-animations|review-animations|value-connect|frontend-design' skills --glob '!_archive/**'
  git diff --check
  ```

  Expected: lint and diff checks pass. Search hits are allowed only where a
  product named “Value Connect” is context, never where an active skill routes
  to a retired name.

  Commit:

  ```bash
  git add skills/prototype/SKILL.md skills/html-doc/SKILL.md skills/README.md
  git commit -m "skills: update frontend catalogue routing"
  ```

- [ ] **Step 4: Prepare reversible live changes**

  Record the current plugin line and direct skill path:

  ```bash
  rg -n -A1 '\[plugins\."frontend-design@claude-plugins-official"\]' /Users/sudakshsoti/.codex/config.toml
  test -f /Users/sudakshsoti/.codex/skills/uncodixfy/SKILL.md
  ```

  Use `apply_patch` to change only the frontend-design plugin's `enabled` value
  from `true` to `false`. Move the unmanaged directory to
  `/Users/sudakshsoti/.Trash/uncodixfy-2026-08-05`; if that exact path exists,
  stop and choose a unique dated suffix rather than overwriting it.

- [ ] **Step 5: Relink, prune and verify live discovery**

  Run from the canonical checkout:

  ```bash
  ./install.sh --prune --no-plugins
  codex exec "list skill names"
  ```

  Confirm each of the eight final frontend/design names appears exactly once;
  retired names, `uncodixfy`, and the plugin-provided `frontend-design` are
  absent; `html-doc` and `discovery-first` remain present exactly once.

  Run bounded smoke prompts in fresh `codex exec` processes:

  1. Visual tokens and typography select `frontend-craft`.
  2. Behaviour-only React data flow does not select `frontend-craft`.
  3. “What is the iOS rubber-band effect called?” selects
     `motion-craft terminology`.
  4. Gesture implementation selects `motion-craft gesture`.
  5. “What should animate on this static screen?” selects
     `motion-review opportunities`.
  6. Existing repo-wide motion selects `motion-review audit`.
  7. A motion diff review selects `motion-review diff`.
  8. A Pop-I strategy critique selects `design-foil` and its healthcare pack.

  Cap each command's output and record only the selected skill/mode and whether
  it matched the expected route.

- [ ] **Step 6: Complete surface-specific verification**

  As Codex, run the checks that do not modify Claude-only `dist/`:

  ```bash
  python3 scripts/lint-skills.py .
  ./scripts/test-context-size.sh
  git status --short
  ```

  The user or a Claude-owned workflow must regenerate the affected `dist/` zips
  before `./scripts/check.sh` can pass `check-zips.py`. Do not edit `dist/` from
  Codex. Also note that `plugins.txt` still installs `frontend-design` for
  Claude Code; changing Claude's plugin catalogue is a separate user-authorised
  task because this Codex overlay forbids editing that file.

## Rollback

If live verification fails:

1. Set the live frontend-design plugin back to `enabled = true`.
2. Move `/Users/sudakshsoti/.Trash/uncodixfy-2026-08-05` back to
   `/Users/sudakshsoti/.codex/skills/uncodixfy`, provided the destination is
   absent.
3. Revert the failing task commit, never reset the branch.
4. Run `./install.sh --prune --no-plugins` again.
5. Repeat the bounded discovery check before continuing.

## Completion gate

The consolidation is complete only when:

- All five tracked task commits exist and the worktree is clean.
- Active skill files contain no routing references to retired skill names.
- The eight final frontend/design skills appear once each in fresh Codex
  discovery.
- Retired names, `uncodixfy`, and Codex's plugin `frontend-design` do not appear.
- `html-doc` and `discovery-first` still appear once each.
- Visual, behaviour-only, motion terminology, motion implementation, all three
  motion-review modes, and healthcare strategy smoke prompts route correctly.
- WCAG 2.2 remains the conformance rule and APCA is supplementary.
- Rollback locations and the previous live plugin value have been recorded.
