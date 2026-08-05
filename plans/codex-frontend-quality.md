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
axes by a shell-generated random index, not by the model's taste. Codex gets structure
wrong and gets personality samey, so constrain the first and randomise the second. Never
ask it to "be original" — that instruction is what produces the clustering.

## Two things this plan cannot assume

**That a new skill gets loaded.** Everything below is inert if Codex doesn't reach for it.
The 2% truncation problem (see Routing) is a direct argument that it might not. Step 0
tests this before anything is built.

**That output is comparable run to run.** Codex varies. A single generation per brief
cannot separate a real improvement from noise, and "cut the guidance that didn't move the
needle" applied to n=1 is exactly the unfalsifiable-advice failure this plan exists to
avoid. The gate script is therefore built *before* the baseline, so scoring is mechanical
and repeats are cheap.

## What reaches Codex today — corrected inventory

Verified against `~/.agents/skills` symlinks and `~/.codex/config.toml` plugin toggles:

| Reaches Codex | Does **not** reach Codex |
| --- | --- |
| `apple-design`, `emil-design-eng`, `design-craft`, `design-foil`, `prototype`, `pick-ui-library`, `ux-writing`, `animation-vocabulary`, `find-animation-opportunities`, `improve-animations`, `review-animations`, `html-doc` (repo skills, symlinked) | `hyperframes` — present in the marketplace cache, **not enabled** in `config.toml` |
| `frontend-design@claude-plugins-official` — **enabled**, `~/.codex/config.toml:99-100` | `frontend-app-builder` — ships inside the `build-web-apps` plugin, **not enabled** |

Consequences the original plan got wrong:

- `~/.codex/.tmp/plugins/plugins/` is a marketplace *catalogue* cache (hundreds of entries),
  not the installed set. Nothing in it is live, and `.tmp` can be wiped. Anything used from
  there must be **copied into the repo**, never referenced by path.
- The real house-style file is
  `~/.codex/.tmp/plugins/plugins/hyperframes/skills/hyperframes/house-style.md`
  (not `.../hyperframes/house-style.md`).
- `frontend-design` is the most likely incumbent to win "make this UI feel better" and was
  missing from the inventory entirely. Being a plugin, it cannot be moved to
  `skills/_archive/`; the lever is `enabled = false` in `~/.codex/config.toml`, which
  removes it from Codex only and leaves Claude untouched.

## Sequencing

### Step 0 — invocation probe (30 min, gates everything)

Run ~10 phrasings through `codex exec` and record which skill Codex actually loads:
"build me a landing page", "make this UI feel better", "style this form", "the spacing here
is off", "give this page some personality", and five more in the user's own words.

Then repeat with a stub `frontend-kit` skill present (SKILL.md, description only, no body).

- **If the stub wins most phrasings** → continue to step 1 as written.
- **If incumbents keep winning** → switch to the `AGENTS.md` route (see Fallback) before
  building anything. `AGENTS.md` is auto-loaded every Codex session: no discovery, no 2%
  budget, no truncation. Guaranteed context beats better content that never loads.

Log the loaded-skill list per run. This log is also the only honest way to run the
emil/apple question later.

### Step 1 — `scripts/audit.mjs`, the measuring instrument (1 day)

Build the gate *first*. Nothing after this is falsifiable without it.

Playwright + headless Chromium (`chromium-1228` is already cached, `playwright` python is
installed; the mjs version needs `npx playwright`). Against rendered output, not source:

- contrast below WCAG AA
- missing `:focus-visible` on interactive elements
- horizontal overflow at 390px
- tap targets under 44px
- heading hierarchy skips
- interactive elements with no hover/active/disabled distinction
- computed font-size below 14px
- layout shift between 390px and 1440px

Exit non-zero on failure. Emit JSON alongside human output so eval runs can be aggregated.

Note the honest divergence from precedent: `skills/html-doc/scripts/check.py` is 209 lines,
stdlib-only, static analysis of HTML source. This one needs a real browser for computed
styles. Accept the dependency, but document the fallback — a `--static` mode covering the
checks that don't need layout (heading skips, font-size in CSS, missing focus rules), so
the gate still runs where Playwright isn't installed.

**Two input modes**, decided up front:

- `audit.mjs path/to/file.html` — single-file, the common case.
- `audit.mjs --url http://localhost:3000/route` — for React/Next work, where the caller is
  responsible for build + serve. Without this, the gate is useless on most real work.

### Step 2 — baseline, scored (half a day)

**4 briefs, not 8**, run **3× each**. Mechanical scoring is what makes repeats affordable,
and n=3 is the minimum that distinguishes signal from variance.

The four, chosen to span the failure surface rather than the app surface:

1. Marketing landing page — hierarchy, type scale, personality.
2. Form-heavy settings screen — states, focus, labels, error handling.
3. Data table with empty and error states — density, alignment, edge states.
4. Mobile-first list view — the 390px breakpoint, tap targets.

For each run: `audit.mjs --json` score, plus screenshots at 390 and 1440.

Artifacts: briefs and JSON scores go in a tracked `evals/` at the repo root. Screenshots go
to the session scratchpad — they are the qualitative check, not the record.

### Step 3 — reference ceiling (2 hours)

Same 4 briefs × 3 runs through Opus, same scoring. This sets the target and shows which
briefs Codex is already fine at, so effort goes where the gap is. If Codex's audit score
already matches Opus's on a brief, the remaining gap there is sameness, not craft — a
different fix.

### Step 4 — build (2 days)

Informed by where steps 2-3 actually failed, not where failure was assumed.

**4a. `assets/kit.css`** — real tokens with real values. Spacing scale, type scale, state
layers, focus rings, motion durations. Not "pick 4-6 hex values". Precedent:
`skills/html-doc/assets/base.html` (808 lines of shipped CSS, not described CSS).

**4b. `assets/components.html`** — start with the five the briefs exercise: nav, card, form
(labelled, with error state), button in all five states, table. Hero, footer, empty and
error states are added only if step 2 shows they're where Codex fails. Every component
passes `audit.mjs` at 390px and 1440px before it ships.

**4c. `references/banned.md`** — prohibitions, since weaker models follow "never do X" far
better than "consider whether Y serves the brief". Content **copied in** from, in quality
order: hyperframes `house-style.md`, the banned-filler list in `frontend-app-builder`,
Anthropic's three AI-default clusters, and `skills/html-doc/references/anti-patterns.md`.
Both of the first two live in the `.tmp` catalogue cache — copy, don't reference.

**4d. `references/directions.md`** — **axes, not presets.** 12 fixed directions means output
clusters into 12 recognisable buckets: a new sameness, and now it's your signature.
Instead enumerate independently: 12 palettes × 6 type stacks × 4 radius/density profiles.

The selection mechanism matters more than the list. Codex has no RNG and no state; told to
"pick an index" it picks 1 or 7 every time. The skill must instruct an actual shell call:

```
shuf -i 1-12 -n 1   # palette
shuf -i 1-6  -n 1   # type stack
shuf -i 1-4  -n 1   # radius + density
```

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

Same 4 briefs, same 3 runs, same widths.

- **Craft (failure mode 1):** `audit.mjs` score, baseline vs post-build vs Opus ceiling.
  Objective, so this is the decision data. Any guidance whose corresponding check didn't
  improve gets **cut, not expanded**.
- **Sameness (failure mode 2):** the audit cannot see this. Lay the 12 post-build screenshots
  side by side and check that palette, type and density actually differ across runs of the
  *same* brief. If three runs of brief 1 look like each other, the randomisation isn't
  firing — check the `shuf` calls actually ran.

Step 5 is the one that will be tempting to skip. Skipping it means shipping unfalsifiable
advice, which is how the 12 existing design skills got their current shape.

### Step 6 — routing, as a separate commit (half a day)

Only after step 5 shows movement. Doing it earlier means reverting a broad global-config
change if the kit doesn't pan out.

The 2% problem: `AGENTS.md` records that Codex caps skills at 2% of context and truncates
every description once that budget fills, so a bloated set degrades discovery across the
whole library. Thirteen frontend-adjacent entries currently reach Codex with overlapping
descriptions and no stated boundaries.

- One frontend entrypoint that routes onward by name; every sibling gains an explicit
  negative-scope clause.
- Anything that cannot justify its slot for Codex specifically moves to `skills/_archive/`
  (precedent: `skills/_archive/web-design-guidelines` is already there).
- `frontend-design` is a plugin, so it is disabled for Codex via `enabled = false` in
  `~/.codex/config.toml` — not archived. Claude keeps it.

**Rollback:** one commit for the archive moves plus one `install.sh` re-run (needed for
adds, renames and deletes; a symlink-only edit is live immediately). Revert the commit,
re-run `install.sh`, restore the `config.toml` toggle. Note down the toggle's prior value
before flipping it, since `config.toml` is untracked.

### The emil/apple question — deferred, not dropped

Whether `emil-design-eng` (674 lines) and `apple-design` (282 lines) are load-bearing for
Codex or Opus-only material. The original plan proposed an ablation in the baseline: run
step 2 twice, once with them reachable and once without.

**That ablation is not runnable as stated.** Codex has no `skillOverrides` equivalent
(`AGENTS.md`), so "unreachable" means moving symlinks out of `~/.agents/skills` and back,
mutating live global config mid-eval. Worse, skill loading is nondeterministic — the two
arms can be byte-identical by accident, and you'd never know.

Use the step 0 log instead: it records which skills Codex actually loaded per run, across
~20 runs. If neither appears, they're Opus-only and become Claude-only without any ablation.
If they do appear, run the symlink ablation then, on 3 runs of a single brief, with the
loaded-skill log confirming the arms actually differ.

## Fallback: `AGENTS.md` instead of a skill

Triggered by step 0 failing. A ~30-line frontend block in `AGENTS.md`: the banned list, "run
`audit.mjs` and paste its output before claiming done", and the path to `kit.css`.

Wins because `AGENTS.md` is auto-loaded every Codex session — no discovery, no 2% budget, no
truncation, no competing skills. It trades content quality for guaranteed presence, which is
the right trade if the failure is guidance not reaching the model rather than guidance not
existing.

Cost: it's global, so it burns context on backend sessions too. Keep it to 30 lines and gate
the detail behind file paths the model reads only when relevant.

## The option not taken

Route frontend work to Opus and stop. If the gap is a model-capability gap on taste, five
days of scaffolding is worse value than `codex → claude` for UI tasks. Steps 0-3 cost about
two days and answer this directly: if the ceiling run shows Opus far ahead on audit score
*and* the baseline shows Codex ignoring frontend skills, abandon and route instead.

## Time

| Step | Estimate |
| --- | --- |
| 0 — invocation probe | 30 min |
| 1 — `audit.mjs` | 1 day |
| 2 — baseline | half a day |
| 3 — ceiling | 2 hours |
| 4 — build | 2 days |
| 5 — compare | half a day |
| 6 — routing | half a day |

About five days total. Steps 0-3 (two days) are the go/no-go — do not start step 4 without
baseline numbers.

## Verification

- **Craft:** post-build `audit.mjs` scores beat baseline on all 4 briefs, and close at least
  half the gap to the Opus ceiling.
- **Gate correctness:** `audit.mjs` passes on `assets/components.html`, and fails on a
  deliberately broken copy — one check per rule, so a silently-dead rule is caught.
- **Sameness:** 3 runs of the same brief differ in palette, type and density.
- **Invocation:** the 10 step-0 phrasings resolve to one owner, re-run after step 6.
- **Hygiene:** `codex exec "list skill names"` shows each name exactly once.
- **Codebase branch:** the skill run against an existing Tailwind project reads that
  project's tokens and does not inject `kit.css`.
