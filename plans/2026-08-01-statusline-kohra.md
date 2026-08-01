# Statusline: Kohra palette, semantic colour, APCA-verified

## Context

The statusline runs `@owloops/claude-powerline` v1.29.0 on the built-in `tokyo-night`
theme, which has nothing to do with Kohra — the fog-grey OKLCH system used by Ghostty,
Zed, VS Code, Obsidian and the studio tokens. So the one strip of UI present in every
session is the only surface still off-system.

Three defects, in order of severity:

1. **Colour carries no meaning.** In the current bar green appears three times for three
   unrelated things (git status glyph, thinking effort `high`, and the plan-mode banner,
   the last of which is Claude Code's own output and not ours to style). Hue is decorative.

2. **The number that drives a decision is the quietest thing on the bar.** Context reads
   `8%` in low-contrast grey. The global `CLAUDE.md` rule is "at a task boundary past
   ~180K, stop and `/clear`" — so context is the only segment that triggers an action,
   and it is styled as though it were incidental.

3. **The chips do not separate.** Measured with APCA 0.1.9, every adjacency in Kohra's
   neutral ramp (`#181b1d` → `#212527` → `#2b2e31`) falls below APCA's reporting floor
   (Sapc < 0.1, clipped to Lc 0). Only `#3f4245` scores at all, at Lc 8.6. The ramp is
   deliberately compressed into the bottom of the luminance range because Kohra is a flat
   fog surface; filled chips with arrow separators have nothing to separate against. This
   is not fixable by re-picking greys.

Intended outcome: a bar where hue means one thing each, where the context figure is the
loudest resting element and legible against the 180K rule without arithmetic, and where a
filled background appears only when something needs attention.

### Decisions taken

- **`minimal` style, foreground-only colour.** Kohra's discipline ("L and C locked per
  bucket, only hue varies") is a foreground rule; it does not survive being applied to
  chip fills. Dropping fills also removes the Nerd Font dependency for separators.
- **Context shows tokens and percent** (`showPercentageOnly: false` → `◔ 77.4k (8%)`).
  The built-in warning threshold is hard-coded at 60% *used* and cannot be moved without
  forking; on 1M Opus that is ~580K, more than 3× past the point the rule says to stop.
  Rather than distort `autocompactBuffer` to force an earlier colour change, show the raw
  token count so the 180K rule reads directly off the bar.
- **Segment set unchanged**: git, model, context, thinking.

## The palette

Every value is an existing Kohra token. No invented colours. APCA Lc measured against the
Ghostty surface `#181b1d` with APCA 0.1.9, reverse polarity (light text on dark).

### Hue assignments — one hue, one category

| Meaning | Token | Hex | Segments | Lc |
|---|---|---|---|---|
| Place | `accent/blue` | `#78accf` | `git`, `directory` | 52.6 |
| The model itself | `fg-secondary` | `#9a9ea1` | `model` | 48.1 |
| Mode | `accent/purple` | `#a89ccf` | `thinking` | 51.1 |
| Subagent | `term/bright-magenta` | `#d598c0` | `agent` | 55.2 |
| **The number you act on** | `fg-normal` | `#babec1` | `context` | **65.7** |
| Money and quota | `accent/teal-bright` | `#70b4a2` | `session`, `today`, `block`, `weekly` | 53.4 |
| Non-default env | `accent/yellow` | `#c29e70` | `env` | 51.6 |
| Telemetry | `fg-muted` | `#828689` | `metrics`, `cacheTimer` | 35.9 |
| Never changes | `fg-subtle` | `#6d7274` | `version` | 26.5 |
| Session identity | `accent/green` | `#9cad77` | `tmux` | 52.9 |

Context at Lc 65.7 is the brightest resting element, ahead of every accent at ~51–53.
That inversion is the point: the decision-bearing figure now outranks orientation.

Green drops from three jobs to one. It can be freed because the git status glyph
**cannot** be coloured independently — `renderGit` pushes `✓ ● ⚠` into the segment text
and returns a single `fgColor` (`src/segments/renderer.ts:370-382`). Status is carried by
glyph shape alone, which is sufficient and was always doing the real work.

### Alert pair — the only filled backgrounds

Kohra's own doctrine: *"Diagnostics break the rule on purpose — they have to interrupt."*
On a flat bar, a fill is unambiguous.

| State | fg | bg | Lc | bold |
|---|---|---|---|---|
| `contextWarning` | `term/bright-yellow` `#d2a56d` | `conflict.border` `#382f1d` | 52.8 | no |
| `contextCritical` | `term/bright-red` `#e19796` | `vcs/deleted-bg` `#321919` | 54.3 | yes |

The obvious choice would have been `diag/error #d36c6d` and `diag/warning #bf801e`, but
those measure **Lc 39.0 and 40.0** on the surface — quieter than ordinary body text at
65.7, so the alert would whisper. The `term/bright-*` variants are still Kohra tokens
(term-bright bucket, L 0.75 / C 0.09) and lift the pair to 52.8 and 54.3 against their
tinted grounds, a gain of roughly 16 Lc.

This pair is shared by `context`, `block`, `weekly` and `cacheTimer` — there is no
per-segment alert colour in the schema.

## Changes

Critical files:

- `claude-powerline.json` — symlinked to `~/.claude/`, so repo edits are live immediately.
- `settings.json` — a **copy**, not a symlink. Edit `~/.claude/settings.json`, then run
  `./sync.sh` to pull it back. Editing the repo copy alone does nothing.
- `CLAUDE.md` / `AGENTS.md` — the statusline section documents the theme choice.

### Checklist

- [x] **1. Rewrite `claude-powerline.json` colours and style.** — `10d5065`
  Set `"theme": "custom"` and add a `colors.custom` block. Set `display.style` from
  `"powerline"` to `"minimal"`.
  **All 17 slots must be filled.** A partial `colors.custom` deep-merges over the built-in
  **dark** theme, so any omitted segment silently inherits dark's values — including a
  `#8b4513` saddle-brown directory and a `#00ffff` cyan session. Slots: `directory`, `git`,
  `model`, `session`, `block`, `today`, `tmux`, `context`, `contextWarning`,
  `contextCritical`, `metrics`, `version`, `env`, `weekly`, `agent`, `thinking`,
  `cacheTimer`. (`sessionId` has no slot; it reuses `session`.)
  Every `bg` is `"transparent"` except `contextWarning` and `contextCritical`, per the
  tables above. `"transparent"` is accepted and emits `\x1b[49m`.

- [x] **2. Make the context segment read in tokens.** — `fecce29`
  In `display.lines[0].segments.context`, set `"showPercentageOnly": false`. Keep
  `"displayStyle": "text"` and `"percentageMode": "used"` — with `displayStyle: "text"`
  the mode defaults to `"remaining"`, so the explicit `"used"` must stay or the number
  inverts. Leave `autocompactBuffer` at `33000` and `modelContextLimits.opus` at
  `1000000` (the latter is deliberate and documented; do not "fix" it to 200000).

- [x] **3. Change the statusline command in `settings.json`.** — `e54aded`
  Currently `claude-powerline --style=powerline`. **The CLI flag overrides the config
  file** (precedence: defaults → file → env → CLI), so leaving it set to `powerline` makes
  step 1's `"style": "minimal"` silently ineffective. This is the single most likely way
  this change fails without any error.
  Change to `claude-powerline --style=minimal`, keeping the flag as the documented
  fallback for a failed config load. Edit `~/.claude/settings.json`, then run `./sync.sh`.

- [x] **4. Update the statusline docs.** — `5efb457`
  In `CLAUDE.md`, the statusline section still describes the theme as a built-in. Record:
  `theme: "custom"` backed by Kohra tokens; `style: "minimal"` with the reason (the
  neutral ramp cannot carry chip separators — APCA sub-floor at every adjacency); that all
  17 colour slots must stay filled because partial merge falls back to dark; and that the
  `--style` flag in `settings.json` overrides the config file.
  Apply the same edit to `AGENTS.md`. Note that file already carries a pre-existing
  string-replacement bug in this exact section — it reads `Codex-powerline` and
  `npm i -g @owloops/Codex-powerline`, which are not real identifiers. Fix those while
  editing.

## Verification

No test suite covers the statusline (`scripts/test-context-size.sh` covers the context
hooks only, and is untouched by this change). Verify by rendering.

1. **Render it directly.** `claude-powerline --style=minimal` in a Ghostty window running
   the kohra theme. Confirm: no arrow glyphs, no chip fills, four segments separated by
   spacing, and the context figure visibly brighter than the git and model text.

2. **Confirm the config is actually being read**, not just the CLI flag — temporarily set
   a segment's fg to something obviously wrong (e.g. `#ff0000` on `model`), re-render,
   confirm it changes, then revert. This is the check that catches a stray
   `.claude-powerline.json` in a project directory winning the search order.

3. **Confirm the token count renders.** Context should read `◔ <tokens> (<pct>%)`, not a
   bare percentage.

4. **Force both alert states.** The thresholds are on context *remaining*: warning at
   ≤40% left, critical at ≤20% left. Rather than burn 600K of real context, verify by
   temporarily lowering `modelContextLimits.opus` to a small value (e.g. `120000`) so the
   current session crosses both thresholds, render, confirm the amber and red grounds
   appear and that the fill is visible in `minimal` style — **this is the one assumption
   worth testing early**, since `minimal` may not emit a background at all. If it does
   not, the alert states need a fallback (bold plus fg-only shift). Restore
   `modelContextLimits.opus` to `1000000` afterwards.

5. **Check a clean and a dirty repo.** Confirm `✓` and `●` both render in the same blue
   and that status is still readable from glyph shape alone.

6. **Confirm the symlink held.** `readlink ~/.claude/claude-powerline.json` should point
   into the repo, so the edit is live without re-running `./install.sh`.

Commit after each checklist item, per the global git rule.
