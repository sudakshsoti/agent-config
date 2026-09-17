# Muse Code subscription as an OMP routing rung (2026-09-18)

Question: a Muse Code Everyday Usage subscription was purchased on 2026-09-18.
Can OMP route agents to it, what does it meter, and which agents should move?

Answer: yes — OMP 18.2.3 reaches it as the `muse-code` provider, the plan's
5-hour and weekly windows are machine-readable so `retry.usageAwareFallback`
covers it, and the window is cost-weighted rather than prompt-counted. On
2026-09-18 `code-worker`, `sonic` and `research` moved to
`muse-code/muse-spark-1.3-contributor`.

## Plan terms (primary source)

- Muse Code subscription tiers: **Everyday Usage $5.00/month** ("Access to the
  latest Muse models", "Send 10-50 prompts every 5 hours, including image and
  video uploads", voice mode, web search), High Usage $15.00/month ("5x more
  usage than the Everyday Usage plan"), Power Usage $50.00/month ("20x more
  usage"). Source: <https://developer.meta.com/ai/products/muse-code/> (read
  2026-09-18). The local account is Everyday Usage, billed ₹399.00, renewing
  2026-10-18 (account settings screenshot supplied by the user, same day).
- Model tiers on the same page: `muse-spark-1.3-contributor` — "Used to improve
  our products", $0.10 input / $0.002 cached / $0.20 output per Mtok;
  `muse-spark-1.3` — "Not used to improve our products", $1.25 / $0.15 / $4.25.
  The 12.5x input and 21x output gap is the price of the training grant, and it
  matches `docs/research/opencode-go-models-2026-09.md`.
- Meta publishes no absolute token budget for a plan window, and no statement
  that contributor and standard prompts consume a subscription window
  differently. "10-50 prompts every 5 hours" is the only published figure.

## Local probes (2026-09-18, omp/18.2.3)

- `omp models muse-code` lists five models: `muse-spark-1.1`, `1.2`,
  `1.2-contributor`, `1.3`, `1.3-contributor`. All show a 1M context window and
  131K max output. Effort levels: `1.3` accepts `minimal,low,medium,high,xhigh,max`;
  `1.3-contributor` accepts `minimal,low,medium,high,xhigh` — **no `max`**.
- A credential is already present (`omp token muse-code` returns an OAuth access
  token plus an `LLM|…` API key), so no login step was needed.
- Reachability, retry disabled so a fallback cannot mask a failure
  (`omp -p --model <id> --config <(printf 'retry:\n  enabled: false\n') "Reply with exactly: ok"`):
  both `muse-code/muse-spark-1.3-contributor` and `muse-code/muse-spark-1.3`
  answered `ok`.
- `omp usage` reports the plan as two windows —
  `5 Hours (Muse Code Everyday Usage)` and `Weekly (Muse Code Everyday Usage)` —
  with reset times, so `retry.usageAwareFallback` (enabled, `usageReservePct: 20`,
  `usageReservePolicy: auto`) can preflight it rather than failing open.
  Reports are cached; `omp usage invalidate` forces a refresh, and every
  measurement below was taken after invalidating.

### Metering is cost-weighted, not prompt-counted

| Step | 5-hour window |
| --- | --- |
| baseline | 0% |
| two one-token prompts (one contributor, one standard) | 1% |
| one further one-token **contributor** prompt | 1% (no integer change) |
| one further one-token **standard** prompt | 2% |
| one full `code-worker`-shaped turn on **contributor** (read two files, two edits, two test runs, 52s) | 2% (no integer change) |

Reading: per-prompt metering on a 10-50 prompt window would have moved the bar
2-10% per prompt, so the window is priced, not counted. A trivial standard-tier
prompt consumed a visible point while trivial contributor prompts and a complete
multi-tool contributor turn stayed below the reporting resolution — the
direction the published 12.5x/21x price gap predicts.

Limits: the usage report has 1% integer resolution, each row above is n=1, and
the measured task ran in a two-file scratch directory. A real repository turn
carries far more context (cached input is $0.002/Mtok on contributor, so repeat
turns in one session are cheaper than the first). The safe conclusion is a lower
bound: an Everyday Usage window absorbs on the order of 100 bounded contributor
tasks, not that it absorbs unlimited work. Re-measure with
`omp usage invalidate && omp usage -p muse-code` if `code-worker` starts
throttling.

## Routing decision (2026-09-18)

| Agent | Before | After | Why |
| --- | --- | --- | --- |
| `code-worker` | `opencode-go/deepseek-v4.1-flash:high` | `muse-code/muse-spark-1.3-contributor:high` | AA Intelligence Index 48 vs 40; LMArena WebDev 1623 vs 1614; leaves the Go cap two days before DeepSeek's promo ends |
| `sonic` | `opencode-go/deepseek-v4.1-flash:high` | `muse-code/muse-spark-1.3-contributor:low` | mechanical work on the cheapest adequate rung |
| `research` | `opencode-go/muse-spark-1.3-contributor:high` | `muse-code/muse-spark-1.3-contributor:high` | same model, own quota pool instead of the shared Go cap |

Unchanged: every Claude role and agent, including `builder` on
`anthropic/claude-sonnet-5:high` (user decision — implementation accuracy on an
approved UI plan is worth plan usage), and every GLM role (`smol`, `tiny`,
`commit`, `scout`, `adversary`, `reviewer`, `advisor`).

Two reasons the GLM roles stayed on Go. First, quota isolation: `muse-code` and
`opencode-go` are separate pools, so a drained Muse 5-hour window still leaves
commits, discovery and review working, and vice versa. Second, lineage: after
this change Muse writes a large share of the code, and `adversary`/`reviewer`
must not be the model under review.

`opencode-go` still carries GLM 5.3 Flash and DeepSeek V4.1 Flash, so the Go
subscription is not idle; it no longer serves Muse Spark at all.

Fallback chains added or changed in `omp/config.yml`:

- `muse-code/muse-spark-1.3-contributor` → `opencode-go/glm-5.3-flash:high` →
  `opencode-go/deepseek-v4.1-flash:high`.
- `opencode-go/deepseek-v4.1-flash` now steps up to
  `muse-code/muse-spark-1.3-contributor:high` before GLM.
- The obsolete `opencode-go/muse-spark-1.3-contributor` chain key was removed
  with its last routed consumer.

## Privacy scope of this decision

`muse-spark-*-contributor` is training-eligible: Meta's own model table says
"Used to improve our products". `code-worker` and `sonic` edit repository
source, so their prompts now carry code to a training-eligible tier. The user
lifted the previous prohibition explicitly on 2026-09-18 ("I don't work on
anything sensitive here").

The scope is wider than this repository: `omp/config.yml` is symlinked to
`~/.omp/agent/config.yml`, so the routing applies to every directory opened in
OMP. Mitigation when a session does touch client or sensitive material: keep the
work off `code-worker`/`sonic`/`research`, or pin
`muse-code/muse-spark-1.3` — the standard tier is explicitly not used for
training, at roughly 12.5x the quota burn, which the measurements above suggest
is affordable for a low-volume agent.

Pi is unaffected: its credential store holds only the OpenCode Go key, so
`muse-code` is unreachable there and `pi/model-ladder.md` still describes Go-only
routing.

## Sources

- <https://developer.meta.com/ai/products/muse-code/> — subscription tiers,
  per-model pricing, training language (read 2026-09-18).
- <https://dev.meta.ai/docs/pricing-rate-limits> — contributor vs standard terms
  (read 2026-09-16, `docs/research/opencode-go-models-2026-09.md`).
- <https://artificialanalysis.ai/models/muse-spark-1-3/>,
  <https://artificialanalysis.ai/models/deepseek-v4-1-flash/> — AA Intelligence
  Index 48 and 40 (read 2026-09-16).
- <https://lmarena.ai/leaderboard> — WebDev snapshot, Muse Spark 1.3 xhigh
  1623.1, DeepSeek V4.1 Flash max 1614.0 (read 2026-09-16).
- <https://opencode.ai/docs/go> — Go caps and the DeepSeek promo ending
  2026-09-20 (read 2026-09-16).
- Local: `omp models muse-code`, `omp token muse-code`, `omp usage`,
  `omp usage invalidate`, `omp -p` probes (2026-09-18).
