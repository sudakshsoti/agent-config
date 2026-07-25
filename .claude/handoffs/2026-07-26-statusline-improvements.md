# Session Handoff: Statusline improvements

**Date:** 2026-07-26
**Project:** /Users/sudakshsoti/dev/agent-config
**Branch:** `statusline-cache-visibility` (off `main`, 10 commits, pushed)
**PR:** https://github.com/sudakshsoti/agent-config/pull/9 — open, ready for review, not merged

## Current State

**Task:** Implement the brainstormed ccstatusline improvements, plus an install flag.
**Phase:** The original plan is finished. Branch open for further iteration.
**Progress:** All planned items closed. Items 6, 8, 9 landed this session; item 7
was investigated and deliberately dropped.

**The layout IS live.** This is the change from the previous handoff:
`./install.sh --force-statusline --no-plugins` was run, then `./sync.sh`.
`diff ccstatusline-settings.json ~/.config/ccstatusline/settings.json` is empty
and the working tree is clean.

## Commits (all 10, oldest first)

```
2418a0b install: add --force-statusline to redeploy the layout
7be00bb scripts: add a statusline preview harness
ccbcf78 statusline: make the git-group separators hide-aware
8ef3f60 docs: correct the statusline render command
f67e3f7 statusline: add a prompt cache timer
80b13be statusline: add cache hit rate widget to the cache group
4881389 statusline: tighten the cache group so line 2 fits 150 columns
83795dd statusline: turn the context label red past the break threshold
ec1bc9d statusline: pin the session clock and cost to the right edge
fa5e98a docs: record what the statusline widget script costs to maintain
```

Current render at width 150 (usable budget is 110, `flexMode: full-minus-40`):

```
line 1: Claude Sonnet 5 high agent-config statusline-cache-visibility (+1,-9)        6m · $1.23
line 2: ctx ▓▓░░░░░░░░ 22.7% 45.1k/200.0k · × COLD 95.0% · 5h ▓▓▓░│░░░░░ 34.0% 2h59m · 7d ▓▓│▓▓▓░░░░ 61.0% 4d23h59m
```

Line 1 pins its right group at exactly column 110. Line 2 is 107 of 110, or 110
when the context alarm fires.

## What We Did

Finished the plan: added a value-driven context alarm (the one thing ccstatusline
structurally cannot do), right-aligned the session group, deployed, documented.
Two plan items did not survive contact with evidence — see Deviations. Every
layout claim in here was verified by rendering and measuring, not by reading the
bundle.

## Decisions Made

- **The `ctx` label became the alarm, rather than adding a separate flag widget.**
  Line 2 had 3 spare columns; a standalone `▲ CLEAR` costs 8 and truncated the 7d
  reset timer at exactly the moment the line is worth reading. Swapping a 3-char
  label for a 5-char one costs 2. Renders grey `ctx` normally, red `CLEAR` past
  threshold.
- **`THRESHOLD` and the token counting moved to `hooks/context_size.py`**, shared
  by the hook and the widget. Two copies would drift, and a status line reading
  "fine" while the hook says "clear now" is worse than having neither.
- **The formula is input-only** (`input_tokens + cache_creation + cache_read`,
  never `output_tokens`). Not a preference — it is what Claude Code's own
  `used_percentage` documents and what ccstatusline computes, so the number can
  never contradict the bar beside it.
- **Payload fast path, transcript fallback.** `context_window.current_usage` is
  null before the first API call and again after `/compact`, so the fallback is
  required. Measured 35ms fast / 68ms walking a real 4.9MB transcript.
- **`context-budget.py` uses `os.path.realpath(__file__)`, not `abspath`.** It runs
  through its `~/.claude/hooks` symlink; abspath would look for `context_size.py`
  in `~/.claude/hooks` and break before `install.sh` had linked it there.
- **Dropped the `·` between the model group and the git group** (see Deviations).
- **Line 2 gets no `flex-separator`** — at 107/110 there is no gap to distribute.
- **Emoji → single-width glyphs CONFIRMED by the user** (`◆ HOT / ▓ / ▒ / ░ / × COLD`).
  This was the previous handoff's open question. Settled, do not re-raise.
- **120-column truncation accepted.** User works at 150. Not a bug to fix.

## Deviations from the plan (read before trusting the old plan text)

- **Item 7 (`git-ci-status`) was investigated and DROPPED by the user.** It is
  genuinely non-blocking, as the plan hoped — `scheduleRefresh` spawns with
  `detached: true, stdio: "ignore"` and `child.unref()`, and the render returns
  whatever is already on disk. But the plan's *other* precondition was false: with
  no PR it returns a literal `"-"` (`NO_CHECKS`), not `null`, so it does not
  collapse. `hideNoGit` only covers "not a git repo"; there is no metadata option
  for the no-PR case. Given the standing "never open a PR until I ask" rule, that
  dash would show nearly always. **Do not re-propose this widget without solving
  the dash.**
- **Item 8 cost the group-boundary dot.** A `separator` scans BACKWARD only and
  hides only when everything before it is empty. So a dot *leading* the git group
  can never collapse with it — outside a repo it dangled against the flex gap. At
  HEAD the *trailing* dot did the hiding and the line read correctly, which is why
  this looked fine before. Measured the frequency rather than guessing: of 307
  recorded sessions, at least a fifth ran in genuinely non-git dirs
  (`claude-projects/workbench`, `~`, `assistant`, Google Drive, `dev`). Removing
  the dot was the fix. **This partly supersedes commit `ccbcf78`** — of the two
  separators it made hide-aware, id 3 is now deleted and id 7 is now the
  flex-separator.

## Code Changes

**Files modified this session:**

- `ccstatusline-settings.json` — id 11 `custom-text "ctx"` → `custom-command`;
  id 3 (`·`) deleted; id 7 `separator` → `flex-separator`.
- `hooks/context_size.py` (new) — `THRESHOLD`, `BUCKET`, `from_payload`,
  `resolve_transcript`, `from_transcript`, `measure`. Importable, not runnable.
- `hooks/context-budget.py` — now imports the above; logic otherwise unchanged.
- `scripts/ctx-flag.py` (new) — the widget. Exits 0 and prints nothing on error.
- `scripts/test-ctx-flag.sh` (new) — 11 tests, all passing.
- `CLAUDE.md` — the "no test step" claim, the moved-checkout gotcha, and a new
  bullet on why value-driven widgets must shell out.
- `.gitignore` — `__pycache__/` (context_size.py is imported, so it byte-compiles).

**The widget's contract, from `execSync` in the bundle:**
exit 0, finish inside **1000ms**, and never set `maxWidth` alongside
`preserveColors` (truncation counts raw string length and cuts mid-escape).
Failures render into the line: `[Exit: N]`, `[Timeout]`, `[Cmd not found]`,
`[Permission denied]`, `[Error]`.

## Verified ccstatusline facts (do NOT re-derive — all empirical)

Bundle: `$(npm root -g)/ccstatusline/dist/ccstatusline.js`, v2.2.26. Registry:
`WIDGET_MANIFEST` (~line 70923).

Carried forward from the previous handoff, still true:

- **The settings schema types `type` as a plain string, NOT an enum.** A wrong
  widget id does not fail validation — it silently renders nothing. Always prove a
  widget by rendering it.
- **`COLUMNS` does nothing.** `probeTerminalWidth()` (~58188) reads
  `CCSTATUSLINE_WIDTH`, then ps/stty, then `tput cols`.
- **Rendering is implicit**: stdin not a TTY → stdout; stdin IS a TTY → launches
  the interactive TUI and hangs. Always pipe stdin.
- **There is NO value-driven conditional colouring.** No threshold/warn/critical
  colour keys. Gradients are POSITIONAL, painted across a widget's own characters,
  not value-mapped. This is the whole reason `custom-command` was needed.
- **`custom-command` supports `preserveColors`** so a script can emit its own ANSI.
  Its stdin = the raw Claude Code payload + an added `terminal_width`.
  ccstatusline's own transcript-derived metrics are NOT passed through.
- Widget ids: `cache-timer` (metadata `ttlSeconds`, `hideWhenEmpty`, `symbolHot`/
  `symbolFresh`/`symbolDraining`/`symbolUrgent`/`symbolCold`), `cache-hit-rate`
  (`cacheScopeSession`, `hideWhenEmpty`), `git-ci-status` (`hideNoGit`, plus
  top-level `rawValue`), `git-review` (canonical; `git-pr` is a legacy alias),
  `flex-separator`, `separator` (text field is `character`, NOT `customText`).
- **cache-timer's glyph and state word are inseparable** — always `"{glyph} {word}"`.
- `ttlSeconds: "3600"` is deliberate; the "300" default would show the cache as
  expired almost immediately given this setup's 1-hour prompt cache TTL.
- Cache scope is per-turn, not session — session totals average away the signal
  from a large inline read.

Corrected or added this session:

- **`exceeds_200k_tokens` DOES exist** in Claude Code's real payload. The previous
  handoff said it does not; that was true of ccstatusline's zod schema only, which
  is a different thing. Unused here (the 150K threshold is absolute, about cost,
  not about filling the window).
- **`commandPath` and `preserveColors` are TOP-LEVEL widget fields**, not `metadata`
  (zod schema ~52994).
- **`custom-command` default timeout is 1000ms**, overridable via a top-level
  `timeout`. Overrun renders `[Timeout]`.
- **Empty command output collapses the widget** (`return output || null`), so a
  hide-aware `separator` beside it behaves correctly.
- **`separator` hide-awareness is BACKWARD-ONLY** (~58915). It scans back and hides
  only if everything before it is empty; it breaks on a `flex-separator`. A
  separator that *leads* a hideable group can never collapse with that group.
- **No default separator is inserted adjacent to a `flex-separator`** (~59021), so
  a flex gap never picks up stray spaces.
- **`git-ci-status` renders `"-"` when there is no PR** — it does not hide.
- **`context_window.current_usage` is `null`** before the first API call and after
  `/compact`. Docs: `code.claude.com/docs/en/statusline` (the `docs.claude.com`
  URL 301s there).

## Gotchas that cost time

- **The committed fixture holds PLACEHOLDER paths.** `preview-statusline.sh`
  rewrites `cwd`/`workspace`/`transcript_path` at runtime. Invoking `ccstatusline`
  directly against `scripts/statusline-sample.json` renders with the git group
  collapsed and looks like a regression that isn't one. **Use the script.**
- Supplying `rate_limits` short-circuits the usage API fetch, so usage/reset
  widgets render offline with no auth.
- The fixture transcript has old timestamps, so cache state renders COLD. That is
  the real countdown path, not the `hideWhenEmpty` path.
- **Dedup will fool you when testing the hook.** `context-budget.py` writes a
  `/tmp/claude-ctx-*` stamp keyed on transcript path + bucket; a second run with
  the same transcript is silent by design and looks like a failure. Use a fresh
  transcript path per check.
- **A code comment is not evidence.** A subagent once "verified" a claim by quoting
  a comment restating it. Re-run the command.
- **Moving this checkout now breaks the live statusline**, not just the symlinks.
  `ccstatusline-settings.json` bakes this checkout's absolute path into
  `commandPath` and is a **copy**, so plain `install.sh` will not repair it — needs
  `--force-statusline`. Symptom is quiet: the `ctx` label just disappears.

## Open Questions

- [ ] Restore the model/git group-boundary dot? Removing it was the cheapest fix
      for the dangling-separator bug, but it does weaken the group structure. A
      conditional dot via a second `custom-command` would preserve the design at
      the cost of another subprocess (~30ms) per render. Judged not worth it; worth
      a second opinion.
- [ ] Line 2 fits 150 but truncates at 120. User accepted this. Revisit only if
      the working width changes.
- [ ] Is 150K still the right threshold? It is absolute and cost-driven, so it does
      NOT scale with a 1M-context model — on Opus 1M the bar reads a calm 21.8% at
      210K tokens while `CLEAR` fires. That is intended, but it is the number most
      likely to want tuning with real use.
- [ ] Should `.claude/handoffs/` be tracked in git? Currently untracked.

## Next Steps

1. [ ] Live-test the alarm by actually running a session past 150K and confirming
       `CLEAR` appears in the real terminal (so far proven only by fixture render
       plus a direct script invocation).
2. [ ] Decide the group-boundary dot question above.
3. [ ] **Make the `ctx` widget tolerant of its own absence.** A missing
       `scripts/ctx-flag.py` should print a plain grey `ctx`, not `[Exit: 2]`.
       This already happened once, in the session that wrote this handoff: the
       working tree was switched to `main`, where the script does not exist, and
       the deployed layout immediately started rendering `[Exit: 2]` in place of
       the label. It will recur on any branch without the script while the layout
       is deployed — including `main` itself after this branch merges but before
       `install.sh` is re-run. Deliberately NOT bundled into the current PR, to
       keep it to work that was already verified.
       Sketch: wrap `commandPath` so the missing case degrades instead of erroring —
       `sh -c 'P=<abs>/scripts/ctx-flag.py; [ -f "$P" ] && python3 "$P" || printf "\033[38;2;130;134;137mctx\033[39m"'`
       — and extend `scripts/test-ctx-flag.sh` with a missing-script case. Check
       the quoting survives `execSync` (it runs the string through `/bin/sh`), and
       re-measure: this adds a second process to every render, on top of the 35ms
       already measured.
4. [ ] Consider whether the cache group still earns its columns now that line 2 is
       at 107/110 — it is the least-consulted group and freeing it would give the
       alarm and any future widget room.
5. [ ] Merge PR #9 (`/merge`). **Immediately after merging, re-run
       `./install.sh --force-statusline --no-plugins`** — not for the layout,
       which is already live and identical, but because until step 3 is done a
       checkout of `main` without the scripts makes the deployed widget render
       `[Exit: 2]`. Merging is what puts the scripts on `main` and closes that
       window.

## Files to Review on Resume

- `ccstatusline-settings.json` — the layout
- `scripts/preview-statusline.sh` — the verification harness; read its header
- `scripts/test-ctx-flag.sh` — run it after touching either Python file
- `hooks/context_size.py` — the shared measurement and THRESHOLD
- `scripts/ctx-flag.py` — the widget
- `CLAUDE.md` — the install/sync model and the widget-authoring constraints

## Verification commands

```bash
./scripts/test-ctx-flag.sh                      # 11 tests, must be 0 failed
./scripts/preview-statusline.sh 150             # render the repo layout
./scripts/preview-statusline.sh 150 ~/.config/ccstatusline/settings.json   # render LIVE
diff ccstatusline-settings.json ~/.config/ccstatusline/settings.json       # must be empty
./install.sh --force-statusline --no-plugins    # push a layout edit out live
```
