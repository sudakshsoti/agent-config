# Studio: verified reference values and prior art

Research capture for the `studio` skill. **No design decisions here.** Round 3
questions are still open; this file exists so the evidence survives and the
eventual `DESIGN.md` files argue from measured values rather than adjectives.

Captured 2026-08-16.

## How these were verified

Computed styles read from headless Chromium at a 1440px viewport, via the
`playwright` 1.59.0 already on PATH. Custom properties resolved off `:root` or
the scoping element where the token layer is scoped rather than global.

Two exceptions, both labelled at the point of use:

- **New Yorker** values are *served CSS declarations*, not computed. A subagent's
  Playwright launch was blocked by sandbox `EPERM`; the served stylesheet was
  read instead.
- **Ramp homepage** returns a machine-readable Markdown fallback to non-browser
  requests, so `ramp.com/pricing` is the reliable computed page.

`origin.com` redirects to EA's PC games library. The financial product is
`useorigin.com`.

## Render gate viability

The render-score-revise loop needs no MCP server, no Chrome extension and no new
dependency:

```
playwright screenshot --viewport-size=390,844 page.html shot-390.png
playwright screenshot --viewport-size=1440,900 page.html shot-1440.png
```

Both shots complete in 1.28s total, and the resulting PNG can be read back and
judged. Chromium is cached at `~/Library/Caches/ms-playwright`.

**Two constraints this imposes on how `studio` is written:**

1. **The gate cannot run in a subagent.** Playwright launch from a subagent hit
   `EPERM` while the same binary worked from the main agent. `studio` must not
   delegate its own verification.
2. **Use the CLI, not a Node or Python wrapper.** One binary already on PATH, no
   `npm install`. The static check stays stdlib Python, as `html-doc`'s
   `scripts/check.py` already is.

## Reference values

### Ramp — `ramp.com/pricing`

The only light-ground reference in the set.

| Property | Value |
| --- | --- |
| Ground | white, `lab(100 0 0)` |
| Ink | `--text-primary: lab(2.83994% .367254 .969091)` |
| Family | Lausanne, one family throughout |
| H1 | 64px / 64px line-height, weight 400, tracking **−0.01px** |
| H2 | 48px / 50px, weight 400, tracking −0.01px |
| Body | 16px / 24px |
| Cards | transparent fill, 1px `lab(83.0178% 1.03405 2.01975)` border, radius 8px, padding 40px 32px, **no shadow** |
| CTA | `--grayLight` fill, ink at 60% opacity, radius 6px, padding 0 20px |
| Radius scale | `.25rem` `.375rem` `.5rem` `.75rem` `1rem` `1.5rem` |
| Accent | `--solar: lab(92.1406% -20.4979 84.7726)` |

Token layer is authored in **CIE Lab**, not hex or OKLCH. `--midnight` is
`linear-gradient(in oklab to bottom, #000 0%, #112d5b 100%)`.

### Linear — `linear.app`

| Property | Value |
| --- | --- |
| Ground | `#08090A` |
| Ink | `#F7F8F8` |
| Family | Inter Variable; **Berkeley Mono** for mono |
| H1 | 64px / 64px, weight **510**, tracking −1.408px (−0.022em) |
| Body | 16px / 24px, weight 400, tracking normal |
| Button | 13px / 19.5px, radius `9999px` |
| Surface ladder | `#08090A` → `#101112` → `#121314` → `#161718`, plus `rgba(255,255,255,0.01)` and `0.02)` tints |
| Borders | 1px `rgba(255,255,255,0.05)` and `rgba(255,255,255,0.08)` |
| Radius scale | 2, 4, 6, 7, 8, 12, 16, 22, plus `9999px` and `400px` pills |

Elevation is **not** blur. It is `0 0 0 1px rgba(0,0,0,0.2)` and
`0 0 0 2px rgba(0,0,0,0.1)` ring shadows, an inset `0 0 0 1px rgb(35,37,42)`,
and one `0 2px 4px rgba(0,0,0,0.4)`. Real blurs appear only on overlays:
`0 4px 32px rgba(8,9,10,0.6)` and `0 0 64px rgba(8,9,10,0.4)`.

The h1 weight of **510** is a variable-font instance, not a named weight.

Berkeley Mono is already held locally as `woff2` at
`homelab/stacks/static/fonts/berkeley-mono-{regular,bold}.woff2`.

### Mercury — `mercury.com`

Dark violet-neutral, **not** a light instrument surface.

| Property | Value |
| --- | --- |
| Ground | `#171721` (`#theme-switch-scroller`) |
| Ink | `#ededf3` |
| Family | Arcadia (body), Arcadia Display (display), Tiempos Headline (editorial) |
| H1 | 49.35px / 54.28px, weight **480**, tracking normal |
| CTA | fill `#5266eb`, white ink, radius **32px**, 16px / 16px, weight 420 |
| Frosted panel | `rgba(175,178,206,0.2)`, border `#afb2ce5c`, radius 32px, **backdrop-blur 20px** |
| Elevated card | `#272735`, radius 12px |
| Card shadow | `0 10px 16px rgba(28,28,35,.02)`, `0 6px 10px rgba(28,28,35,.04)`, `0 0 3px rgba(28,28,35,.09)` |

Scoped semantic tokens are `--surface-*`, not `--color-*`:
`--surface-default #1e1e2a`, `--surface-elevated #272735`,
`--surface-frosted #afb2ce33`, `--surface-primary #5266eb`,
`--surface-inverted #ededf3`, `--surface-elevated-hover #363644`.

Neutral ramp: `#10101a` `#171721` `#1e1e2a` `#272735` `#363644` `#535461`
`#70707d` `#9d9da8` `#c3c3cc` `#dddde5` `#ededf3` `#f4f5f9` `#fbfcfd`.

Secondary accents: green `#188554`, orange `#c45000`, red `#d03275`, blue
`#007f95`, beige `#c3b389`.

### Origin — `useorigin.com`

| Property | Value |
| --- | --- |
| Ground | `#0f1011` |
| Ink | `#fff`, h2 at `#fafafa` |
| Family | Suisse Int'l (body), Lyon Display (display), Roboto Mono (UI labels) |
| H1 | **96px**, weight 300, line-height 86.4px, tracking normal |
| H2 / H3 | 80px, weight 300, line-height 80px |
| Body | 16px / 24px |
| CTA | white fill, black ink, Roboto Mono 12px / 24px, radius 8px, height 48px, padding 12px 18px |
| Cards | `#e2e2e0` fill, radius 16px, padding 24px, 40px gaps |
| Radius scale | 8, 16, 24, 30, plus full-round glass pills |
| Accents | cyan `#00b3dd`, pink `#dd90d8`, lavender `#847dff` / `#d1c9ff`, blue `#4b49aa` / `#90b8f0` |

Measure is narrow: `.layout-block-container` is `max-width: 728px` on desktop.
Glass panels are `rgba(255,255,255,0.12)` and `rgba(255,255,255,0.19)` with
`rgba(255,255,255,0.15)` borders and 24px blur.

### V7 — `v7labs.com`

| Property | Value |
| --- | --- |
| Ground | `#1c1c1c` hero and bento; `#fff` page body |
| Family | **Martina Plantijn Light** (serif display), STK Bureau / STK Bureau Sans Book |
| H1 | 44px, weight **300**, tracking −1.32px (−0.03em), line-height 52.8px |
| H2 | 40px, weight 300, tracking −1.2px, line-height 48px |
| Bento panels | 440×388, **radius 0, no shadow, no border** |
| Pricing cards | 440×562, first `#ff683d`, rest `#f7f6f5`, **radius 0** |
| Translucent panel | `rgba(255,255,255,0.12)`, radius 8px |

A light-weight **serif** carrying display at heavy negative tracking, against
hard-edged panels. Loaded `woff2` are Framer-hashed, so filenames cannot be
mapped to families.

### New Yorker — Pope.L article *(served CSS, not computed)*

| Property | Value |
| --- | --- |
| Ground | `#fff`; inverted theme also declared at `#000` / `#121212` |
| Ink | `#000` |
| Display | `IrvinHeadingPro`, weight 400, standard headline 30px → 36px → **42px**, line-height 1.0667, **tracking `normal`** |
| Feature headline | 34px → 40.8px → 44.2px, line-height 1.13 |
| Body | `TNYAdobeCaslonPro`, **21px / 1.5em**, weight 400 |
| Feature body | 20px / 1.43 |
| Description | 21px / 1.3333, italic Caslon |
| Utility / nav | Graphik 12–13px, weight 400/500, tracking −0.0125em |
| Measure | grid columns 3 / span 8 of 12 at ≥768px |
| Ladder | `#fff` base, `#f5f5f5` subtle and hover, `#e5e5e5` 1px borders |
| Radius | almost nowhere: 4px table container, 50% avatar, 64px sticky utility |
| Accents | action blue `#0879bf`, pressed `#07588b`, rubric red `#db3334` |
| Spacing | 0.5, 1, 1.5, 2, 2.5, 3rem, 40px |

Two families, one display and one body, and **zero negative tracking anywhere**
including 42px headlines. Hero is a split screen: centred title block at
`max-width: 500px` beside a full-height `object-fit: cover` image.

### Headspace — `headspace.com`

| Property | Value |
| --- | --- |
| Ground | `#f9f4f2` warm off-white, and `#fff` |
| Ink | `#2d2c2b` display, `#4b4c4d` body |
| Family | **Headspace Apercu, single family**, weights 400 / 500 / 700 only |
| H2 | 52px / 57.2px, weight **700**, tracking −1.56px (−0.03em) |
| Body | 16px / 18.4px |
| Radius scale | 8, 12, 16, 24, 30, 32, 112, 800px, plus `24px 24px 0 0` one-sided |
| Shadows | `0 1px 8px rgba(20,19,19,.2)`, `0 2px 0 rgba(65,61,69,.2)`, `0 3.23px 6.45px rgba(20,19,19,.2)` |
| Colour fields | blue `#0061ef`, yellow `#ffce00`, pink `#ffa1cc`, purple `#3b197f`, green `#02873e`, cyan `#00a4ff`, warm dark `#44423f` |
| Illustration | 133 inline SVG against 114 `<img>` |

Play comes entirely from large flat colour fields and 24–112px radii. The type
is a tight-tracked grotesque at weight 700. The warm ground and warm near-black
ink are what stop it reading as childish.

## Cross-reference findings

**Nobody uses blur for elevation.** Ramp uses a 1px border and no shadow. Linear
uses `0 0 0 1px` and `0 0 0 2px` rings, which are borders in a shadow's clothing.
V7 uses nothing at all. New Yorker's article shell has none. Only Mercury and
Headspace blur anything, and Mercury's blurs are at 2–9% opacity. The agent
default of `0 4px 6px rgba(0,0,0,0.1)` on a card matches none of the seven.

**Tracking separates the references more cleanly than typeface does.** New Yorker
`normal` at 42px, Ramp −0.01px at 64px, Linear −0.022em, V7 and Headspace
−0.03em. The editorial reference has zero negative tracking, the opposite of the
default instinct when told "editorial".

**Family count is one or two, never more.** Ramp one, Headspace one, Linear one
plus mono, New Yorker one display plus one body plus a utility grotesque,
Mercury two plus an editorial third, Origin two plus a mono for labels.

**Display weight is rarely bold.** 300 at Origin and V7, 400 at Ramp and New
Yorker, 480 at Mercury, 510 at Linear. Only Headspace uses 700.

**Radius is either a tight scale or a wide one, never uniform.** Ramp 4–24, New
Yorker effectively none, V7 zero, Linear 2–16 plus pills, Origin 8–30 plus
full-round, Headspace 8–800.

## Grouping verdict

Seven references, and by measured values they are **not** collapsible into one or
two languages:

- **Ramp** stands alone as white-ground, single-accent, border-elevated, zero-shadow.
- **Linear** stands alone as near-black with alpha-tint elevation and white-alpha hairlines.
- **Mercury and Origin** are the only pair close enough to share a base file: both dark, image and glass led, multi-accent, large radii. Their type, card and hero treatments still need separate variants.
- **V7** stands alone: hard-edged, radius 0, light-weight serif display.
- **New Yorker** stands alone: light editorial, two families, no tracking, no radius.
- **Headspace** stands alone: warm ground, one family, saturated flat fields, very large radii.

## Prior art

| Project | What it is | Representation |
| --- | --- | --- |
| [bitjaru/styleseed](https://github.com/bitjaru/styleseed) | Design-method engine, 23 skills, 74 rules, MIT | Separates output grammar, brand recipe, palette, skin. Lock file plus compiled `effective-rules.md`. Scored build gate refusing below 80. |
| [MengTo/Skills](https://github.com/MengTo/Skills) | ~123 skill folders | Each demo ships `demo/index.html`, `preview.jpg` at 1280×720, and a `PROMPT.md` that recreates it. "Specs beat vibes, references beat paragraphs." |
| [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) | Per-brand `DESIGN.md` files | Philosophy, canvas/ink/accent, radius, surface ladder, signature signals, observed components, anti-slop rules. |
| [Laith0003/ux-skill](https://github.com/Laith0003/ux-skill) | Python engine plus Claude plugin | 12 JSON manifests, 7-axis synthesiser, 152-pattern regex anti-slop linter. |
| [anthropics frontend-design](https://github.com/anthropics/claude-code/tree/main/plugins/frontend-design) | One prose `SKILL.md` | No style catalog, no tokens, no gate. Currently enabled in `plugins.txt:27`. |

### The one measured claim

StyleSeed's own benchmark: 20 fixtures × 2 agents × 3 conditions, 120 rendered
cells, neutral fixed-seed judge.

| Condition | Codex | Claude |
| --- | --- | --- |
| bare | 74.8 | 74.1 |
| + rules | 76.4 (**+1.6**) | 70.4 (**−3.7**) |
| + rules + enforced gate | 80.1 (**+5.3**) | 79.4 (**+5.3**) |

Rules alone were noise. The enforced render-score-revise loop was the lever.
Distinctiveness remained the lowest-scoring category throughout, so nobody has
solved "not generic".

Self-published and unreplicated. Sources:
[benchmark](https://raw.githubusercontent.com/bitjaru/pixelmind/main/bench/v1/README.md),
[gate](https://styleseed-demo.vercel.app/gate).

## Packaging mechanics

- A plugin manifest is **optional**; `name` is the only required field
  ([reference](https://code.claude.com/docs/en/plugins-reference#plugin-manifest-schema)).
  Bundled skills auto-namespace as `plugin:skill`.
- Codex reads `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
  ([protocol.rs:45-50](https://github.com/openai/codex/blob/9ded177ce7c1c0bd2047f902936c177612ab3434/codex-rs/exec-server-protocol/src/protocol.rs#L45-L50)).
- opencode is not installed on this machine: no binary, no config directory.
- `install.sh:149-154` symlinks `skills/*/SKILL.md` **one level deep**, so
  per-direction material must be plain `.md`, not nested `SKILL.md`.
- `.githooks/pre-commit` rejects the commit unless `dist/<skill>.zip` is rebuilt
  and staged. Anthropic guidance is `SKILL.md` under 500 lines.
- Repo is **private** (`sudakshsoti/agent-config`).

## Font inventory

Held as `woff2` and usable today: Söhne (Buch, Kräftig, Halbfett), National 2
(regular, italic, medium, bold, bold-italic), Berkeley Mono (regular, bold), plus
free Literata, Newsreader, Inter, JetBrains Mono.

Desktop only, no `woff2`: Mallory, National 2, Tiempos Text, Halyard, Atkinson
Hyperlegible Next.

Not present in any form: Mercury, Whitney, Archer, Verlag, Knockout, Gotham,
Domaine, Harriet, despite `frontend-craft`'s operator-context section listing
them.

### Google Fonts policy, as settled so far

**Allowed:** Newsreader, Literata, Source Serif 4, Geist, Geist Mono, IBM Plex
Sans / Serif / Mono, JetBrains Mono, Schibsted Grotesk, Bricolage Grotesque,
Libre Caslon Text, Hanken Grotesk, Fira Sans / Fira Code / Fira Mono. Inter for
body and UI only, never display.

**Banned:** Poppins, Montserrat, Raleway, Lato, Open Sans, Nunito, Quicksand,
Playfair Display, Oswald, Bebas Neue, Comfortaa, Josefin Sans, Roboto, Space
Grotesk, Manrope, DM Sans, DM Serif, Instrument Sans, Instrument Serif, Fraunces.

Paid fonts are local-machine only, for print or eyes-only artifacts. Anything
public defaults to free faces unless licensing is sorted.

## Settled decisions

- Skill, not a plugin. Named **`studio`**.
- Absorb and retire `frontend-craft`; keep `typography-craft` as the specialist;
  disable `frontend-design` in `plugins.txt`; repoint `agents/frontend-craft.md`.
- 3-4 monolithic `DESIGN.md` files, one per direction. Skill suggests one.
- L3 per direction: prose, tokens, and a working `example.html`.
- Render gate is mandatory and blocking, with one revise cycle then
  ship-and-report.
- Anti-slop is one script: mechanical DOM and CSS checks fail with line numbers,
  judgement stays prose in each direction's avoid-list.

## Open questions

Round 3, unanswered:

1. Does `html-doc` retire into `studio`? Its Hard Rule 1 (no webfonts), its
   no-questions Phase 0, and its determinism thesis each conflict with what
   `studio` needs to do.
2. Do artifact-shape rules live once in `SKILL.md` rather than four times across
   the `DESIGN.md` files?
3. Which 3-4 directions, given seven distinct candidates, and does Kohra sit
   inside the roster or outside it as the default?
4. Which additional Google Fonts display faces are allowed, now that Instrument
   Serif and Fraunces are banned and the display inventory is thin?
5. Exact wording and default of the licensed-versus-free font question.
6. Gate scoring: universal rubric, per-direction avoid-list, or both weighted.
7. Build one direction end-to-end first as a format test, or all four together?
