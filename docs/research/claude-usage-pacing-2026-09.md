# Pace-aware Claude usage gating (2026-09-28)

Question: the overnight runner's `usage-gate.sh` stops on raw weekly usage
(`SEVEN_DAY_STOP_PCT=60`), but 60% on day 1 of the 7-day window is dangerous
while 60% just before reset is fine. How do community tools compute usage
**pace**, and what should the gate adopt? Prior primitives (omp JSON shape,
window ids, epoch-ms `resetsAt`) are in
`docs/research/claude-code-overnight-primitives-2026-09.md` and not repeated
except where pacing needs them.

Answer: every pace-aware tool surveyed converges on one formula —
`expected% = elapsed/window × 100`, `delta = used% − expected%`, with
`window_start = resetsAt − window_length` — differing only in tolerance,
edge-case guards, and whether they also project exhaustion time. The gate
should stop a weekly window when `used > expected + margin` (past a minimum
elapsed floor) while keeping the 60% absolute ceiling, and leave the 5h
sleep path untouched.

## 1. What our data provides — VERIFIED live

`omp usage invalidate --provider anthropic`, then ~40 s later
`omp usage --provider anthropic --json` (account identifiers redacted):

- `anthropic:5h`: `amount.used = 21` (percent),
  `window = {id: "5h", durationMs: 18000000, resetsAt: 1790548200000}`.
- `anthropic:7d`: `amount.used = 22` (percent),
  `window = {id: "7d", durationMs: 604800000, resetsAt: 1790780400000}`.
- `generatedAt: 1790536546667`. No `anthropic:7d:<tier>` entry was present
  in this run (cf. the `go.json` fixture, which carries `anthropic:7d:fable`
  at 0% with its own `durationMs`/`resetsAt`), so scoped windows appear
  conditionally — the gate must keep treating them as optional.
  (Live `omp` output, 2026-09-28.)

Window start is therefore derivable per window as
`start = resetsAt − durationMs`, with the duration authoritative per window
(5 h = 18,000,000 ms; 7 d = 604,800,000 ms) rather than hardcoded.
Worked example at `now = generatedAt`: 5h elapsed =
(1790536546667 − (1790548200000 − 18000000)) / 18000000 ≈ **35.3%** vs 21%
used (headroom); 7d elapsed =
(1790536546667 − (1790780400000 − 604800000)) / 604800000 ≈ **59.7%** vs 22%
used (deep headroom). Under the current raw gate both read "fine" for the
wrong reason; at 60% used the raw gate could not tell these two situations
apart.

## 2. Tool survey

### 2.1 claude-pace (Astro-Han) — VERIFIED (source)

Pure Bash + jq statusline; its entire pace model is one function. Given
`u` = used% (floored), `rm` = whole minutes until `resets_at`, `w` = window
length in minutes (300 / 10080 at the single call site):

```bash
local d=$((u - (w - rm) * 100 / w))
```

Positive `d` renders `⇡d%` (overspend), negative renders `⇣d%`
(headroom). Sources:
[`claude-pace.sh:249`](https://raw.githubusercontent.com/Astro-Han/claude-pace/main/claude-pace.sh)
(formula),
[`claude-pace.sh:284`](https://raw.githubusercontent.com/Astro-Han/claude-pace/main/claude-pace.sh)
(`_usage "$U5" "$RM5" 300` / `_usage "$U7" "$RM7" 10080` call site).
Notes: `NOW=$(date +%s)` is captured once per render; the delta is skipped
unless `rm <= w` (stale/far-future `resets_at` guard); no tolerance band and
no near-start floor — `d` is display-only, so noise is harmless. Windows:
5h + 7d from stdin `rate_limits`; data source is live stdin only, with an
explicit no-stale-cache decision
([README](https://github.com/Astro-Han/claude-pace),
[removal decision](https://github.com/Astro-Han/claude-pace/blob/main/docs/decisions/2026-05-20-quota-cache-removal.md)).

### 2.2 Claude-Code-Usage-Monitor v4 (Maciek-roboblog) — VERIFIED (source)

 Computes a `pace` block in the machine-readable snapshot
(`src/claude_monitor/output/snapshots.py`, `_pace_from_window`):

- `window_start = reset_at − 5h`; `elapsed_ratio` clamped to [0, 1];
  `elapsed_pct = round(ratio × 100, 1)`; `delta = used_pct − elapsed_pct`
  ([snapshots.py:143-147](https://raw.githubusercontent.com/Maciek-roboblog/Claude-Code-Usage-Monitor/main/src/claude_monitor/output/snapshots.py)).
- Labels with a ±10-point tolerance band
  (`_PACE_TOLERANCE_POINTS = 10.0`, [snapshots.py:30](https://raw.githubusercontent.com/Maciek-roboblog/Claude-Code-Usage-Monitor/main/src/claude_monitor/output/snapshots.py)):
  `delta > 10` → `"slow down"`, `< −10` → `"speed up"`, else `"on track"`
  ([snapshots.py:149-154](https://raw.githubusercontent.com/Maciek-roboblog/Claude-Code-Usage-Monitor/main/src/claude_monitor/output/snapshots.py)).
- Missing `used_percentage` or `resets_at` → `"unknown"` (never a stale
  label). At/past reset the captured percentage is discarded as expired
  (`_window` in
  [`output/official.py`](https://raw.githubusercontent.com/Maciek-roboblog/Claude-Code-Usage-Monitor/main/src/claude_monitor/output/official.py)).
- Pace is computed for the **5h window only** (`_FIVE_HOUR_SECONDS`,
  [snapshots.py:31](https://raw.githubusercontent.com/Maciek-roboblog/Claude-Code-Usage-Monitor/main/src/claude_monitor/output/snapshots.py));
  the 7d percentage renders official-only with no pace.

Separately, its burn-rate engine (`core/calculations.py`) is token-based,
not quota-based: `tokens_per_minute = total_tokens / duration_minutes`
(active block, ≥1 min), `calculate_hourly_burn_rate` sums each block's
tokens pro-rated into the trailing 60 min, and `project_block_usage`
linearly extends the rate over remaining block time
([calculations.py](https://raw.githubusercontent.com/Maciek-roboblog/Claude-Code-Usage-Monitor/main/src/claude_monitor/core/calculations.py)).
Data sources: official stdin `rate_limits` (captured, 600 s TTL,
`OFFICIAL_TTL_SECONDS` in `output/official.py`) + local JSONL token counts.
The plan README advertises "reset-aware pace labels … and limit-hit freeze
behavior" ([README](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor)).

### 2.3 ccusage (ryoppippi) — VERIFIED (source)

Token-based burn + linear projection per 5-hour session block
(`rust/crates/ccusage/src/blocks.rs`):

- `calculate_burn_rate`: `tokens_per_minute = total_tokens / duration_minutes`
  over first→last entry timestamps; a second
  `tokens_per_minute_for_indicator` excludes cache tokens; `cost_per_hour`
  likewise ([blocks.rs:567-584](https://raw.githubusercontent.com/ryoppippi/ccusage/main/rust/crates/ccusage/src/blocks.rs)).
- `project_block_usage` (active blocks only):
  `total = current_tokens + rate × remaining_minutes`,
  `cost = current + hourly/60 × remaining_minutes`
  ([blocks.rs:586-601](https://raw.githubusercontent.com/ryoppippi/ccusage/main/rust/crates/ccusage/src/blocks.rs)),
  surfaced with a `(assuming current burn rate)` row and an
  exceeds/warning/ok status against the token limit.
- No quota-percentage pace: ccusage reads local JSONL, never `rate_limits`,
  so it cannot compute used-vs-elapsed. Relevant as the projection idiom
  (rate × remaining), not as a pacing formula. (Live-monitoring docs are
  historical-only since v17 removal:
  [ccusage.com/guide/live-monitoring](https://ccusage.com/guide/live-monitoring).)

### 2.4 CodexBar (steipete) — VERIFIED (source)

The richest quota-pace model found, in
[`Sources/CodexBarCore/UsagePace.swift`](https://raw.githubusercontent.com/steipete/CodexBar/main/Sources/CodexBarCore/UsagePace.swift)
(`UsagePace.weekly`). Windows: session/weekly (Codex) plus Claude OAuth
usage (the Claude provider reads Claude Code's Keychain OAuth item for
usage:
[`ClaudeProviderImplementation.swift:121`](https://raw.githubusercontent.com/steipete/CodexBar/main/Sources/CodexBar/Providers/Claude/ClaudeProviderImplementation.swift)).

- Window start identically derived: `elapsed = duration − timeUntilReset`,
  clamped to [0, duration]; `expected = elapsed/duration × 100`
  ([UsagePace.swift:58-72](https://raw.githubusercontent.com/steipete/CodexBar/main/Sources/CodexBarCore/UsagePace.swift)).
- Guards: `nil` when `resetsAt` is missing, `timeUntilReset ≤ 0`, or
  `timeUntilReset > duration` (stale/skewed reset); `nil` when
  `elapsed == 0 && actual > 0` (any usage at window start is
  infinitely-over-pace — the near-start problem made explicit)
  ([UsagePace.swift:50-76](https://raw.githubusercontent.com/steipete/CodexBar/main/Sources/CodexBarCore/UsagePace.swift)).
- Stages by |delta|: ≤2 on-track; ≤6 slightly ahead/behind; ≤12
  ahead/behind; beyond that far ahead/behind
  ([UsagePace.swift:256-262](https://raw.githubusercontent.com/steipete/CodexBar/main/Sources/CodexBarCore/UsagePace.swift)).
- Exhaustion projection from the current average rate: `rate = actual /
  elapsed`, `eta = (100 − actual) / rate`, `willLastToReset = eta ≥
  remaining`; plus `projectedRemainingUsage = actual × remaining / elapsed`
  and a `speedMultiplierToReset` headroom factor
  ([UsagePace.swift:83-90,93-108](https://raw.githubusercontent.com/steipete/CodexBar/main/Sources/CodexBarCore/UsagePace.swift)).
  A `workDays` variant re-baselines `expected` against workday seconds only.
- A sibling predictive-warning layer notifies only when `!willLastToReset`
  with `eta > 0` and `runOutProbability ≥ 0.5`
  ([PredictivePaceWarnings.swift:49-54](https://raw.githubusercontent.com/steipete/CodexBar/main/Sources/CodexBar/PredictivePaceWarnings.swift)),
  and a separate historical profiler (`HistoricalUsagePace.swift`, 169-point
  weekly grid, 56-day retention) calibrates pace against past weeks rather
  than uniform burn ([HistoricalUsagePace.swift:67-82](https://raw.githubusercontent.com/steipete/CodexBar/main/Sources/CodexBar/HistoricalUsagePace.swift)).
  Both are heavier than the gate needs; cited as the "sophisticated
  alternative" in §5.

### 2.5 ccstatusline (sirmalloc) — negative result

README grep for pace/burn finds no pace delta — it renders usage widgets,
reset countdowns ("calmer reset timer startup"), and overage widgets, i.e.
raw % + countdown only
([README](https://github.com/sirmalloc/ccstatusline)).
Included to bound the survey: not every statusline is pace-aware.

## 3. Consensus pattern

| Step | Consensus | Outliers |
| --- | --- | --- |
| Window start | `start = resetsAt − window_length` (all quota tools) | ccusage never sees resets (JSONL-only) |
| Expected | `expected% = elapsed/length × 100`, elapsed clamped [0, length] | CodexBar workday variant re-baselines elapsed |
| Signal | `delta = used% − expected%` | ccusage/CodexBar-ETA use rate × remaining projection (algebraically equivalent under uniform burn: `used×L/elapsed > 100 ⟺ delta > 0` [INFERENCE]) |
| Tolerance | 10pp (monitor) / staged 2-6-12 (CodexBar) / none, display-only (claude-pace) | — |
| Near-start | CodexBar returns nil at elapsed=0 with usage; others clamp | claude-pace shows raw delta (display-only) |
| Missing/stale reset | `unknown`/nil, never a label (monitor, CodexBar) | — |

## 4. Recommended gate design

Apply pacing to the **weekly** windows only (`anthropic:7d` + gated
`anthropic:7d:<tier>`); the 5h window keeps its existing sleep-until-reset
semantics (a 5h reset is always near, so sleeping is cheap and correct).

Per weekly window, with `U` = `amount.used`, `R` = `window.resetsAt`,
`L` = `window.durationMs`, `N` = `USAGE_GATE_NOW_MS`:

```text
remaining = R − N
elapsed   = clamp(L − remaining, 0, L)
expected  = elapsed / L × 100
delta     = U − expected
pace_over = elapsed ≥ PACE_MIN_ELAPSED_MS  AND  delta > PACE_MARGIN_PCT
hard_over = U ≥ SEVEN_DAY_STOP_PCT
stop      = pace_over OR hard_over          # exit 20
```

Semantics:

- **Stop, not sleep, on pace.** A blown weekly pace resolves at the weekly
  reset (days away), never within an overnight run; sleeping would idle the
  runner until morning for nothing. Keep exit 10 exclusively for the 5h
  window.
- **Keep the absolute ceiling.** `SEVEN_DAY_STOP_PCT=60` stays as `hard_over`
  regardless of pace: it bounds total weekly spend even when the burn is
  "on schedule", and it is the fail-safe when `resetsAt` is absent (fall
  back to the raw comparison; do not pace-gate without a reset time —
  monitor/CodexBar both refuse to label in that case, §2.2/§2.4).
- **Near window start.** While `elapsed < PACE_MIN_ELAPSED_MS`, any `U > 0`
  is infinitely-over-pace (CodexBar's explicit nil, §2.4); skip `pace_over`
  and judge by `hard_over` only. Default floor: 5% of the window
  (≈8.4 h for 7d) [INFERENCE — value, not pattern; CodexBar uses an exact
  zero check, the monitor clamps without a floor].
- **Near reset.** When `remaining` is tiny, `expected → 100` and pace says
  "go" for anything under the cap — correct: the window is about to clear.
  Clamp `elapsed` to `L` (stale `R < N` ⇒ `expected = 100`, pace silent,
  hard cap still guards). Surface `resets in …` in the reading so the
  operator sees why 60% was allowed.
- **Env knobs and defaults.**

  | Knob | Default | Basis |
  | --- | --- | --- |
  | `SEVEN_DAY_STOP_PCT` | 60 (unchanged) | existing ceiling |
  | `PACE_MARGIN_PCT` | 15 | above monitor's 10pp display band (a gate should fire less eagerly than a label), inside CodexBar's 12pp "far ahead" edge [INFERENCE — default value] |
  | `PACE_MIN_ELAPSED_FRAC` | 0.05 of `L` | near-start noise guard [INFERENCE — value] |
  | `PACE_ONLY` (opt-in) | unset | when set, skip `hard_over` for sensitivity testing |

- **Worked numbers** (live probe, §1): 7d at `U=22`, `expected=59.7` →
  `delta=−37.7`, go. Hypothetical day-1 `U=60` at `elapsed=15%` →
  `delta=+45 > 15` → stop. Same `U=60` at `elapsed=90%` → `delta=−30` →
  go (hard cap still 60, so `U=60` exactly is at the ceiling — the pace
  win only materializes below it, e.g. `U=55` late-window: currently
  stops? No — 55 < 60 goes today. The real behavior change is early-window:
  `U=40` at `elapsed=10%` stops under pace while raw lets it burn).

> Implemented 2026-09-28 with the ceiling at **90, not 60**, by user
> decision: a 60 ceiling blocks the late-week case (e.g. U=60 at 90%
> elapsed stops on `hard_over` despite healthy pace), so pace does the real
> gating and 90 is the fail-safe.

## 5. Alternatives considered

1. **Projection-to-reset stop** (`projected = U × L/elapsed > 100`, à la
   ccusage/CodexBar-ETA): equivalent to `delta > 0` under uniform burn but
   explodes near start (`elapsed → 0`) and needs its own floor; the margin
   form degrades linearly instead of hyperbolically. Adopt only if the team
   wants an ETA-in-hours reading for logs — cheap to add as display text
   (`eta_to_100 = (100−U)/U × elapsed`), not as the decision rule.
2. **Historical-profile pace** (CodexBar `HistoricalUsagePace`): compare
   against the runner's own past weeks instead of uniform burn. Overnight
   burn is bursty by nature (tickets, not humans), so a uniform schedule is
   the honest prior; revisit only if early-window stops prove too eager
   after a month of logs.

## 6. Test cases for `scripts/test-overnight-usage-gate.sh`

Fixtures reuse the `go.json` shape (`USAGE_GATE_JSON` + `USAGE_GATE_NOW_MS`;
`durationMs: 604800000` for 7d, `18000000` for 5h):

1. `pace-go-late-7d.json`: 7d `U=55`, `R−N ≈ 0.1×L` (expected≈90,
   delta≈−35) → exit 0. The motivating case: raw-adjacent usage allowed
   near reset.
2. `pace-stop-early-7d.json`: 7d `U=45`, `R−N ≈ 0.85×L` (expected≈15,
   delta≈+30 > 15) → exit 20. Early-window overspend the raw gate misses.
3. `pace-guard-start-7d.json`: 7d `U=10`, `R−N ≈ 0.99×L`
   (elapsed < 5% floor) → exit 0 despite delta > margin. Near-start floor.
4. `pace-hard-cap-late-7d.json`: 7d `U=65`, `R−N ≈ 0.05×L` (pace fine,
   delta < 0) → exit 20 via `hard_over`. Ceiling survives pacing.
5. `pace-stop-model-7d.json`: global 7d on-pace, `anthropic:7d:fable`
   over-pace with `--model …fable…` → exit 20 naming the scoped id; without
   `--model` likewise (unknown worker family gates all scoped windows, per
   current semantics).
6. `pace-no-reset-7d.json`: 7d entry without `window.resetsAt`, `U=40` →
   exit 0 (raw fallback, no pace); same fixture at `U=65` → exit 20.
   Missing-reset fail-safe.
7. `pace-5h-unchanged.json`: 5h `U=75` over sleep threshold with weekly
   on-pace → exit 10 with seconds ≈ `R₅ₕ−N` + grace. Guards the untouched
   5h path.
