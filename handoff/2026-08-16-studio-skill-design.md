# Handoff: `studio` skill — design settled, build not started

Session of 2026-08-16. Research and design decisions are complete across four
rounds of grilling. **No skill code has been written yet.**

## What changed on disk

One file created:

- `docs/2026-08-16-studio-reference-values.md` (16KB) — verified reference values
  for all seven design references, cross-reference findings, grouping verdict,
  prior-art table with the StyleSeed benchmark, packaging mechanics, font
  inventory, and the settled decisions.

Nothing committed. Nothing staged. No skill directory exists yet.

Scratch only, safe to delete: `/tmp/studio-probe/` (render-gate probe page and
two screenshots).

## What `studio` is

One skill replacing `frontend-craft` and `html-doc`. It holds a small registry of
named design directions. The user names a direction, or the skill suggests one,
and it builds a standalone HTML artifact against that direction, then renders it,
scores it, and revises once before handing it over.

The problem it solves: Claude Code and Codex produce ugly pages when asked for a
self-contained HTML explainer or a landing page, and prose guidance alone does not
fix it.

## Settled decisions

### Packaging

- **A skill, not a plugin.** `install.sh:149-154` already symlinks
  `skills/*/SKILL.md` into `~/.claude/skills` and `~/.agents/skills`. A plugin
  buys namespacing and third-party install, neither of which is needed. Adding
  `.claude-plugin/marketplace.json` later requires moving no files.
- **Named `studio`.** The user's own word; `plans/2026-08-01-statusline-kohra.md:7`
  calls the token set "the studio tokens".
- Per-direction material must be plain `.md`. `install.sh` scans one level deep,
  so a nested `SKILL.md` would not register as a skill.

### Retirements

- **`frontend-craft` retires into `studio`.** Its labelled 8-item aesthetic menu
  is what the registry replaces. Its operator-context and voice sections move
  across. `agents/frontend-craft.md` is a separate Opus subagent pointing at the
  skill and needs repointing.
- **`html-doc` retires into `studio`.** Three of its load-bearing rules conflict
  with what the user wants: Hard Rule 1 bans webfonts (`SKILL.md:50-52`), Phase 0
  forbids asking questions (`:108-111`), and its determinism thesis (`:23-25`)
  is the opposite of varying by design direction.
  **Port across:** the 15-primitive document vocabulary (`:116-119`),
  `references/anti-patterns.md`, `scripts/check.py`, and the never-invent-data
  and never-rewrite-the-source rules. **Drop:** the three themes, the
  no-webfonts rule, the no-questions rule.
- **`typography-craft` stays** as the specialist. It owns print, brand identity
  and display type, which `studio` will never cover. `studio` routes to it.
- **`frontend-design` gets disabled** in `plugins.txt:27`. It is prose-only
  guidance, the category the benchmark showed does nothing.
- Known references to update: `skills/README.md:65` and `:88-90` (which states a
  "nine-skill count" that changes), and `skills/frontend-craft/SKILL.md:122`.

### Structure

- **3-4 monolithic `DESIGN.md` files**, one per direction. The user rejected a
  language × grammar matrix.
- **Artifact-shape rules live once in `SKILL.md`**, not repeated in each
  `DESIGN.md`, because composition of a document does not change between
  directions.
- **Two artifact shapes in v1: document and page.** Both standalone HTML the
  render gate can check.
- **React and Tailwind app UI is out of scope** for v1. It needs shadcn token
  mapping and cannot be verified by screenshotting one file.
- **Vocabularies are open starting sets, not closed lists.** The user reversed an
  earlier decision to close the page vocabulary at ten primitives, on the grounds
  that it is too restrictive. Discipline instead comes from the anti-patterns
  reference, each direction's avoid-list, and the mechanical checks. The check
  script warns on a novel selector rather than failing, matching what
  `html-doc`'s `check.py` already did.

### The four directions

Chosen for widest range, one per corner, confirmed by measured values:

| Direction | Reference | Character |
| --- | --- | --- |
| `editorial` | New Yorker, plus the user's own VC Design Standards language | light, two families, no negative tracking, almost no radius |
| `instrument` | Ramp | white ground, one accent, bordered cards, zero shadow |
| `product-dark` | Linear | `#08090A`, alpha-tint elevation, white-alpha hairlines |
| `calm` | Headspace | warm ground, one family, flat colour fields, large radii |

**Casualties, accepted knowingly:** Mercury, Origin and V7 do not make the cut.
Dark glass and hard-edge-serif both lose to Linear for the single dark slot.

**Kohra sits outside the roster as the eventual default.** Its palette exists
(`~/dev/kohra/themes/kohra.superset.json`, 1977 bytes) but covers terminal and
editor UI slots only. No type scale, spacing, radius or surface ladder. Until
Kohra is built, the skill **asks** rather than defaulting.

The `editorial` direction should start from the user's **VC Design Standards**
project language, already in production: OKLCH paper/ink palette, Source Serif 4
/ Hanken Grotesk / IBM Plex Mono, 64ch measure. The New Yorker is the reference
it gets measured against, not copied from.

### Fonts

- **Blacklist only, no whitelist.** The user removed the whitelist so anything not
  banned is available, and he adds to the blacklist as he finds things he dislikes.
- **Banned:** Poppins, Montserrat, Raleway, Lato, Open Sans, Nunito, Quicksand,
  Playfair Display, Oswald, Bebas Neue, Comfortaa, Josefin Sans, Roboto, Space
  Grotesk, Manrope, DM Sans, DM Serif, Instrument Sans, Instrument Serif,
  Fraunces.
- **Inter is body and UI only, never display.** Inter at 72px in a hero is the
  loudest "an agent made this" signal.
- **Paid fonts are this-machine-only**, for print or eyes-only artifacts. Anything
  public defaults to free faces unless licensing is sorted.
- The skill asks one line, free pre-selected: *"Free fonts (safe to share) or your
  licensed set (this machine only)?"*
- Held as `woff2` today: Söhne, National 2, Berkeley Mono, plus free Literata,
  Newsreader, Inter, JetBrains Mono, all under `homelab/stacks/static/fonts`.
  Desktop only: Mallory, Tiempos Text, Halyard, Atkinson Hyperlegible Next.
  **Not present in any form:** Mercury, Whitney, Archer, Verlag, Knockout, Gotham,
  Domaine, Harriet, despite `frontend-craft` listing them as the user's library.
- Preferred delivery for shareable artifacts: **base64-embed the subset `woff2`
  inline** rather than linking Google's CDN. Two Latin-subset faces are roughly
  100KB after base64 and the file stays self-contained.

### The render gate

Mandatory and blocking. Render at 390 and 1440, run the mechanical check, score,
revise once if it fails, re-render. On a second failure, ship the file and name
the failing checks out loud. Never silently pass.

Scoring runs against both a universal rubric and the direction's own avoid-list,
weighted toward the avoid-list, because the universal rubric is what makes
everything average.

**Verified working this session:**

```
playwright screenshot --viewport-size=390,844 page.html shot-390.png
playwright screenshot --viewport-size=1440,900 page.html shot-1440.png
```

Both shots in 1.28s. `playwright` 1.59.0 is on PATH via Homebrew, Chromium cached
at `~/Library/Caches/ms-playwright`. The resulting PNG can be read back and
judged. No MCP server, no Chrome extension, no new dependency.

**Two constraints this imposes:**

1. **The gate cannot run in a subagent.** A subagent's Playwright launch hit
   sandbox `EPERM` while the same binary worked from the main agent. `studio` must
   not delegate its own verification.
2. **Use the CLI, not a Node or Python wrapper.** One binary already on PATH. The
   static check stays stdlib Python.

### Anti-slop

One script, two halves. Mechanically detectable failures fail with line numbers:
two-hue gradient in a hero, exactly three sibling cards, one uniform radius on
every element, emoji in headings, filler words, a centred 1200px container as the
only layout idea, blacklisted font families. Judgement stays prose in each
direction's avoid-list.

## Planned file layout

```
skills/studio/
  SKILL.md
  references/
    anti-patterns.md     ported from html-doc, generalised beyond documents
    vocabularies.md      document and page starting sets, open not closed
    fonts.md             blacklist, Inter rule, local licensed inventory
  directions/
    editorial/     DESIGN.md  tokens.css  example.html
    instrument/    DESIGN.md  tokens.css  example.html
    product-dark/  DESIGN.md  tokens.css  example.html
    calm/          DESIGN.md  tokens.css  example.html
  scripts/
    check.py       ported from html-doc, extended to pages
    render.sh      playwright screenshots at 390 and 1440
```

Each `DESIGN.md` needs the same section order so the four stay interchangeable:
thesis, when to use and when not, reference values, ground and ink, surface ladder
with how elevation is signalled, type roles table, radius scale, accent policy,
spacing rhythm, signature move, avoid-list, token map.

`tokens.css` needs a fixed custom-property vocabulary across all four directions
or they will not be swappable. Proposed: `--ground`, `--ground-2`, `--ground-3`,
`--ink`, `--ink-2`, `--ink-3`, `--hair`, `--accent`, `--accent-ink`,
`--radius-sm|md|lg|pill`, `--font-display|body|mono`,
`--text-base|h1|h2|h3|small`, `--leading-body|display`,
`--track-display|body`, `--measure`, `--space-1` through `--space-8`,
`--shadow-1` (which may legitimately be `none`).

## Measured findings worth not rediscovering

Full values in `docs/2026-08-16-studio-reference-values.md`. The four that most
change how a direction gets written:

1. **Nobody uses blur for elevation.** Ramp uses a 1px border and no shadow.
   Linear uses `0 0 0 1px` and `0 0 0 2px` rings. V7 uses nothing. The agent
   default of `0 4px 6px rgba(0,0,0,0.1)` matches none of the seven references.
2. **Tracking separates the references more than typeface does.** New Yorker is
   `normal` at 42px, Ramp −0.01px at 64px, Linear −0.022em, V7 and Headspace
   −0.03em. The editorial reference has zero negative tracking, the opposite of
   the default instinct.
3. **Family count is one or two, never more.** Display weight is rarely bold: 300
   at Origin and V7, 400 at Ramp and New Yorker, 480 at Mercury, 510 at Linear.
   Only Headspace uses 700.
4. **Mercury is dark, not light** (`#171721` with 20px backdrop blur). Ramp is the
   only light non-editorial reference in the set.

## Prior art

`bitjaru/styleseed` is what "styleseed" means. MengTo has no design plugin; the
real artefact is `MengTo/Skills`, whose demo contract pairs each skill with
`demo/index.html`, a 1280×720 `preview.jpg`, and a `PROMPT.md` that recreates it.
Also relevant: `VoltAgent/awesome-design-md` and `Laith0003/ux-skill`.

The one measured claim, from StyleSeed's own benchmark over 120 rendered cells:
rules alone were noise (Codex +1.6, Claude −3.7), the enforced render-score-revise
loop was +5.3 for both. Self-published, unreplicated. Distinctiveness remained the
lowest-scoring category, so nobody has solved "not generic".

## Current state

Design is fully settled. Build has not started. The session ended immediately
after the todo list was initialised, before any skill file was created.

The user's last two instructions, both of which supersede earlier plans:

- **Build all four directions together using subagents**, not one first. He
  changed his mind from the one-direction-first plan: "I can refine them later,
  I'll at least have a starting point."
- **Keep the vocabularies open.** Ten primitives for a page is too restrictive.

He also wants the remaining work filed in Linear so he can track it: team
**OKLCH** (the only team), project **Agent Config** (`bc426a18-8983-418a-8aec-21a8e76b648f`),
one issue per sitting, via the `backlog` skill with Priority and Estimate set.

## Watch out for

- **The pre-commit hook** (`.githooks/pre-commit`) rejects any commit where a
  changed skill's `dist/<skill>.zip` is stale, missing, or orphaned. Run
  `./scripts/build-zip.sh <skill>` for every changed skill and stage the zip.
  Retiring `frontend-craft` and `html-doc` means removing their orphan zips too.
- **`install.sh --prune`** is needed to clear dangling symlinks after a skill is
  deleted. Plain `install.sh` leaves them.
- Anthropic guidance is `SKILL.md` under 500 lines.
- `editorial` is the direction most likely to land on two of the three named AI
  defaults: cream ground with high-contrast serif and terracotta accent, and the
  broadsheet look. Paper/ink is the brief, but terracotta and a high-contrast
  serif display are not.

## Next action

Create `skills/studio/SKILL.md` plus the three `references/` files and the two
`scripts/` files, then dispatch four subagents in one batch to build the four
direction folders against the `DESIGN.md` section order and the shared
`tokens.css` property vocabulary above.
