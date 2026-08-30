# Design doctrine overhaul

**Date:** 2026-08-31
**Branches:** `agent-config@design-setup-overhaul`, `repertory@design-rebuild`
(both pushed)

## Why this happened

Sudaksh was invoking `/frontend-craft`, `/typography-craft` and `/design-foil` and
getting unusable UI. First pass this session added skills and a render gate, then
rebuilt Repertory's programme screen. **It passed every gate and was still bad.**
That is the real finding.

Diagnosis: the skills measured absence of defects and never stated what a good
screen *has*, and the doctrine underneath was written for editorial artifacts, not
product screens. Set against Airbnb and Linear, almost every rule pointed the wrong
way — a "signature element" and a second family for metrics where the reference
uses one family and nothing distinctive; hairline rules where the reference uses
whitespace; no mention of an app shell anywhere in any skill.

Every visible defect traced to a rule I had written.

## What changed — agent-config

- **Archived** `skills/nightjar/` and `skills/frontend-craft/` to `archive/skills/`.
  Sudaksh is remaking both. Marketing pages now go to Anthropic's `frontend-design`
  plugin, re-enabled in `plugins.txt` in that narrower role. Decks and reports fall
  to `artifact-design` — a real gap until nightjar returns.
- **New `skills/app-ui/`** — the positive doctrine. What a screen has: a shell with
  named slots, unit choice by content shape, one primary action plus overflow, a
  modular type scale at a stated ratio, one spacing base unit, whitespace before
  rules, the decision-carrying medium leading, every state designed, words as
  design material. Carries a direction override: on a product screen, unsurprising
  is the goal, and this skill beats any anti-slop guidance.
- **`skills/design/` renamed to `skills/design-brief/`** — it was colliding with
  Claude Code's bundled `design` skill (the canvas artifact one). The anchor is now
  a procedure with file paths, not a word.
- **`skills/design-review/`** gained a P0 tier for *absence* and a pass condition a
  defect list cannot reach: beside the reference, could a stranger tell which one
  shipped. `references/slop.md` scoped to marketing surfaces.
- `skills/interface-composition/` demoted to the arithmetic pass that runs *after*
  `app-ui`. `global-agents.md` exempts design work from smallest-change and
  never-rename, and adds "before claiming a visual result is good, look at it".

## What changed — repertory

- `design-overhaul` — Linear established as the anchor. `design/reference/` holds
  `linear-list.png` and `linear-detail.png`, captured from Mobbin. `DESIGN.md`
  rewritten as the brief; `AGENTS.md` carries the binding subset.
- `design-rebuild` — the teardown. `App.tsx` and every presentational component
  removed; `index.css` 341 → 141 lines. Tokens, dark mode, focus rings,
  reduced-motion survived. **150 tests still pass** across api, cache, sse,
  validate and reducer.

## Decisions and why

- **Anchor must be a shipping product in the same medium doing the same job, held
  as images on disk.** The first pass used "a printed repertory-cinema programme",
  which is why the screen had no navigation. A name is an adjective; an image is a
  brief.
- **No anchor is named in any skill.** Writing "Airbnb" or "one family" into a
  general skill overfits every future project. Conventions come from research;
  project choices live in that project's `DESIGN.md`.
- **Repertory's list is posterless.** Measured: 3 of 70 films have a poster (4.3%),
  and the newest slate is 3 of 5. A 40% miss on five rows is two grey boxes every
  night. The blurb carries the visual weight. Poster plumbing stays in the backend.
- **All four ratings stay visible** — no hover-only data, the app is used on a phone.
- **Rail: Tonight / History / Watchlist**, which requires two new endpoints.
- **Fonts removed.** Archivo and Martian Mono were chosen for the dead anchor.
  Files remain in `frontend/public/fonts/` for the rebuild to adopt or delete.

## Current state

Everything is committed and pushed. Nothing is half-done in agent-config.

`repertory@design-rebuild` **does not build** — intentional. `main.tsx` imports a
deleted `App.tsx`. Tests and the Python side are unaffected.

Known open items, all recorded in `repertory/handoff/2026-08-31-frontend-rebuild.md`:

- `/api/history` and `/api/watchlist` do not exist. Data and loaders do
  (`recommend` slate loaders, `watchlist.load()`). Roughly 60–80 lines plus tests.
- No empty-state reference captured.
- `humanizer` is 30KB, over the 20KB lint warning threshold. Pre-existing.
- The four `claude-in-chrome` permissions added to `settings.json` are inert unless
  that MCP is enabled for the project (`/mcp`).

## Next action

Rebuild the Repertory frontend in a **fresh session**, driven by `/design-brief`,
with no turn-by-turn steering. A rebuild that gets hand-held proves nothing about
whether the skill changes worked. Then run `/design-review` and judge the result by
eye.
