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
> Anthropic drives, plans and looks at pictures. DeepSeek V4 Flash does the
> work you wait on. Muse Spark does the work nobody waits on. SuperGrok is the
> outside opinion. Two repos opt out of Muse Spark entirely.

> [!success] Applied 2026-08-29
> `omp/config.yml`, `omp/projects/*.config.yml`, `install.sh` steps 3e/3j, the
> `.gitignore` entries in `OQGA` and `clinical-reasoning`, and the
> [Ollama removal](#ollama-removal) are all live. One thing is **not** done:
> the [Codex handover](#the-codex-handover), which waits on SuperGrok.
>
> Muse Spark was then **measured** and moved off `scout` and `librarian`. See
> [Measured, not guessed](#measured-not-guessed) — that section supersedes the
> speed reasoning in any earlier draft of this file.

## What changed and why

Four decisions drive the whole layout.

**Muse Spark 1.2 Contributor is the best value in reach on quality-per-dollar,
and the ZDR trade is accepted.** Terminal-Bench 2.1 of 82.9% ([Meta's own
figure](https://research.meta.ai/blog/introducing-muse-code-and-muse-spark-1-2))
against Claude Fable 5's 83.8% at the #1 official spot — for $0.10/$0.20 instead
of $10/$50. It tops the Go fleet on Arena's coding board (1526±25, ahead of Hy3
1500, MiniMax M3 1499, GLM-5 1497), and Meta demonstrated it sustaining 1,000+
tool calls across a 24-hour job. 45,300 requests per 5 hours is 14x
GLM-5.3-Flash's 3,160.

**But it is slow in wall-clock, so it only gets work nobody waits on.** This is
the one place the plan changed after measurement rather than reading — see
[Measured, not guessed](#measured-not-guessed).

The price is real, though: it is the **only** model in the Go lineup marked
"Model training: Yes / Data retention: Not ZDR" on
[opencode.ai/docs/go](https://opencode.ai/docs/go). Meta says the same at
[dev.meta.ai/docs/pricing-rate-limits](https://dev.meta.ai/docs/pricing-rate-limits)
— the contributor tier is discounted *in exchange for* training rights. Every
other Go model is "Not used / 0 days". That trade is fine for `homelab`,
`dotfiles`, `agmtech` and the rest. It is not a personal call for two repos, so
they get [their own configs](#the-two-carve-outs).

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
| `adversary` | GPT-5.6 Sol | low | **temporary** — see [handover](#the-codex-handover) |
| `smol` | DeepSeek V4 Flash | low | prewalk + vibe `fast` tier, so speed is everything: 119 tok/s, 1.12s TTFT, SWE-V 79% |
| `tiny` | Haiku 4.5 | low | fires before every turn under `defaultThinkingLevel: auto`, so its TTFT lands on your wait; free under Max, warm connection |
| `commit` | Muse Spark | low | cheaper on output than Qwen3.8-Flash and a far better model; budget irrelevant at 45,300/5h |
| `advisor` | Muse Spark | high | reviews every transcript delta: huge input, tiny output, and cached input is $0.002/M. Inert while `advisor.enabled` is false |

Subagents:

| Agent | Model | Effort | Reason |
| --- | --- | --- | --- |
| `scout` | DeepSeek V4 Flash | low | you wait on scouts, and it measured **faster than Sonnet** on identical work; 1M context, SWE-V 79%, ZDR |
| `librarian` | DeepSeek V4 Flash | high | same reason — a library answer is a long report you are blocked on |
| `sonic` | Muse Spark | low | mechanical bulk, runs in parallel, nobody waits on any single one |
| `reviewer` | Kimi K3 | high | SWE-V 93.4%, the highest verified score in the fleet; 110 req/5h is fine for review volume |
| `security-reviewer` | Kimi K3 | high | same |

`adversary` is deliberately **absent** from `agentModelOverrides` —
`omp/agents/adversary.md` pins `model: "@adversary"`, so the role drives it and
an override would be dead config.

**The rule that decides Muse Spark placement:** it gets a role only when the
output is short (`commit`), or nobody is blocked on it (`advisor`, `sonic`, the
fallback chains). Every role where you sit and wait for a long answer —
`default`, `smol`, `tiny`, `scout`, `librarian` — goes to Anthropic or DeepSeek.

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
> `omp/projects/*.config.yml` is the **opposite** — omp reads those and never
> writes them. Verified: 35 and 30 comment lines still present after the global
> file was stripped to zero. Rationale that must sit next to the values belongs
> there.
>
> An earlier claim in `install.sh` step 3e that "nothing is reordered or
> dropped" was false and has been corrected in place.

## Fallback chains

Key specificity is `provider/model-id` > `provider/*` > role name > `default`
([settings.md](omp://settings.md)). Two consequences are baked into the config:

- There is **no `openai-codex/*` key**. It would shadow the `adversary` role
  chain, which is the only reason a Codex model is still assigned.
- The `adversary` role chain puts **Grok first**, so the cross-lineage property
  survives a Codex failure. It is unresolvable until `/login xai-oauth`;
  unavailable entries are skipped, so it is safe to carry now and activates
  itself on login.

Two invariants worth restating because they are easy to undo:

- **No `anthropic/*` entry in any chain.** A fallback exists *because* Anthropic
  failed. Sending the retry back there wastes it.
- **Muse Spark is absent from the `opencode-go/*` chain.** If the Go gateway is
  what failed, the next hop should not be another model behind the same path.
  GLM-5.3-Flash and MiniMax M3 are the diversity within Go.

## The two carve-outs

`OQGA` (Optum HEDIS chart abstraction) and `clinical-reasoning` (real nephrology
handover notes in `cases/`) must not reach Muse Spark. Each gets a project
config that pins every Muse Spark role to a ZDR model:

| Role | Carve-out model | Why |
| --- | --- | --- |
| `scout` | DeepSeek V4 Flash `low` | you wait on it, and it is the fastest measured thing in reach |
| `librarian` | DeepSeek V4 Flash `high` | same |
| `sonic` | Qwen3.8 Flash `low` | mechanical bulk, ZDR, nobody waits |
| `advisor` | GLM-5.3-Flash `high` | huge input, tiny output, nobody waits, and `advisor.enabled` is false anyway |
| `commit` | Haiku 4-5 `low` | free under Max, and a commit message is 20 tokens |

`scout` and `librarian` were on GLM-5.3-Flash in the first version of these
files. They moved to DeepSeek once Muse Spark was measured, because the same
finding applies here: GLM reads **1.1 tok/s over 3 samples** in omp's
`model_perf` and has no SWE-bench Verified score from anyone, so it should not
hold a role you sit and wait on. It keeps `advisor`, where the latency is free.
DeepSeek is `Not used / 0 days` on
[opencode.ai/docs/go](https://opencode.ai/docs/go), so it is legal here — but
see the [expiry warning](#expiry-warnings), because that is dated.

Project files live in **`omp/projects/<repo>.config.yml`** and are symlinked to
`~/dev/<repo>/.omp/config.yml` by `install.sh` step 3j. The repo is the source
of truth; the symlink is machine-local, which is why `.omp/` is in each target
repo's `.gitignore` and why step 3j warns when it isn't.

This works despite `modelRoleStorage: global`: that setting governs where the
TUI *saves* roles, not where they are read from. Per
[config-usage.md](omp://config-usage.md), "Native `.omp/config.yml` model roles
are then reapplied as the authoritative project model-role layer."

> [!danger] `fallbackChains` deep-merges — restate every key
> A project file's `fallbackChains` merges with global, so any chain key it
> omits **survives from global as-is**. The first version of these files omitted
> `adversary`, and `omp config list` run from `OQGA` showed the global
> `adversary` chain intact, Muse Spark included. The carve-out had a hole in it.
> Both files now restate `adversary` explicitly. Restate every chain key that
> exists globally, even to say the same thing.

Verify the carve-out from inside each repo:

```sh
cd ~/dev/OQGA && omp config list | grep -cE 'muse-spark'   # must be 0
cd ~/dev && omp config list | grep -cE 'muse-spark'        # must be > 0
```

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
- **`xai-oauth/grok-4.6` does not resolve yet**, as expected without SuperGrok.
- **`--model` rejects a `:level` suffix on some model ids, but config files
  never do.** `omp -p ... --model opencode-go/glm-5.3-flash:high` fails with
  `Model not found`, deterministically, at every level. So does
  `opencode-go/qwen3.8-flash:low`. The same suffix on `deepseek-v4-flash`,
  `minimax-m3`, `kimi-k3`, `claude-sonnet-5` and `muse-spark-1.2-contributor`
  works, and dropping the provider prefix (`--model glm-5.3-flash:high`) also
  works. **Config-file resolution is unaffected** — a project `.omp/config.yml`
  with `default: opencode-go/glm-5.3-flash:high` ran a real turn and registered
  a `model_perf` row against GLM, so the roles in `omp/projects/*.config.yml`
  are sound. This only bites when timing or spot-checking from the CLI; drop
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
moved to DeepSeek.

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

## The Codex handover

When the ChatGPT subscription lapses, one line:

```yaml
adversary: xai-oauth/grok-4.6:high
```

Then `/login xai-oauth`. omp runs an RFC 8628 device flow against `auth.x.ai`
with the `grok-cli:access` scope and bills the SuperGrok quota at zero marginal
cost, so it never touches the OpenCode Go budget. Grok is already first in the
`adversary` fallback chain, so nothing else moves. See [[Two-Stage Plan Review]]
for the pipeline it feeds.

> [!note] Grok effort suffixes may be ignored
> Grok honours `reasoning.effort` only for models on an allowlist over
> `/v1/responses`. A `:high` suffix can be silently dropped. Grok 4.6 has
> published effort tiers so it should be honoured, but don't assume it from the
> config alone.

If Codex survives instead, `smol: openai-codex/gpt-5.6-luna:medium` is worth
considering — SWE-V 93.0% and TB2.1 75.7% at $1/$6 beats anything in the Go
fleet on *verified* numbers. Luna is also reachable through OpenCode Go at 2,050
req/5h with no ChatGPT subscription at all.

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
> was first written DeepSeek V4 Flash held **one** role. After the speed
> measurements it holds **five**: `smol`, `scout` and `librarian` globally, plus
> `scout` and `librarian` inside both carve-out repos. It is now the single
> biggest privacy dependency in the config, and it is the one with a dated
> agreement.
>
> Check [api-docs.deepseek.com](https://api-docs.deepseek.com/quick_start/pricing)
> and OpenCode's own privacy table at [opencode.ai/docs/go](https://opencode.ai/docs/go)
> on or after 2026-09-01.
>
> If ZDR has lapsed, the global roles are a judgment call, but the **carve-outs
> are not** — DeepSeek joins Muse Spark as a model `OQGA` and
> `clinical-reasoning` must exclude, from their roles *and* their fallback
> chains, where it currently sits last in every chain.
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
