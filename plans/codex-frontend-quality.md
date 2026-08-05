# Plan: raise Codex's frontend output to near-Opus

## Context

Codex produces worse frontend than Opus. The instinct is to write it a better design
skill, but the skills that work on Opus are taste essays — Anthropic's `frontend-design`
is a page of adjectives ("make deliberate, opinionated choices about palette", "take one
real aesthetic risk you can justify"). That prose *directs* a latent capability. It does
not supply one. On a model with weaker design priors it is close to inert.

What transfers is not direction but substitution: shipped artifacts the model copies,
mechanical gates that catch what judgment misses, and prohibitions rather than aspirations.
This was proved on `html-doc` this session — prose-described CSS became `assets/base.html`,
a ten-item checklist became `scripts/check.py`, and the output stopped drifting.

**Figma covers large projects already, so this targets small and medium work where there is
no design to implement against.**

## The two failure modes are different problems

Conflating them is why generic "make it beautiful" guidance fails.

**1. Broken craft.** Spacing with no rhythm, type scale with no hierarchy, missing hover
and focus and disabled states, contrast that fails AA, layouts that break between 390px and
1440px, misaligned grids, unstyled form controls. This is most of what reads as "sucks",
it is objective, and it is fixable with a component kit plus mechanical gates.

**2. Sameness.** Purple-on-white gradients, generic SaaS card grid, cream + serif +
terracotta. Objectively fine, immediately recognisable as AI.

They pull in opposite directions. A shipped component kit fixes (1) and makes (2) worse.
So: **ship the system, vary the skin.** Structure, spacing scale, component anatomy and
states come from a fixed kit. Palette, type, radius and density are drawn from enumerated
axes by a seeded selector, not by the model's taste. Codex gets structure wrong and gets
personality samey, so constrain the first and randomise the second. Never ask it to "be
original" — that instruction is what produces the clustering.

## Three things this plan cannot assume

**That a new skill gets loaded.** Everything below is inert if Codex doesn't reach for it.
The 2% truncation problem (see Routing) is a direct argument that it might not. Step 0
tests this with `codex exec --json` JSONL evidence, before anything is built.

**That output is comparable run to run.** Codex varies. A single generation per brief
cannot separate a real improvement from noise, and "cut the guidance that didn't move the
needle" applied to n=1 is exactly the unfalsifiable-advice failure this plan exists to
avoid. The gate script is therefore built *before* the baseline.

**That "score" means anything until it is defined.** Every decision downstream of step 2
treats the audit result as a scalar. A list of pass/fail rules is not a scalar. Step 1a
writes the schema first — severity weights, and an explicit three-way split between fail,
pass and not-applicable — because a rule that silently returns "inapplicable" on every run
otherwise reads as a rule that passes.

## What reaches Codex today — corrected inventory

Verified against `~/.agents/skills` symlinks and `~/.codex/config.toml` plugin toggles:

| Reaches Codex | Does **not** reach Codex |
| --- | --- |
| `apple-design`, `emil-design-eng`, `design-craft`, `design-foil`, `prototype`, `pick-ui-library`, `ux-writing`, `animation-vocabulary`, `find-animation-opportunities`, `improve-animations`, `review-animations`, `html-doc` (repo skills, symlinked) | `hyperframes` — present in the marketplace cache, **not enabled** in `config.toml` |
| `frontend-design@claude-plugins-official` — **enabled**, `~/.codex/config.toml:99-100` | `frontend-app-builder` — ships inside the `build-web-apps` plugin, **not enabled** |

Consequences the first draft got wrong:

- `~/.codex/.tmp/plugins/plugins/` is a marketplace *catalogue* cache (hundreds of entries),
  not the installed set. Nothing in it is live, and `.tmp` can be wiped. Anything used from
  there must be **copied into the repo**, never referenced by path — and its licence checked
  for redistribution and attribution terms before the copy is committed.
- The real house-style file is
  `~/.codex/.tmp/plugins/plugins/hyperframes/skills/hyperframes/house-style.md`.
- `frontend-design` is the most likely incumbent to win "make this UI feel better" and was
  missing from the inventory entirely. Being a plugin, it cannot be moved to
  `skills/_archive/`; the lever is `enabled = false` in `~/.codex/config.toml`, which
  removes it from Codex only and leaves Claude untouched.

## The `_archive` route does not do what it claims

`install.sh:134-138` runs one loop over `skills/*/` and calls both `link_into` (→
`~/.claude/skills`) and `mirror_into` (→ `~/.agents/skills`). There is no exclusion
mechanism in either function. So moving `emil-design-eng` to `skills/_archive/` removes it
from **Claude as well as Codex**. "Make them Claude-only" currently has no implementation.

**Step 6a builds one:** a `CLAUDE_ONLY` list in `install.sh` that skips the `mirror_into`
call for named skills, so they stay linked into `~/.claude/skills` and never appear in the
shared `~/.agents` root. Small change, and it is the prerequisite for every "archive it for
Codex" decision in this plan. Until it exists, the only Codex-only levers are the
`config.toml` plugin toggles.

## Sequencing

### Step 0 — invocation probe (2 hours, gates everything)

Run ~10 phrasings and record **which skill Codex actually loaded**, from
`codex exec --json` JSONL events — not from the model mentioning a skill by name, which is
not evidence.

Phrasings: "build me a landing page", "make this UI feel better", "style this form", "the
spacing here is off", "give this page some personality", plus five more in the user's own
words.

Run envelope, fixed and recorded for every run in this plan:

```
codex exec --json --ephemeral -C "$FIXTURE" --skip-git-repo-check --sandbox <mode> "<brief>"
```

`--ephemeral` plus a throwaway git fixture per run keeps twenty autonomous runs from editing
or committing into this repo. Archive the JSONL under `evals/runs/`.

Then repeat with a stub `frontend-kit` skill present. Adding a new skill requires an
`install.sh` re-run (editing an existing SKILL.md is live; adds, renames and deletes are
not — `AGENTS.md`), so the stub is a real install, reverted afterwards.

- **If the stub wins most phrasings** → continue to step 1.
- **If incumbents keep winning** → switch to the hybrid route (see Fallback) before building
  anything.

The JSONL log is also the only honest way to settle the emil/apple question later.

### Step 1a — the evaluation contract (half a day, written before any code)

Nothing downstream is meaningful without this. Write `evals/CONTRACT.md` specifying:

- **Per-rule outcome:** `fail` / `pass` / `not-applicable` / `needs-review`. axe-core already
  distinguishes violations, passes and incomplete results; preserve that distinction rather
  than flattening it, or manual-review items silently score as passes.
- **Severity weights** per rule, and the denominator: score over *applicable* rules only,
  reported alongside the applicable count so a shrinking denominator is visible.
- **Aggregation** across the 3 runs of a brief: report median and range, not mean, so one
  broken generation doesn't swing the verdict.
- **Run envelope:** the `codex exec` invocation above, verbatim; recorded model version
  string and date; identical prompt text per brief across all arms.
- **What is not controlled:** temperature and model version are not exposed on a hosted
  model. Record them where visible, don't pretend to hold them fixed, and treat any
  difference smaller than the observed run-to-run range as noise.

### Step 1b — pinned runtime (2 hours)

There is no root `package.json` in this repo and `npx playwright` floats — it may fetch a
version expecting a different Chromium revision from the cached `chromium-1228`. Commit a
root `package.json` and `pnpm-lock.yaml` pinning `@playwright/test` and
`@axe-core/playwright`. Do not depend on the ambient Python Playwright install.

### Step 1c — `scripts/audit.mjs`, the measuring instrument (half a day)

Build the gate before the baseline. Most of it is not custom code.

**Delegate to `@axe-core/playwright`:** contrast below WCAG AA, form labels, heading
hierarchy skips, ARIA and role correctness. This is a solved problem with a maintained rule
set; hand-rolling a contrast engine is the largest avoidable build in this plan.

**Custom checks, geometry only** (axe doesn't cover these):

- Horizontal overflow at 390px: `scrollWidth > clientWidth` on `documentElement`.
- Tap targets under 44px: bounding box of every interactive element at 390px.
- **Breakpoint integrity** (renamed): the intended check was never CLS. Responsive reflow
  between 390px and 1440px is expected, not a defect — CLS measures *unexpected* movement
  between frames within one page lifecycle. The invariant to assert instead: at both widths,
  no element overflows its container, no text node is clipped, and no interactive element
  has zero area. Measure CLS separately per viewport if it's wanted at all.
- Computed font-size below 14px on body text.
- Interactive state distinction: for each interactive element, assert that the computed
  values of `background-color`, `color`, `border-color`, `box-shadow` or `transform` differ
  between rest and `:hover`, and that a `:focus-visible` style exists — exercised by
  keyboard `Tab`, not by mouse. `disabled` is `not-applicable` when nothing on the page has
  a disabled state, which is exactly why step 1a needs that outcome value.

Exit non-zero on failure. Emit the contract's JSON schema alongside human output.

Divergence from precedent, stated honestly: `skills/html-doc/scripts/check.py` is 209 lines,
stdlib-only, static analysis of source. This one needs a real browser. Accept the
dependency; the `--static` fallback idea is dropped, since a fallback that silently skips
most rules produces a score that isn't comparable to the full run.

**Two input modes:**

- `audit.mjs path/to/file.html` — single-file, the common case.
- `audit.mjs --url http://localhost:3000/route` — for React/Next work, where the caller
  builds and serves. Without this, the gate is useless on most real work.

### Step 2 — baseline, scored (half a day)

**4 briefs, 3 runs each**, in isolated fixtures, under the step 1a envelope.

n=3 is not a statistical guarantee — it is the point where run-to-run range becomes visible,
which is what the median-and-range reporting uses. Cutting to n=2 while demanding tighter
controls would be backwards: the range is the control.

The four briefs, chosen to span the failure surface rather than the app surface:

1. Marketing landing page — hierarchy, type scale, personality.
2. Form-heavy settings screen — states, focus, labels, error handling.
3. Data table with empty and error states — density, alignment, edge states.
4. Mobile-first list view — the 390px breakpoint, tap targets.

Artifacts, all tracked under `evals/`: briefs, JSON scores, run JSONL, and a compressed
labelled contact sheet per brief with generation metadata. Screenshots are the evidence for
the sameness verdict, so they cannot live only in scratch.

### Step 3 — reference arm (2 hours)

Same 4 briefs × 3 runs through Claude Code on Opus.

**State what this compares.** Not two models under controlled conditions — Claude Code and
Codex differ in system prompt, skill set, tools and autonomy. This is an end-to-end
*workflow* comparison: "the output I get from Codex" versus "the output I get from Claude",
which is the decision actually being made. Any claim of the form "Opus is better at
frontend" is out of scope for this eval.

### Step 4 — build (2 days)

Informed by where steps 2-3 actually failed, not where failure was assumed.

**4a. `assets/kit.css`** — real tokens with real values. Spacing scale, type scale, state
layers, focus rings, motion durations. Not "pick 4-6 hex values". Precedent:
`skills/html-doc/assets/base.html` (808 lines of shipped CSS, not described CSS).

**4b. `assets/components.html`** — start with the five the briefs exercise: nav, card, form
(labelled, with error state), button in all five states, table. Hero, footer, empty and
error states only if step 2 shows they're where Codex fails. Every component passes
`audit.mjs` at both widths before it ships.

**4c. `references/banned.md`** — prohibitions, since weaker models follow "never do X" far
better than "consider whether Y serves the brief". Content **copied in** from, in quality
order: hyperframes `house-style.md`, the banned-filler list in `frontend-app-builder`,
Anthropic's three AI-default clusters, and `skills/html-doc/references/anti-patterns.md`.
The first two live in the `.tmp` catalogue cache — copy, don't reference, and check the
licence first.

**4d. `references/directions.md`** — **axes with constraints, not presets.** 12 fixed
directions means output clusters into 12 recognisable buckets: a new sameness, and now it's
your signature. Enumerate independently — 12 palettes × 6 type stacks × 4 radius/density
profiles — but give each entry a `compatible-with` field so a display serif can exclude the
tightest density profile. Constrained composition, not pre-baked bundles.

The selection mechanism matters more than the list. **`shuf` and `gshuf` are not installed
on this machine** — the first draft's mechanism simply fails. Selection runs in the pinned
Node harness from step 1b:

```
node scripts/pick-direction.mjs --seed <seed>
```

It prints the three indices and the seed. The seed is recorded in the run metadata, so any
output can be regenerated. Codex has no RNG and no state; told to "pick an index" it picks
1 or 7 every time, which is why this cannot be left to the model.

**4e. Forced render-verify loop.** Not "critique your work as you build" — Codex will report
success without looking. A numbered checklist against a real screenshot at both widths, with
`audit.mjs` output pasted as evidence before any completion claim. `frontend-app-builder`
demonstrates the pattern (demanding `view_image` before claiming a match) even though it
isn't live here.

**4f. Codebase branch, stated explicitly in SKILL.md.** Most small/medium work is React +
Tailwind with existing tokens, where `kit.css` is inapplicable and copying it in violates
the standing rule to reuse the project's tokens. So:

- Greenfield single-file or prototype → use `kit.css` + `components.html` directly.
- Existing codebase → read its tokens first. Only `banned.md` and `audit.mjs` transfer.

### Step 5 — re-run and compare (half a day)

Same 4 briefs, same 3 runs, same envelope.

- **Craft:** median audit score with range, baseline vs post-build vs reference arm. This is
  the decision data. Any guidance whose corresponding rule didn't improve gets **cut, not
  expanded**. A rule that scored `not-applicable` throughout gets cut too — it measured
  nothing.
- **Sameness:** the audit cannot see this. From the labelled contact sheet, check that
  palette, type and density differ across the 3 runs of the *same* brief. This tests only
  that randomisation fired — three different-looking outputs can all be bad, so it is a
  liveness check on the mechanism, not a quality verdict. No blinding: there is one rater,
  who knows which arm is which, and blinding at n=12 is ceremony.

Step 5 is the one that will be tempting to skip. Skipping it means shipping unfalsifiable
advice, which is how the 12 existing design skills got their current shape.

### Step 6 — routing, as separate commits (1 day)

Only after step 5 shows movement. Doing it earlier means reverting a broad global-config
change if the kit doesn't pan out.

**6a. `install.sh` gains a `CLAUDE_ONLY` list** (see above). Without it, nothing in 6b is
Codex-only. Verify by re-running `install.sh` and confirming the named skill is present in
`~/.claude/skills` and absent from `~/.agents/skills`.

**6b. The 2% cleanup.** `AGENTS.md` records that Codex caps skills at 2% of context and
truncates every description once that budget fills, so a bloated set degrades discovery
across the whole library. Thirteen frontend-adjacent entries currently reach Codex with
overlapping descriptions and no stated boundaries.

- One frontend entrypoint that routes onward by name; every sibling gains an explicit
  negative-scope clause.
- Skills that can't justify a Codex slot go on the `CLAUDE_ONLY` list. `skills/_archive/`
  stays reserved for skills retired from *both* agents (precedent:
  `skills/_archive/web-design-guidelines`).
- `frontend-design` is a plugin: `enabled = false` in `~/.codex/config.toml`. Claude keeps
  it.

**Rollback:** 6a and 6b are separate commits. Revert, re-run `install.sh`, restore the
`config.toml` toggle. Record the toggle's prior value before flipping it — `config.toml` is
untracked.

### The emil/apple question — settled by step 0, not by ablation

Whether `emil-design-eng` (674 lines) and `apple-design` (282 lines) are load-bearing for
Codex or Opus-only material.

The first draft proposed an ablation. It isn't runnable: Codex has no `skillOverrides`
equivalent, so "unreachable" means mutating live global config mid-eval, and skill loading
is nondeterministic enough that the two arms can be identical by accident.

Use the step 0 JSONL instead — it records what Codex actually loaded across ~20 runs. If
neither appears, they go on the `CLAUDE_ONLY` list with no ablation needed. If they do
appear, ablate then, on 3 runs of one brief, with the JSONL confirming the arms differ.

## Fallback: split the work by failure mode

Triggered by step 0 failing, or by step 3 showing the residual gap is taste rather than
craft.

Codex implements and verifies; Opus supplies direction and the final critique. Codex
receives a concrete direction artifact (the three indices plus the token values), implements
against existing project tokens, runs the axe/geometry gate, and hands the rendered
screenshots back for one Opus critique pass.

This wins where the gap is judgment, not construction: no global skill-budget surgery, no
random-skin failure mode, and far less to maintain. It also keeps `audit.mjs` and
`banned.md`, which are the two artifacts that carry their weight regardless of routing.

Second fallback, cheaper still: route frontend work to Opus entirely and stop. Steps 0-3
cost about two and a half days and answer this directly — if the reference arm is far ahead
*and* step 0 shows Codex ignoring frontend skills, abandon the kit and route instead.

## Time

| Step | Estimate |
| --- | --- |
| 0 — invocation probe | 2 hours |
| 1a — evaluation contract | half a day |
| 1b — pinned runtime | 2 hours |
| 1c — `audit.mjs` | half a day |
| 2 — baseline | half a day |
| 3 — reference arm | 2 hours |
| 4 — build | 2 days |
| 5 — compare | half a day |
| 6 — routing + installer change | 1 day |

About five and a half days. Steps 0-3 (two and a half days) are the go/no-go — do not start
step 4 without baseline numbers.

## Verification

- **Craft:** post-build median audit score beats baseline on all 4 briefs by more than the
  observed run-to-run range, and closes at least half the gap to the reference arm.
- **Gate correctness:** `audit.mjs` passes on `assets/components.html` and fails on a
  deliberately broken copy — one broken fixture per rule, so a silently-dead rule is caught.
- **Contract correctness:** no rule reports `not-applicable` across all 12 baseline runs.
- **Sameness:** 3 runs of the same brief differ in palette, type and density, and the
  recorded seed reproduces a given run.
- **Invocation:** the 10 step-0 phrasings resolve to one owner, re-run after step 6.
- **Installer:** a `CLAUDE_ONLY` skill is present in `~/.claude/skills` and absent from
  `~/.agents/skills` after `install.sh`.
- **Hygiene:** `codex exec "list skill names"` shows each name exactly once.
- **Codebase branch:** the skill run against an existing Tailwind project reads that
  project's tokens and does not inject `kit.css`.
