# pi replaces omp as the daily driver

Date: 2026-09-08.
Branch: `pi-minimal-setup`.
Status: built and verified. omp untouched and still working.

## The decision

Move day-to-day coding from omp to pi,
keeping omp installed and configured as the fallback.
Nothing about omp was deleted:
`omp/` is still tracked,
`~/.omp` is intact,
and the `ompgo`/`ompcodex` wrappers still work.

Revisit deleting omp around 2026-09-22,
and only if a fortnight has passed without reaching for it.

## What pi does and does not have

Free, and already installed:
auto-compaction is built into pi (`compaction.enabled`),
LSP is `pi-lens`,
subagents are `@tintinweb/pi-subagents`,
web search is `pi-web-access`,
and skills are native — pi reads `~/.agents/skills` with nothing to configure.

Two things omp had that pi simply does not:

**Model roles.** pi has one default model, an `enabledModels` list cycled with Ctrl+P,
and `modelThinkingLevels`.
Per-job models exist only inside `pi/agents/<name>.md` frontmatter.
There is no main-session equivalent of omp's `plan`/`slow`/`adversary`/`commit` roles.

**Fallback chains.** pi's `retry` is retry-the-same-model.
No cross-model rerouting exists at any level.
A dead model means Ctrl+P to the next one, or open omp.

Both are confirmed against the settings schema in
`dist/core/settings-manager.d.ts`, not guessed.

## What was built

`pi/` in this repo, symlinked by `install.sh` steps 3k–3n the same way `omp/` is:

- `pi/settings.json` — models, thinking level, theme, package list
- `pi/subagents.json` — widget and FleetView off
- `pi/agents/scout.md` — the one custom subagent
- `pi/themes/irfan-sumi.json` — the old theme, kept but not selected

pi writes `settings.json` itself when you run `pi install` or change something in `/settings`,
and the write follows the symlink into the repo.
So a TUI change shows up as a plain `git diff` with no sync step.
Review before committing.

Untracked on purpose: `auth.json` (tokens and API keys, chmod 600),
`models-store.json` (a refetchable cache),
`sessions/` and `npm/` (runtime state).

`~/.pi/agent/skills/` is deliberately **not** linked.
pi already discovers `~/.agents/skills`.
A second copy is discovered twice — the mistake baseline made.

## Models

Default: `opencode-go/muse-spark-1.3-contributor` at `high`.

Ctrl+P cycle: Codex Luna `xhigh`, Codex Terra `medium`,
`opencode-go/deepseek-v4-flash` `high`, `opencode-go/glm-5.3-flash` `high`.
All five were probed and answered.

### The Muse Spark trial, and how to undo it

Muse Spark 1.3 is on a **one-week trial** ending around 2026-09-15.

The case for it: cheapest thing on the Go plan by a wide margin.
$0.10/$0.20 per Mtok against a $60 monthly quota,
about 0.44% of the month per 1,000 requests.
deepseek-v4-flash costs 2.6% for the same 1,000 — 5.9x more.
It also carries a 1M context window against Codex's 272K.

The case against it, from this repo's own gotchas:
Meta tuned 1.3 for roughly 20% fewer tool calls and 25% fewer tokens than 1.2,
so it stops early and skips exploration.
That is exactly the failure mode to watch for.
The risk concentrates in the `scout` subagent, which runs the same model,
because scouting *is* exploration.

**To swap back**, edit `pi/settings.json`:

```json
"defaultProvider": "openai-codex",
"defaultModel": "gpt-5.6-luna",
```

That is the whole change. Nothing else depends on it.

Codex Luna is the right fallback because Codex Plus meters every prompt,
file read and tool call as a message against a 5-hour window,
and Luna's allowance is 250–2,000 against Sol's 10–100.

## Providers

Codex (OAuth, already there), OpenCode Go and OpenRouter. No Anthropic, by choice.

The OpenCode Go and OpenRouter credentials are plain API keys,
copied out of `~/.local/share/opencode/auth.json`
into `~/.pi/agent/auth.json` as `{"type": "api_key", "key": "..."}`.
No OAuth flow, no browser. On a new machine, repeat that copy by hand —
`install.sh` will not do it, because that file holds secrets and stays untracked.

## Packages

Kept: `@tintinweb/pi-subagents`, `pi-lens`, `pi-web-access`,
`@juicesharp/rpiv-ask-user-question`, `flexoki-pi-theme`.

Dropped: `pi-powerline-footer`, `pi-mcp-adapter`,
and the three `orca-*` extensions in `~/.pi/agent/extensions/`.
The orca ones only did anything when `ORCA_PANE_KEY` was set.

## Appearance

Stock pi TUI. Nothing added, no frames, no custom statusline.
Theme is `flexoki-dark` from `flexoki-pi-theme`,
matching the `kohra-flexoki` Ghostty theme.

The alternatives that were considered and rejected, if you want them later:
`pi-zentui` (Opencode-style TUI plus a Starship footer, well documented, 14 screenshots),
`pi-claude-code-ui` (Claude Code-style grouped tool rows),
`pi-rounded-tools` (rounded corners on tool frames and nothing else),
and the browsable gallery at <https://isashi.github.io/awesome-pi-themes/>.

## Verified

- All five models answer a print probe.
- The default resolves to `opencode-go/muse-spark-1.3-contributor` over `openai-responses`.
- `Agent` advertises `general-purpose`, `Explore`, `Plan` and `scout`.
- Skills load.
- All four repo symlinks resolve into this checkout.

## Not done

- omp is still installed and still tracked. That is the plan, not an oversight.
- No `adversary` or `commit` subagent in pi. Only `scout` was wanted.
- `pi/settings.json` has no `retry` block. There is nothing useful to put in one.
