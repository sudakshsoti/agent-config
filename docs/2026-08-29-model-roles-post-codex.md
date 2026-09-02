---
title: Model Roles After Codex
date: 2026-08-29
tags:
  - omp
  - models
  - config
  - cost
  - privacy
  - ai
aliases:
  - Post-Codex Model Roles
  - Muse Spark Roles
  - Model Role Plan 2026-08
status: active
---

# Model Roles After Codex

The applied `modelRoles` layout for `omp/config.yml`, sized for **Claude Max 5x
+ OpenCode Go**, with SuperGrok arriving next month and Codex on its way out.

> [!abstract] One-line mental model
> Anthropic drives, plans and looks at pictures, on Max quota. DeepSeek V4
> Flash does the parallel bulk, GLM-5.3-Flash does everything that needs
> judgement, and Muse Spark is the reservoir for prewalk and the advisor.
> Nothing opts out.

> [!success] Applied 2026-08-29
> `omp/config.yml`, `install.sh` step 3e and the
> [Ollama removal](#ollama-removal) are all live. One thing is **not** done:
> the [Codex handover](#the-codex-handover), which waits on SuperGrok.
>
> Muse Spark was then **measured**, moved off `scout` and `librarian`, and moved
> back the same day once price beat speed. See
> [Measured, not guessed](#measured-not-guessed) — that section supersedes the
> speed reasoning in any earlier draft of this file.

> [!success] Revised 2026-09-02 — quotas are requests, not dollars
> Go publishes a **requests/month allowance per model**, and that is the
> currency the plan actually meters. Every dollar-based comparison below is
> superseded by
> [The request-quota ladder](#the-request-quota-ladder-2026-09-02). Three
> claims in this file turned out to be wrong: Muse Spark's benchmark case, the
> "14x" allowance ratio, and the decision to drop DeepSeek V4 Flash.

## What changed and why

Four decisions drive the whole layout.

**Muse Spark 1.2 Contributor was picked on vendor-reported numbers, and they do
not hold up.** The Terminal-Bench 2.1 figure of 82.9% and the Arena coding score
of 1526±25 are both [Meta's
own](https://research.meta.ai/blog/introducing-muse-code-and-muse-spark-1-2).
On a third-party board of the top 120 models it ranks **#49 with an index of
40.5 and a Tools score of 20.8**, its Terminal-Bench cell is empty, and its Code
Arena cell is blank while DeepSeek V4 Flash shows 2,407. The price is real
($0.10/$0.20, and 226,600 requests a month) and the ZDR trade is still accepted,
but the quality argument was never independently verified. The allowance ratio
against GLM-5.3-Flash is **28.7x**, not the 14x claimed here — GLM-5.3-Flash
gets 1,580 requests per 5 hours, not 3,160.

**But it is slow in wall-clock, so it only gets work nobody waits on.** This is
the one place the plan changed after measurement rather than reading — see
[Measured, not guessed](#measured-not-guessed).

The price is real, though: it is the **only** model in the Go lineup marked
"Model training: Yes / Data retention: Not ZDR" on
[opencode.ai/docs/go](https://opencode.ai/docs/go). Meta says the same at
[dev.meta.ai/docs/pricing-rate-limits](https://dev.meta.ai/docs/pricing-rate-limits)
— the contributor tier is discounted *in exchange for* training rights. Every
other Go model is "Not used / 0 days". Accepted everywhere as of 2026-08-29,
including `OQGA` and `clinical-reasoning` — see
[the retired carve-outs](#the-two-carve-outs-retired-2026-08-29).

**Cheap models go on named agents, never on the `task` role.** The `task` role
stays Sonnet 5 so an unnamed or newly added agent lands on the capable model.
`scout`, `librarian` and `sonic` are named, and that is where the volume is.

**Grok reasons, it does not drive.** ARC-AGI-2 67.1%
([arcprize.org](https://arcprize.org/results)) and an Artificial Analysis index
of 61 against Sonnet 5's 55 — but absent from the SWE-bench Verified leaderboard
entirely, best Terminal-Bench 2.0 result rank 53 of 142 (and that's Grok 4.20 via
a third-party harness), and ~40s to first token at high effort. So: `adversary`,
and nothing else.

## Applied roles

| Role | Model | Effort | Reason |
| --- | --- | --- | --- |
| `default` | Sonnet 5 | medium | 90.7 tok/s, the fastest frontier model measured; 1M context; free under Max |
| `plan` | Opus 5 | high | plan mode is low-token and high-reasoning, so buy the effort |
| `slow` | Opus 5 | high | leads SWE-bench Verified (~96–97%) and ARC-AGI-2 (90.4%) |
| `designer` | Sonnet 5 | high | `agmtech` brand and motion work needs the headroom |
| `vision` | Sonnet 5 | medium | UI critique quality; cheap multimodals stay fallbacks |
| `task` | Sonnet 5 | medium | fail-safe: unnamed agents get the capable model |
| `adversary` | GLM-5.3-Flash | max | 51.1 index at 7,900 req/month. Kimi K3 costs 16x for 3.4 index points; Grok 4.6 gets 845 req/month for 47.2 and is dominated outright |
| `smol` | Muse Spark | low | prewalk + vibe `fast` tier. Was DeepSeek for speed; moved on price, since a spend budget makes 2.2x input / 3.3x output the thing you actually pay |
| `tiny` | Haiku 4.5 | low | fires before every turn under `defaultThinkingLevel: auto`, so its TTFT lands on your wait; free under Max, warm connection |
| `commit` | GLM-5.3-Flash | high | short and frequent, and you wait on it, so 8.3s latency beats Muse Spark's throughput |
| `advisor` | Muse Spark | high | reviews every transcript delta: huge input, tiny output, and cached input is $0.002/M. Inert while `advisor.enabled` is false |

Subagents:

| Agent | Model | Effort | Reason |
| --- | --- | --- | --- |
| `scout` | DeepSeek V4 Flash | high | the volume role. 45.7 index against Muse Spark's 40.5, and 37,800 req/month is 4.8x GLM-5.3-Flash's allowance |
| `librarian` | GLM-5.3-Flash | high | long output, low frequency, so the better model is affordable here |
| `sonic` | DeepSeek V4 Flash | low | mechanical bulk, runs in parallel, nobody waits on any single one |
| `reviewer` | GLM-5.3-Flash | max | Tools 34.0 against Muse Spark's 20.8. The cache-read argument below was arithmetically right but economically trivial — the whole month on Muse Spark was $1.76 |
| `security-reviewer` | GLM-5.3-Flash | max | same |

`adversary` is deliberately **absent** from `agentModelOverrides` —
`omp/agents/adversary.md` pins `model: "@adversary"`, so the role drives it and
an override would be dead config.

**The rule that decided Muse Spark placement, and how it changed twice.**
Originally: Muse Spark gets a role only when the output is short (`commit`) or
nobody is blocked on it (`advisor`, `sonic`, the fallback chains). Price
overrode that on 2026-08-29 — see [the reversal](#measured-not-guessed). On
2026-09-02 the request-quota table overrode it again, and Muse Spark is back to
**`smol` and `advisor` only**: 3.4s latency for prewalk, and a $0.002/Mtok cache
read for a role that re-reads the whole transcript. `default`, `plan`, `slow`,
`task`, `vision` and `tiny` stay on Anthropic, where the cost is Max quota
rather than Go allowance. `reviewer` was Kimi K3 for the verified score, then
GLM-5.3 at max effort, then Muse Spark from 2026-08-30, and is GLM-5.3-Flash
from 2026-09-02.

**How the Go monthly limit actually works.** It is **not a dollar total**. Every
model carries its own monthly dollar quota — $15, $30 or $60 by tier — and the
plan's "Monthly limit" is the **sum of each model's used fraction, capped at
100%**. The dashboard on 2026-08-30 read 102.6%, and the % column sums to
exactly that. So the number to minimise is percentage points, not dollars, and
**a dollar spent on a $60-quota model costs 1.67 points while the same dollar on
a $15-quota model costs 6.67 points** — a 4x difference in plan cost for
identical spend.

### The request-quota ladder (2026-09-02)

Go also publishes an **estimated requests/month per model**, which is the
dollar quota divided by that model's typical cost per request. This is the
number to plan against, because it needs no assumption about token mix.

| Model | Req/month | % of month per 1,000 req | vs GLM-5.3-Flash | Index |
| --- | --- | --- | --- | --- |
| Muse Spark 1.2 | 226,600 | 0.44% | 0.035x | 40.5 |
| DeepSeek V4 Flash | 37,800 | 2.6% | 0.21x | 45.7 |
| Qwen3.8 Flash | 27,000 | 3.7% | 0.29x | 49.6 |
| GLM-5.3-Flash | 7,900 | 12.7% | 1x | 51.1 |
| Hy4 preview | 6,770 | 14.8% | 1.17x | 51.5 |
| DeepSeek V4 Pro | 5,200 | 19.2% | 1.52x | 52.9 |
| GLM-5.3 | 1,080 | 92.6% | 7.3x | 54.1 |
| Kimi K3 | 490 | 204% | **16.1x** | 54.5 |

Those eight are the Pareto frontier on (allowance, intelligence). Everything
else on the plan is beaten on both axes: Hy3, MiniMax M3 and M2.7, Qwen3.6
Plus, Qwen3.8 Max, GPT 5.6 Luna, MiMo, and Grok 4.6 — which gets 845
requests a month for an index of 47.2 when Qwen3.8 Flash gives 32x the
allowance at 49.6.

**Above GLM-5.3-Flash the curve goes vertical.** Hy4 buys 0.4 index points,
DeepSeek V4 Pro 1.8, GLM-5.3 3.0 for 7.3x, Kimi K3 3.4 for 16.1x. Nothing
above GLM-5.3-Flash earns a role; DeepSeek V4 Pro earns exactly one chain
rung.

**Qwen3.8 Flash is the unused balance point** — 49.6 at 27,000 req/month,
3.4x GLM-5.3-Flash's allowance for 1.5 index points. Its 25.1s latency rules
it out for anything you wait on, but not for parallel subagents. Worth a look
if `sonic` volume ever grows.

**Sizing against real load.** `~/.omp/stats.db` recorded **4,245 Go requests
in 30 days**. On one model that whole load would consume 1.9% of the month on
Muse Spark, 11% on DeepSeek V4 Flash, 54% on GLM-5.3-Flash, 82% on DeepSeek
V4 Pro, and 866% on Kimi K3. The applied split lands around 35%.

**Why DeepSeek V4 Flash came back.** A token-price reading had it dominated by
GLM-5.3-Flash — 3x the input price on the same $30 tier. In request terms it
gets 4.8x the allowance, so it is the correct pick for `scout` and `sonic`,
where nobody waits and the index gap to GLM-5.3-Flash is 5.4 points.

The dollar side of the same month, from the OpenCode dashboard on 2026-08-30:

| Model | Quota | Used | Share of the month |
| --- | --- | --- | --- |
| GPT 5.6 Luna | $15 | $11.08 | **55.1%** |
| Hy3 | $60 | $8.29 | 10.3% |
| GLM 5.3 | $15 | $1.89 | 9.4% |
| Muse Spark 1.2 Contributor | $60 | $1.76 | 2.2% |
| DeepSeek V4 Flash | $30 | $0.49 | 1.2% |
| GLM 5.3 Flash | $30 | $0.17 | 0.4% |

**Why `reviewer` left GLM-5.3.** Not the dollar bill, which was small. GLM 5.3
sits on a $15 quota, so its 9.4% costs more of the month than Muse Spark's
$1.76 costs on a $60 quota. Muse Spark is the most quota-efficient model on the
plan: cheapest rates *and* the largest allowance. The mechanism still matters —
a reviewer re-reads the same diff every turn, so **cache-read price is the only
rate that decides this role**, and Muse Spark charges $0.002/Mtok against GLM
5.3's $0.26, 130x less.

> [!caution] omp's cost estimates are not OpenCode's meter
> omp `stats` put that same review at **$11.36 on GLM 5.3**; the OpenCode
> dashboard metered it at **$1.89**, 6x lower. In the other direction omp
> estimated $2.67 for Luna against OpenCode's $11.08, 4x high. Use `omp stats`
> only to find *which* model and *which* folder caused load. For how much plan
> is left, the per-model dashboard is the only trustworthy source, and
> `omp usage` shows just the capped aggregate.

> [!warning] `usageAwareFallback` blocks Go on the aggregate, ignoring per-model quota
> This is the trap, and it cost most of an afternoon to find. omp receives only
> the capped aggregate from Go (`rolling-5h`, `weekly`, `monthly` — no per-model
> rows, confirmed via `omp usage --json`). With `usageAwareFallback: true` and
> the aggregate reading `exhausted`, the preflight **skips every
> `opencode-go/*` selector**, including models sitting at 2% of their own quota.
> Two `reviewer` runs were pushed onto `claude-sonnet-5` this way while Muse
> Spark had 97.8% of its $60 allowance free. Setting `usageAwareFallback: false`
> fixed it on the next run: the reviewer reached
> `opencode-go/muse-spark-1.2-contributor` and billed $0.0022.
>
> The cost of `false` is one failed attempt when a model genuinely is out, which
> is what `fallbackChains` exists to absorb. Keep it off while the plan meters
> per model and omp only sees the total.
>
> One earlier observation had the same cause: an `adversary` run reached
> `opencode-go/glm-5.3-flash` while the reviewer was being skipped. Not a
> per-model difference — the usage cache had just been invalidated, so the
> preflight had no report to skip on.

> [!warning] zen is a second wallet, and it is real money
> A zen call returned `401 Your workspace has reached its monthly spending limit
> of $10`. After the limit was raised to $20, a direct `POST
> https://opencode.ai/zen/v1/chat/completions` returned `200` with a real
> `deepseek-v4-flash` completion, while Go's monthly still read 100.0% after
> `omp usage invalidate`. Two independent ceilings.
>
> **zen spend bills on top of the $10 subscription**, bounded only by that
> workspace limit. zen was therefore removed from every fallback chain on
> 2026-08-30: all three permitted models exist on Go under plan quota, so there
> is no reason to reach for cash. zen's catalog also cannot serve this fleet —
> it has no `glm-5.3-flash` (newest is `glm-5.2`), its Muse Spark is the
> non-contributor tier at $1.25/$4.25 rather than $0.10/$0.20, and both
> contributor ids are dead (`-contributor` "not supported",
> `-contributor-free` "Model is disabled").

> [!danger] Comments in `omp/config.yml` do not survive
> This file was written with a full block of rationale comments on every role
> and both invariants. Within the same session omp rewrote it and **every `#`
> line was gone**, values byte-identical. `omp config list` and `omp -p` were
> both tested afterwards and neither strips comments, so the exact trigger is
> unidentified — but the loss is reproduced and real.
>
> Consequence: this document is the only durable home for the reasoning. Do not
> put rationale in `omp/config.yml`; it will be silently deleted.
>
> `omp/projects/*.config.yml` used to be the opposite — omp read those and never
> wrote them, so 35 and 30 comment lines survived a global strip to zero. Both
> files were deleted 2026-08-29, so this document is the only durable home left.
>
> An earlier claim in `install.sh` step 3e that "nothing is reordered or
> dropped" was false and has been corrected in place.

## Fallback chains

Key specificity is `provider/model-id` > `provider/*` > role name > `default`
([settings.md](omp://settings.md)). Two consequences are baked into the config:

- There is **no `openai-codex/*` key**. Codex is no longer assigned to any role,
  but `openai-codex` still served 25,438 requests in the 30 days to
  2026-09-02 — six times the whole Go volume — so something outside
  `modelRoles` routes there. Unresolved.
- **Kimi K3 is banned from every chain.** It was rung 1 of the
  `opencode-go/glm-5.3-flash` chain at `:max`, so a single GLM-5.3-Flash
  outage would have routed every `scout`, `reviewer` and `commit` to the
  plan's most expensive model at maximum effort — 490 requests a month, 16x
  GLM-5.3-Flash. DeepSeek V4 Pro holds that rung instead, at 1.5x.
- Every `openrouter/*` rung is **decoration**. The OpenRouter key returns
  `401 User not found`, so the `openrouter/*` chain key was deleted on
  2026-09-02 and those selectors now fall through to `default`.

Two invariants worth restating because they are easy to undo:

- **No `anthropic/*` entry in a chain keyed from `anthropic/*`.** A fallback
  exists *because* Anthropic failed. Sending the retry back there wastes it.
- **The `opencode-go/*` chain leaves Go entirely.** If the gateway is what
  failed, the next hop must not sit behind the same path. It holds
  `anthropic/claude-sonnet-5:low` alone. Between 2026-08-30 and 2026-09-02
  this invariant was violated in the live config — Muse Spark sat at rung 1.

## The two carve-outs, retired 2026-08-29

`OQGA` (Optum HEDIS chart abstraction) and `clinical-reasoning` (real nephrology
handover notes in `cases/`) each had a project config whose only job was to keep
Muse Spark out. **Both are deleted.** Muse Spark's training tier is now accepted
on every repo, decided 2026-08-29 after the exposure was stated plainly: Meta
trains on prompts and completions from the contributor tier, so client chart
work and identifiable patient notes are in scope, and nothing sent is
recallable.

Removed with them:

- `omp/projects/OQGA.config.yml` and `omp/projects/clinical-reasoning.config.yml`
- the now-empty `omp/projects/` directory
- `install.sh` step 3j, the loop that symlinked those files to
  `~/dev/<repo>/.omp/config.yml` and nagged when `.omp/` was missing from the
  target repo's `.gitignore`. The step number is retired in place, like 3i.
- the live symlinks and their `.omp/` directories in both target repos

The `.gitignore` entries for `.omp/` in `OQGA` and `clinical-reasoning` are
harmless and were left alone.

Both repos now take the global roles: `scout` and `librarian` on Muse Spark,
`sonic` on Muse Spark, `commit` and `advisor` on Muse Spark, `task` still on
Sonnet 5. The five roles they used to pin — DeepSeek for `scout`/`librarian`,
Qwen3.8 Flash for `sonic`, GLM-5.3-Flash for `advisor`, Haiku for `commit` — no
longer apply anywhere.

> [!note] What this closes off
> `opencode-zen/muse-spark-1.2` is the same model *without* the training trade,
> and would have been the clean fix. It is unreachable: no Zen key exists on
> this machine and the OpenRouter key returns `401 User not found`. On OpenCode
> Go the contributor tier is the only Muse Spark available, so there was no
> route to Muse Spark's price without its training terms.

Two facts worth keeping from the retired setup, because they apply to any
future project config:

- **Project roles do override global despite `modelRoleStorage: global`.** That
  setting governs where the TUI *saves* roles, not where they are read from. Per
  [config-usage.md](omp://config-usage.md), "Native `.omp/config.yml` model
  roles are then reapplied as the authoritative project model-role layer."
- **`fallbackChains` deep-merges, so a project file must restate every key.**
  Any chain key it omits survives from global as-is. The first version of these
  files omitted `adversary`, and `omp config list` run from `OQGA` showed the
  global `adversary` chain intact with Muse Spark in it. The exclusion had a
  hole in it for a while.

## Gotchas found while applying

> [!warning] Thinking levels are per-model, and `medium` is often missing
> Three models in this config expose only `low / high / max` — no `medium`:
> `glm-5.3-flash`, `deepseek-v4-flash`, `kimi-k3`. Writing `:medium` on those is
> silently wrong. `minimax-m3`, `qwen3.8-flash` and `qwen3.7-plus` do have
> `medium`; `qwen3.*` has no `max`. Check before assuming:
>
> ```sh
> omp models --json | jq -r '.models[] | [.selector, ((.thinking // ["none"])|join(" "))] | @tsv'
> ```

Also confirmed at apply time:

- **Muse Spark resolves on this machine.** Its availability is footnoted
  "(limited regions)" and Meta's Geographic Use Policy applies, but
  `opencode-go/muse-spark-1.2-contributor` is present in `omp models`.
- **The catalog lists its input as text + image only**, not the video/PDF the
  docs advertise. Don't route PDFs at it expecting native handling.
- **`xai-oauth/*` resolves to nothing**, and the stale `xai` key in
  `~/.local/share/opencode/auth.json` is dead (`xai/grok-4.6` fails auth).
  Grok therefore comes from `opencode-go/grok-4.6`, not from xAI directly.
- **`openrouter` and `opencode-zen` are not usable routes.** Probing
  `openrouter/openai/gpt-5.6-sol` returns a plausible reply, but it is the
  fallback answering: the OpenRouter key returns `401 User not found` and no
  Zen key exists. Confirmed by diffing `model_perf.samples` across a probe,
  which credited `muse-spark`. **Always verify a route that way**, because a
  successful-looking `omp -p` proves nothing about which model served it.
- **`--model` rejects a `:level` suffix on some model ids, but config files
  never do.** `omp -p ... --model opencode-go/glm-5.3-flash:high` fails with
  `Model not found`, deterministically, at every level. So does
  `opencode-go/qwen3.8-flash:low`. The same suffix on `deepseek-v4-flash`,
  `minimax-m3`, `kimi-k3`, `claude-sonnet-5` and `muse-spark-1.2-contributor`
  works, and dropping the provider prefix (`--model glm-5.3-flash:high`) also
  works. **Config-file resolution is unaffected** — a project `.omp/config.yml`
  with `default: opencode-go/glm-5.3-flash:high` ran a real turn and registered
  a `model_perf` row against GLM, so config-file roles resolve correctly. This
  only bites when timing or spot-checking from the CLI; drop
  the provider prefix and it resolves.

## Measured, not guessed

Nobody publishes Muse Spark's speed — Artificial Analysis lists output tok/s as
unknown and has no TTFT, and Meta published neither. So it was measured here on
2026-08-29, on this machine, on this connection.

Method: identical prompt ("write exactly 400 words of continuous prose, no
headings or lists"), thinking level pinned so hidden reasoning tokens can't
skew it, three or more runs each, wall-clock from process start to exit.
Pinning the level matters — an unpinned first attempt under
`defaultThinkingLevel: auto` produced numbers 3x worse and was measuring
reasoning, not throughput.

| Model | Level | Wall for 400 words | Spread over runs |
| --- | --- | --- | --- |
| DeepSeek V4 Flash | low | **12.0s** | 11.0–35.8s |
| Sonnet 5 | low | **13.5s** | 12.8–13.5s |
| Muse Spark | minimal | **24.1s** | 22.6–43.8s |
| MiniMax M3 | medium | **102.1s** | single run |

DeepSeek V4 Flash beat Sonnet. Muse Spark took ~1.8x Sonnet's wall and ~2x
DeepSeek's, with a 2x spread run to run. That is why `scout` and `librarian`
first moved to DeepSeek.

> [!note] Reversed later the same day — price beat speed
> Go is a spend budget, so DeepSeek's speed was being paid for in quota:
> $0.22/$0.66 per Mtok against Muse Spark's $0.10/$0.20, plus Muse Spark's
> $0.002 cached-input rate that DeepSeek has no equivalent for. That is 7,600
> req/5h against 45,300. With the monthly window at 84% and four days left,
> `smol`, `scout` and `librarian` went to
> `opencode-go/muse-spark-1.2-contributor` — `:low`, `:low`, `:high`. Slower
> per subagent turn, and subagents run in the background where the segment
> stalls overlap with other work. Verified by running a scout turn and diffing
> `model_perf`: Muse Spark +5 samples, DeepSeek unchanged.
>
> DeepSeek stays last in the `opencode-go/*` fallback chain. The two carve-outs
> were retired the same day, so `OQGA` and `clinical-reasoning` get Muse Spark
> for `scout` and `librarian` as well.

### Why it is slow, which is not what you'd guess

Muse Spark's *generation* rate is fine. omp records per-model throughput in
`~/.omp/agent/agent.db`, table `model_perf`, and over 216 samples it reads
**95.3 tok/s — the fastest model in the table**, ahead of Sonnet's 81.1.

The wall-clock and the throughput disagree because **one Muse Spark turn is not
one generation**. Counting `model_perf.samples` before and after a single turn:

| Model | `model_perf` samples added by one 400-word turn |
| --- | --- |
| Sonnet 5 | 1 |
| DeepSeek V4 Flash | 1 |
| Muse Spark | **4–6** |

Muse Spark's reply arrives in 4–6 segments of roughly 90 tokens, and each
segment pays the full ~3.0s time-to-first-token. Six segments is ~18s of dead
time on a turn whose actual generation is under 6s. Nothing appears on stderr;
the turn simply takes twice as long.

This is a good trade for `sonic`, `advisor` and the fallback chains, where
segment stalls overlap with other work. It is a bad trade for anything you sit
and watch.

> [!note] Re-measure with the same method, not a stopwatch
> ```sh
> sqlite3 ~/.omp/agent/agent.db \
>   "SELECT model_key, CAST(samples AS INT) n,
>           ROUND(output_tokens/(gen_ms/1000.0),1) tok_s,
>           ROUND(ttft_ms/ttft_samples/1000.0,2) ttft_s
>    FROM model_perf ORDER BY tok_s DESC;"
> ```
> `tok_s` from this table is generation-phase only. It will look great for a
> model that segments. Always pair it with a wall-clock run.

Two other measured results worth keeping:

- **MiniMax M3 took 102s** for the same 400 words. It sits at `:medium` in the
  fallback chains. Fine for a fallback, but do not promote it.
- **GLM-5.3-Flash's `model_perf` row reads 1.1 tok/s over 3 samples.** Too few
  samples to be a verdict, but combined with its total absence from SWE-bench
  Verified it is not a model to hand real work to yet.

## The Codex handover — retired 2026-08-29

Paid 8/4/2026 as **ChatGPT Pro 5x ₹9,516.88**, not Plus. Monthly billing puts
the next charge at **Sep 4, 2026** even though `omp usage` reports its
`prolite` 7-day window expiring Sep 21 — the window is not the billing date.
The image you sent confirms cancellation holds access through Sep 4.

Retired 2026-08-29, six days early:

```yaml
adversary: opencode-go/grok-4.6:high
```

No login step. Grok 4.6 is in the OpenCode Go catalog (verified 7s) and now
serves the role directly. Fallback is Muse Spark. Cost is Go quota, whose
binding limit is the monthly one
(71% used with 4d18h left at time of switch). See [[Two-Stage Plan Review]]
for the pipeline it feeds.

Grok 4.6 on Go carries a 500k context window against Sol's 1M, so a very large
plan review is the one case where losing Sol actually costs something.

Fallback verified 2026-08-29: a throwaway `.omp/config.yml` pointed
`adversary` at a dead-credential catalog id (`openrouter/openai/gpt-5.6-sol`),
and `model_perf` credited `opencode-go/grok-4.6=5`, with the turn returning
"**Verdict: rethink** — caching every API …". An *unknown* model id hard-errors
instead ("No model selected"), so the chain only saves you when the id is
valid — which `openai-codex/gpt-5.6-sol` remains even after the sub ends.

> [!note] Grok effort suffixes may be ignored
> Grok honours `reasoning.effort` only for models on an allowlist over
> `/v1/responses`. A `:high` suffix can be silently dropped. Grok 4.6 has
> published effort tiers so it should be honoured, but don't assume it from the
> config alone.

If Codex survives instead, `smol: openai-codex/gpt-5.6-luna:medium` is worth
considering — SWE-V 93.0% and TB2.1 75.7% at $1/$6 beats anything in the Go
fleet on *verified* numbers. Luna is also reachable through OpenCode Go at 2,050
req/5h with no ChatGPT subscription at all.
## Which subscription

Decided 2026-08-29. You paid **ChatGPT Pro 5x ₹9,516.88** on 8/4/2026, not Plus.
The choice on the table was Pro 5x at ₹9,517/mo against SuperGrok at ₹699/mo,
with Claude Max 5x and OpenCode Go staying either way. You cancelled effective
Sep 4, keeping access through the end of the billing period.

**Neither.** `opencode-go/grok-4.6` answers in 7s and is already in the Go
plan, so SuperGrok resells a model you own. Pro 5x is the closer call, because
Go carries only `gpt-5.6-luna`, the cheapest GPT-5.6 tier ($1/$6 against Sol's
$5/$30), which is not a substitute for Sol. But Sol served exactly one role,
`adversary`, and `omp usage` showed it at **3% of its 7-day allowance** with
5-hour Spark at 0% — ₹9.5k for a review agent you barely touched.

`adversary` reviews plans, not code, which is why Grok survives the comparison.
Its strong results are abstract-reasoning ones (ARC-AGI-2 67.1%, Artificial
Analysis 61 against Sonnet's 55); its weak ones are code-execution benchmarks
this role never runs. Sol is the better programmer and that is not what the role
asks for.

What Pro 5x bought beyond omp was the ChatGPT app, Sora and deep research;
₹699 would buy the Grok app and X integration. Consumer-app calls, not config ones.

## Benchmark data behind the picks

Collected 2026-08-29. **Re-check if more than a month has passed** — the whole
fleet turned over twice in the six months before this.

### Frontier

| Model | SWE-bench Verified | Terminal-Bench 2.1 | ARC-AGI-2 | tok/s | TTFT | $/Mtok in/out | Context |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 5 | ~96–97% | not listed | 90.4% | 56.0 | not found | $5 / $25 | 1M |
| Claude Sonnet 5 | not found | not found | not found | 90.7 | not found | $2 / $10 | 1M |
| Claude Haiku 4.5 | ~73.3% | not found | not found | not found | not found | $1 / $5 | 200k |
| Claude Fable 5 | ~95% | **83.8% (#1 official)** | not found | not found | not found | $10 / $50 | 1M |
| GPT-5.6 Sol | 96.2% | SOTA claimed, no row | **92.5%** | 74.4 | not found | $5 / $30 | 1.05M |
| GPT-5.6 Terra | 95.4% | 78.4% | not found | not found | not found | $2.50 / $15 | not found |
| GPT-5.6 Luna | 93.0% | 75.7% | not found | not found | not found | $1 / $6 | not found |
| Grok 4.6 | absent from leaderboard | no standalone score | 67.1% | 59 | 40.3s (high) | $2 / $6 | 500k–2M |

SWE-bench Verified for the GPT-5.6 family are third-party
[vals.ai](https://vals.ai/benchmarks/swebench) harness runs — OpenAI never
reported Verified for this generation, only SWE-bench Pro. Terminal-Bench rows
are the official
[tbench.ai](https://www.tbench.ai/leaderboard/terminal-bench/2.1) leaderboard.

### OpenCode Go fleet

| Model | Best agentic score | tok/s | TTFT | $/Mtok in/out | Cached in | Context | req/5h | Training |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Muse Spark 1.2 Contributor | TB2.1 82.9% *(Meta official)* | **not published** | **not published** | $0.10 / $0.20 | $0.002 | 1M | 45,300 | **YES** |
| Hy4 preview | TB2.1 85.4% *(vendor image)* | not found | not found | $0.834 / $2.501 | $0.042 | 1M | 1,350 | No |
| GLM-5.3-Flash | TB2.1 84.3% *(vendor)* | 49.4 | 1.49s | $0.075 / $0.25 | $0.015 | 1M | 3,160 (2x) | No |
| Kimi K3 | SWE-V **93.4%**, TB2.1 80.9% | 35.9 | 8.85s | $3 / $15 | not found | 1M | 110 | No |
| Hy3 | SWE-V 78.0%, TB2.1 71.7% | 68.8 | 2.70s | $0.14 / $0.58 | not found | 256k | 34,400 (8x) | No |
| LongCat-2.0 | TB2.1 70.8% | 42.1 | 2.87s | $0.75 / $2.95 | not found | 1M | 11,400 | No |
| Qwen3.7 Plus | **TB2.0-Terminus 70.3%**, SWE-V 77.7% | 55.8 | 2.17s | $0.40 / $1.60 | not found | 1M | 4,300 | No |
| MiniMax M3 | SWE-V 80.5%, TB2.1 66.0% | 108.4 | 1.04s | $0.30 / $1.20 | not found | 1M | 3,200 | No |
| DeepSeek V4 Flash | SWE-V 79.0%, TB2.0 56.9% | **119.4** | **1.12s** | $0.22 / $0.66 | not found | 1M | 7,600 | No |
| Qwen3.8 Flash | LiveBench coding 72.6 | 74.0 | 2.98s | $0.15 / $0.47 | not found | 1M | 5,400 | No |
| MiMo-V2.5 | none verifiable | 63.9 | 33.9s | $0.14 / $0.28 | not found | 1M | 30,100 | No |

**Read the provenance column carefully.** Only Qwen3.7 Plus reports an agentic
score with harness, hardware, time limit and run count disclosed
([qwen.ai/blog?id=qwen3.7-plus](https://qwen.ai/blog?id=qwen3.7-plus): Harbor /
Terminus-2, 5h, 12 CPU / 24GB, averaged over 5 runs). Anything marked *(vendor)*
is self-reported on the lab's own Claude Code scaffold with generous timeouts and
has no row on the official leaderboard.

Meta was unusually restrained by comparison: they published methodology and
claimed only two benchmarks, TB2.1 and DeepSWE. GLM-5.3-Flash's 84.3% comes with
**no SWE-bench Verified number from anyone**, official or third-party.

**If subagents start producing junk, Qwen3.7 Plus is the conservative swap** —
roughly 5x GLM-5.3-Flash's price, still a fifth of Sonnet, and a number you can
actually trust.

### Budget mechanics

OpenCode Go is a **rolling spend budget, not a request quota**: $12 per 5 hours,
$30 per week, $60 per month, all three tracked by omp. The req/5h column is that
budget divided by each model's price. This is why `tiny` stays on Haiku — a
per-turn background role should not compete with subagent fan-out for the same
$12.

## Expiry warnings

> [!danger] DeepSeek's zero-retention agreement expires 2026-08-31 — two days out
> It renews monthly and was stated valid only through 2026-08-31. When the plan
> was first written DeepSeek V4 Flash held **one** role. The speed measurements
> briefly gave it five, then the price comparison took all of them back: as of
> 2026-08-29 DeepSeek holds **no role at all** and appears only as the last hop
> in the `anthropic/*` and `opencode-go/*` fallback chains. The dated agreement
> now matters much less than it did.
>
> Check [api-docs.deepseek.com](https://api-docs.deepseek.com/quick_start/pricing)
> and OpenCode's own privacy table at [opencode.ai/docs/go](https://opencode.ai/docs/go)
> on or after 2026-09-01.
>
> If ZDR has lapsed, DeepSeek is a fallback-only exposure — it serves a turn
> only when Muse Spark, GLM and MiniMax have all already failed. Judgment call,
> not the hard problem it was when it held five roles.
>
> Replacements if it lapses, in order of preference:
>
> 1. **Sonnet 5** — 13.5s vs DeepSeek's 12.0s, so you lose almost nothing on
>    speed. Costs Max quota rather than cash. This is the honest answer.
> 2. **GLM-5.3-Flash** — where it was before, but see the 1.1 tok/s reading.
> 3. **MiniMax M3** — ZDR and cheap, but measured 102s for 400 words. Fallback
>    only, do not promote.

Lower stakes:

- **Hy4 preview is not being retired.** A "preview down 8/31" signal exists but
  refers to Tencent sunsetting the separate older `Hy3 preview` SKU. OpenCode's
  docs carry no retirement language for Hy4.
- **Aider's polyglot leaderboard is dead** for this purpose — last updated
  November 2025, no 2026 model in it. Don't reach for it when re-checking.

## Ollama removal

**Done 2026-08-29.** `tiny` is back on `anthropic/claude-haiku-4-5:low` and
every trace of the local provider is gone:

- `omp/models.yml` — deleted with `git rm`. The whole file was the
  `ollama-local` provider; nothing else lived in it.
- `~/.omp/agent/models.yml` — the symlink removed.
- `install.sh` step 3i — deleted, and the step-numbering gap is marked with a
  tombstone comment in the header so nobody hunts for it. The `SKIP omp`
  message no longer names `models.yml`. Installer re-run: `linked=45`, down one
  from 46, `skipped=0`.
- `docs/2026-08-15-omp-audit.md` and `-explainer.html` — the local-model
  sections carry superseded callouts. The historical reasoning is intact on
  purpose; those are dated records of what was built and why.

Done by hand, **not** by the `git revert c474b30 0706cb7 8c56c74` path the audit
doc recorded. `omp/config.yml` has been rewritten substantially since those
commits, so the revert would have conflicted. That stale instruction is now
removed from both audit docs.

Machine state, verified:

- The Ollama **desktop app is gone** (`/Applications/Ollama.app` absent). It
  owned port 11434, so nothing is listening and `ollama-local` cannot resolve.
- **`~/.ollama` does not exist**, so both `qwen3.5:0.8b` and the 4B
  `qwen3.5:4b-mlx` weights are gone. There is no disk to reclaim and no
  `ollama rm` left to run.
- `~/.omp/agent/cache/tiny-title-runtime` still holds **381MB** and is no
  longer load-bearing. Safe to clear.

Two loose ends, neither breaking anything:

- The **Homebrew CLI is still installed** — `ollama` 0.33.0 at
  `/opt/homebrew/bin/ollama`, with no server running. `brew uninstall ollama`
  when convenient.
- `omp models` **still lists two phantom entries**, `ollama/qwen3.5:0.8b` and
  `ollama/qwen3.5:4b-mlx`, from omp's built-in `ollama` provider. Nothing can
  serve them: no server, no weights. This is precisely the stale-discovery-cache
  behaviour the deleted `models.yml` warned about in its own header comment,
  which retroactively justifies having declared a full custom provider instead
  of overriding the built-in one.

## Verify

```sh
./install.sh --no-plugins                       # relinks projects/ (step 3j)
omp models                                      # every role resolves
omp -p "say ok"                                 # default path works

# carve-outs: Muse Spark unreachable in these two, reachable at the root
cd ~/dev/OQGA               && omp config list | grep -c muse-spark   # 0
cd ~/dev/clinical-reasoning && omp config list | grep -c muse-spark   # 0
cd ~/dev                    && omp config list | grep -c muse-spark   # > 0

# Ollama fully gone
ls ~/.ollama 2>&1                               # no such file
ls ~/.omp/agent/models.yml 2>&1                 # no such file
grep -c models.yml install.sh                   # 0 outside the header tombstone
```

## Related

- [[OMP Audit]] — what the local title model was and why
- [[Two-Stage Plan Review]] — the pipeline `adversary` feeds
