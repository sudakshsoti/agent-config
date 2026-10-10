# Ladder benchmarks for the SuperGrok cutover (read 2026-10-10)

Scope: every candidate named in the assignment plus the two added by follow-up
(`claude-fable-5-1`, `claude-mythos-5-1`). Extends — does not redo —
`docs/research/chatgpt-vs-supergrok-coding-2026-10.md` §3 (same-day headlines
for Opus/Sonnet 5.5, GPT-6 family, Grok 4.6/4.7, GLM-5.3-Flash reused where
re-verified below). Local probes quoted here ran 2026-10-10 on this checkout
(Anthropic subscription OAuth, retry disabled): `anthropic/claude-haiku-5-5` →
`ok`; `anthropic/claude-fable-5-1` → `ok`; `anthropic/claude-mythos-5-1` → 404
`not_found_error`. No config changed, no login performed.

Methods: Artificial Analysis model pages (static fetch) plus the per-provider
comparison dataset embedded in those pages (fields: `intelligenceIndex`,
`capabilities.engineering`, `terminalBench40/21`, `omniscience`,
`omniscienceHallucinationRate`); official Terminal-Bench 4.0 board
(https://www.tbench.ai, headless Chromium, table needed scroll+wait);
LMArena WebDev + Text (https://arena.ai, headless Chromium, Overall boards
dated Oct 8 2026); DesignArena overall + General Purpose
(https://www.designarena.ai/leaderboard/code, headless Chromium);
Anthropic docs + support articles; xAI docs; OpenRouter `/api/v1/models`
snapshot 2026-10-10. Anything not from a primary source is marked UNVERIFIED.

Definitions: AA Index = Artificial Analysis Intelligence Index v4.3.2 (10
evals incl. Terminal-Bench 4.0; max-effort variant shown unless noted). TB
official = tbench.ai resolution rate (harness noted per row). AA TB4.0 run =
Artificial Analysis' own TB4.0 run (mini-swe-agent harness). Halluc. = AA
`omniscienceHallucinationRate` (0–1, lower is better; the matching eval page
labels the complement "AA-Omniscience Non-Hallucination Rate", i.e. 1 −
hallucination rate). Ranks without dates are the Oct 8 2026 board snapshots.

## 1. Benchmark table (headline variants)

| Model | AA Index | AA speed / $/task | TB official 4.0 | AA TB4.0 run | Halluc. | WebDev | Text | DesignArena overall (GP) | Ctx / API $/M in/out | Efforts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-opus-5-5 (max) | 58, #1/227 | 97 tok/s, $5.98 | 64.8% #1 (Claude Code) | 59.6% | 0.59 | #1 1813 (max) | #2 1507 (high; no max row) | #1 1403 (#12 GP 1306) | 1M / $4/$20 | low..max (omp); default medium, always on |
| claude-sonnet-5-5 (max) | 56, #2/227 | 142 tok/s, $5.46 | 61.8% #2 (Claude Code) | 63.6% | 0.47 | #3 1774 (xhigh) | #32 1476 (xhigh) | #5 1360 (#28 GP 1281) | 1M / $2/$10 | low..max (omp); default high |
| claude-haiku-5-5 (max) | 43 | 237 tok/s, $0.21 | not listed (rel. Oct 7) | 32.8% | 0.40 | #30 1587 (high row only, 978 votes) | not listed | not listed | API 1M, omp 100K / $0.10/$0.50 ≤100K, $0.50/$2.50 above | low..max (omp); default medium |
| claude-haiku-4-5 | not listed (AA 404) | — | not listed | — | — | #119 1330 | #143 1414 | GP #129 1133 | 200K / $1/$5 | no effort param (budget_tokens) |
| claude-fable-5-1 (max) | 53 | 70 tok/s, $7.63 | 57.9% #5 (Claude Code) | 55.1% | 0.73 | #5 1744 (max) | #6 1501 (max) | #10 1340 (#3 GP 1337) | 1M / $10/$50 | low..max (omp); default high, always on |
| claude-mythos-5-1 | not listed (AA 404; no arena rows) | — | not listed | — | — | not listed | not listed | not listed | 1M / $10/$50 | same as Fable; verification-required, 404 on this plan — excluded |
| grok-4.7 (xhigh) | 46 | 74 tok/s, $3.74 | 37.6% #10 (Grok Build) | 25.8% | 0.29 | #15 1639 (xhigh) | #90 1443 (xhigh) | GP #4 1334 | 500K / $2/$6 (<200K), $4/$12 (≥200K) | low/medium/high/xhigh, default high, cannot disable |
| grok-4.6 (high) | 44 | 60 tok/s, $1.48 | 20.3% #16 (Grok Build) | 21.2% | 0.34 | #25 1617 (high) | #72 1454 (high) | GP #20 1292 | 500K / same 2-tier pricing | same effort set as 4.7 |
| grok-4.7-fast | no page (Cursor/Build only) | — | not listed | — | — | not listed | not listed | not listed | 2x std rates (1.5x long-ctx), billed via plan | oauth exposure UNVERIFIED |
| grok-build-0.1 | no AA page; no arena rows anywhere | — | not listed | — | — | not listed | not listed | not listed | 256K / $1/$2 (API) | subscription-catalog exposure UNVERIFIED |
| grok-code-fast-1 | 14 (Aug 2025 vintage) | no price/speed cells | not listed | null | 0.79 | #140 1167 (789 votes) | not listed | GP #156 1060 | UNVERIFIED (arena lists $0.20/$1.50) | UNVERIFIED |
| deepseek-v4.1-flash (max) | 39 | 217 tok/s, $0.27 | not listed | 26.8% | 0.54–0.97 across provider rows (ambiguous, see §4) | #23 1619 (max) | #39 1475 (max) | #12 1325 (#12 GP 1306) | OR `deepseek/deepseek-v4.1-flash` 1M ctx, $0.30/$1.20 | max + non-reasoning (AA 25) |
| z-ai/glm-5.3-flash | 42 | 58 tok/s, $0.25 | 35.8% #12 (as non-reasoning, Claude Code) | 32.8% | 0.28 | #26 1609 | #38 1475 | GP #26 1288 | OR `z-ai/glm-5.3-flash` 1M ctx, $0.15/$0.50 | single reasoning profile on AA |
| z-ai/glm-5.3 (max) | 45 | 83 tok/s, $2.01 | 41.8% #9 (Claude Code) | 41.9% | 0.30 | #22 1622 (max) | #27 1478 (max) | ~1313 overall (GP #17 1296) | OR `z-ai/glm-5.3` 1M ctx, $0.04/$4.80 list (odd split — verify at invoice) | max + low (AA 34) |
| moonshotai/kimi-k3 (max) | 44 | 39 tok/s, $2.00 | not listed | 12.6% | 0.53 | #14 1654 (max) | #16 1488 (max) | #4 1367 (#6 GP 1329) | OR `moonshotai/kimi-k3` 1M ctx, $0.64/$13.50 | max + low (AA 30) |
| minimax/m3 | 29 | 101 tok/s, $0.51 | not listed | 2.0% | 0.18 | #63 1482 | #96 1440 | GP #55 1240 | OR `minimax/minimax-m3` 1M ctx, $0.30/$1.20 | single profile on AA |
| qwen3.8-max (0902) | 45 | 36 tok/s, $5.41 | 27.0% #13 (as 0902, Claude Code) | 18.7% | 0.42 | #10 1674 (0902, Prelim) / #11 1672 | #22 1483 | GP #26 1288 | OR `qwen/qwen3.8-max-0902` 1M ctx, $2/$6 | single profile on AA |
| openai/gpt-6.1-sol (max) | 52 | 57 tok/s, $0.72 | 58.2% #3 (Codex) | 56.1% | 0.54 | #4 1755 (max) | #21 1484 (max) | #8 1348 (#14 GP 1305) | OR `openai/gpt-6.1-sol` 1.05M ctx, $2/$10 | max/high/medium/low (48/42 at med/low) |
| openai/gpt-6-luna (max) | 38 | 137 tok/s, $0.07 | 16.4% #19 (Codex) | 12.6% | 0.77 | #34 1581 (max) | #91 1443 (max) | GP #42 1260 | OR `openai/gpt-6-luna` 1.05M ctx, $0.10/$0.50 | max + low (AA 22) + non-reasoning (AA 18) |
| google/gemini-3.8-flash (high) | 41 | 125 tok/s, $1.24 | 19.1% #17 (mini-SWE-agent) | 19.7% | 0.55 | #31 1583 (high, Prelim) | #8 1497 (high, Prelim) | ~1309 overall (#15 GP 1303) | OR `google/gemini-3.8-flash` 1M ctx, $0.75/$3.75 | high + medium (AA 40) + low (AA 33) |

Notable non-candidate observed while scraping (context, not a proposal): `gemini-4-argon-high`
— AA 53 ($1.99/task), TB official absent, WebDev #9 1678 (Preliminary), Text #1 1525
(Preliminary) — but **absent from the OpenRouter catalog snapshot 2026-10-10**, so it
cannot serve as an OpenRouter backstop today.

Per-effort AA Index values that matter for chain rungs (all from AA variant pages,
read 2026-10-10): Opus-5.5 medium 51 / low 42; Sonnet-5.5 high 47 / medium 41 / low 36;
Haiku-5.5 medium 34 ($0.05/task, 169 tok/s) / low 29 ($0.02/task, 180 tok/s);
Fable-5.1 medium 49 ($2.98) / low 47 ($2.37); Grok-4.7 high 46 ($2.73) / low 42 ($1.25);
Grok-4.6 xhigh 44 ($1.75) / medium 43 ($1.14) / low 35 ($0.38); 6.1-Sol medium 48 ($0.21) /
low 42 ($0.13); Luna low 22 / non-reasoning 18; DeepSeek non-reasoning 25 ($0.15);
GLM-5.3 low 34 ($0.85); Kimi-K3 low 30 ($1.15); Gemini-3.8-Flash medium 40 / low 33.

## 2. Cited bullets

### Anthropic 5.5 family + Fable + Mythos
- Releases (Anthropic model pages, read 2026-10-10): Fable 5.1 and Mythos 5.1
  **September 1, 2026** (https://platform.claude.com/docs/en/models/mythos-5-1/overview);
  Opus 5.5 **September 22, 2026**; Sonnet 5.5 **September 28, 2026**;
  Haiku 5.5 **October 7, 2026** (https://platform.claude.com/docs/en/models/haiku-5-5/overview).
  TB official confirms the same dates (tbench.ai, read 2026-10-10).
- Context/output/pricing (same pages): all five are **1M context / 128K output**
  (300K output on Batch API with beta header for Opus/Sonnet/Haiku 5.5); Opus 5.5
  $4/$20, Sonnet 5.5 $2/$10, Fable/Mythos 5.1 $10/$50, Haiku 5.5 **tiered: $0.10/$0.50
  up to 100K tokens, $0.50/$2.50 above** — the tier boundary is presumably what
  omp surfaces as "100K context" (UNVERIFIED mapping; omp shows 100K ctx / 128K out).
- Thinking (same pages + Haiku comparison table): Opus 5.5 adaptive always-on,
  **default `medium`**; Sonnet 5.5 adaptive, **default `high`**; Haiku 5.5 adaptive,
  **default `medium`** (new: Haiku supports the effort parameter; Haiku 4.5 did not);
  Fable/Mythos 5.1 adaptive always-on, **default `high`**. Cache-read discounts:
  Fable/Mythos 2.5%, Opus/Sonnet 5.5 5%, Haiku 10%. Haiku 5.5 uses the post-4.7
  tokenizer, so identical text counts ~30% more tokens than on Haiku 4.5.
- Plan treatment of Fable (https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan,
  read 2026-10-10): Fable 5/5.1 are **not a separate pool** — on Max / premium Team /
  premium seat-based Enterprise they draw from the regular weekly limits up to a
  **50% cap** (never more than the weekly limit; tracked in usage settings); on Pro /
  standard seats they are **usage-credits-only from the first message** (API rates).
  Consequence: routing Fable on a Pro plan silently spends money; routing it on Max
  spends the same pool as everything else, capped at half.
- Mythos 5.1 (same overview page): "the same model as Claude Fable 5.1, available
  **only to organizations verified** through Anthropic's verification programs";
  status "Active (verification required)". Local probe 404s on this plan — consistent.
  **No benchmarks exist anywhere checked** (no AA page, no arena rows), so even if
  access were granted there is no evidence for ladder placement. Excluded.
- omp catalog state per plan gate note (2026-10-10, retry-disabled probes): Haiku 5.5
  and Fable 5.1 answer `ok`; Mythos 5.1 404s. Fable reachable ⇒ this plan is either
  Max/premium-seat or has usage credits enabled — **plan tier UNVERIFIED**, verify
  before routing Fable anywhere (see §5).

### xAI
- API prices/context (https://docs.x.ai/developers/pricing, read 2026-10-10):
  grok-4.7/4.6 **500K ctx**, $2/$6 below 200K prompt tokens, $4/$12 above (cached
  $0.50/$1.00); **grok-build-0.1: 256K ctx, $1/$2** ($2/$4 long-ctx); no
  grok-code-fast-1 or grok-4.7-fast rows on the public API page.
- Reasoning (https://docs.x.ai/developers/model-capabilities/text/reasoning, read
  2026-10-10): grok-4.7/4.6 support `reasoning_effort` **low/medium/high/xhigh**,
  default high, **cannot be disabled**; xhigh exists on 4.6+. No `max`/`minimal` on
  the API side — omp's effort scale is its own mapping (UNVERIFIED how omp maps
  `max` for Grok).
- 4.7 Fast (same pricing page): "the same Grok 4.7 model served on faster
  infrastructure", **Cursor- and Grok-Build-only, 2x token rates (1.5x long-context),
  not on the public API**, billed through the plan there; Build's free tier excludes
  it. Whether `xai-oauth` traffic can reach it is UNVERIFIED.
- Grok Build (https://docs.x.ai/build/overview, read 2026-10-10): the coding agent
  (TUI/headless/ACP, browser auth); docs name **grok-4.7 as the latest model** and
  show custom-model config, but publish **no subscription model catalog** — which ids
  (`grok-4.7`? `grok-build-0.1`? `grok-4.7-fast`?) a SuperGrok login exposes to
  third-party clients is UNVERIFIED until `omp models xai-oauth` post-login.
- SuperGrok quotas: no change since the companion doc — one shared weekly pool, no
  published per-tier numbers (https://docs.x.ai/grok/faq, https://x.ai/pricing, read
  2026-10-10). TB official confirms Grok 4.7 runs under the **Grok Build** harness
  (37.6%), i.e. Build-side usage is real harness-comparable traffic against the same
  pool.
- Cheap-slot evidence gap: `grok-build-0.1` has **zero published benchmarks** (no AA
  page, no WebDev/Text/DesignArena rows, no TB row). Its siblings bracket it only
  loosely: grok-4.6-low AA 35, grok-4.7-low AA 42. Fitness for scout/commit is
  UNVERIFIED from primary sources — the draft's "CHEAP = build-0.1 if present"
  rests on price ($1/$2, cheapest xAI coding model) and 256K ctx, not on measured
  quality. `grok-code-fast-1` (the only cheap-xAI-adjacent model with numbers) is
  disqualifyingly weak: AA 14, WebDev #140, DesignArena GP #156, hallucination 0.79.

### OpenRouter backstops (OR catalog snapshot + AA, read 2026-10-10)
- `deepseek/deepseek-v4.1-flash` ($0.30/$1.20, 1M): AA 39 max / 25 non-reasoning;
  TB official not listed; AA TB run 26.8%; WebDev #23; Text #39; DesignArena #12.
  Hallucination ambiguous (0.54 vs 0.97 across AA provider rows) — see §4.
- `z-ai/glm-5.3-flash` ($0.15/$0.50, 1M): AA 42; TB official 35.8% (run as
  non-reasoning under Claude Code); AA TB run 32.8%; WebDev #26; Text #38;
  DesignArena GP #26; hallucination 0.28 — the lowest of any cheap backstop.
- `z-ai/glm-5.3` ($0.04/$4.80 list — lopsided split, verify at invoice; batch
  variant $0.45/$2.00): AA 45 (low 34); TB official 41.8% #9; WebDev #22; Text #27;
  hallucination 0.30.
- `moonshotai/kimi-k3` ($0.64/$13.50, 1M): AA 44 (low 30); TB official not listed;
  AA TB run 12.6%; WebDev #14; Text #16; DesignArena #4 — the best designer of the
  backstop set, but pricey output and no TB signal.
- `minimax/minimax-m3` ($0.30/$1.20, 1M): AA 29; AA TB run 2.0%; WebDev #63;
  Text #96; DesignArena GP #55; hallucination 0.18 (lowest measured — on a model too
  weak to use for review).
- `qwen/qwen3.8-max-0902` ($2/$6, 1M): AA 45; TB official 27.0% (as 0902);
  WebDev #10/11; Text #22; hallucination 0.42.
- `openai/gpt-6.1-sol` ($2/$10, 1.05M): AA 52 (med 48 / low 42); TB official 58.2%
  #3; WebDev #4; Text #21; DesignArena #8; hallucination 0.54. Strong but same price
  class as Sonnet and highest hallucination of the review-grade backstops.
- `openai/gpt-6-luna` ($0.10/$0.50, 1.05M): AA 38 (low 22 / non-reasoning 18);
  TB official 16.4%; WebDev #34; Text #91; DesignArena GP #42; hallucination 0.77.
  Fast and nearly free, but weak judgment and hallucination-prone — unfit for review.
- `google/gemini-3.8-flash` ($0.75/$3.75, 1M; latest Google model **on OpenRouter**):
  AA 41 (med 40 / low 33); TB official 19.1%; WebDev #31 (Prelim); Text #8 (Prelim);
  hallucination 0.55.
- **Review-fallback pick (non-Anthropic, non-xAI, intelligence-per-dollar with low
  hallucination): `z-ai/glm-5.3-flash`** — highest cheap-backstop AA (42), lowest
  cheap-backstop hallucination (0.28), only cheap backstop with an official TB row
  (35.8%), cheapest per-task ($0.25). For rungs where review-grade judgment matters
  more than per-token price, step up to **`z-ai/glm-5.3`** (AA 45, TB official 41.8%,
  hallucination 0.30) rather than to 6.1-Sol (AA 52 but hallucination 0.54, 8x the
  input price, and OpenAI-lineage where the ladder already leans on GPT history).

## 3. Subscription / catalog answers
- SuperGrok exposes to third-party clients: UNVERIFIED (no primary catalog; close
  with `omp models xai-oauth` post-login per plan gate 0). Public API ≠ subscription
  catalog: 4.7-Fast is documented Cursor/Build-only; build-0.1's subscription
  presence is assumed by the draft, not evidenced.
- Published per-tier SuperGrok usage numbers: none (reaffirmed 2026-10-10).
- Fable separate pool: no — same weekly pool, 50% cap on Max/premium, credits-only
  on Pro. The "Claude 7 Day (Fable)" window in `omp usage` reflects that 50% cap
  tracker, not a separate pool (interpretation — UNVERIFIED against Anthropic docs,
  which say only "tracked in usage settings").
- Mythos on subscription: no (verification-gated API model; 404 locally).

## 4. Gaps (UNVERIFIED, priority order)
1. `omp models xai-oauth` catalog (4.7? 4.6? build-0.1? 4.7-fast?) + effort mapping
   (esp. what omp `max` sends Grok) — one post-login command closes it.
2. This Anthropic plan's tier (Max/premium vs Pro/standard) + whether usage credits
   are enabled — determines whether Fable 5.1 is pool-capped or money-burning.
3. `grok-build-0.1` quality: no benchmarks anywhere; first-week scout/commit
   sampling or removal from quality-sensitive paths needed.
4. DeepSeek V4.1 Flash hallucination: AA provider rows disagree (0.54 vs 0.97);
   treat its hallucination rate as unverified, not as 0.54.
5. SWE-bench Verified per-model for all 2026-10 candidates: official board's newest
   rows are Feb 2026 (Claude 4.5 Opus 76.8% top) — stale for this ladder; use TB.
6. Haiku 5.5 TB official (released Oct 7, too new), Haiku 5.5 Text/DesignArena rows,
   Mythos benchmarks (none exist), omp's "100K context" semantics vs the API's 1M +
   100K price tier.
7. OR `z-ai/glm-5.3` $0.04/$4.80 split and `:batch`/`:pro` suffix semantics at invoice.
8. Gemini 4 Argon has no OpenRouter row (2026-10-10 snapshot) — re-check if Google
   becomes the backstop lineage.

## 5. Implications for the draft ladder (`plans/supergrok-cutover.md`)

- **adversary/reviewer/advisor → `grok-4.7:high`: keep, with two evidence notes.**
  Grok 4.7-high is AA 46 ($2.73/task) with TB official 37.6% and WebDev #15 — a
  genuine second lineage, far above the outgoing Go baseline (GLM-Flash AA 42) but
  far below Sonnet-5.5-high (AA 47, TB 61.8%) at the same effort. Consider `:xhigh`
  for `adversary` specifically (AA 46, $3.74/task, DesignArena GP #4 1334 shows
  Grok 4.7's visual judgment is relatively stronger than its TB rank) — costs pool,
  so keep reviewer/advisor at high. Do NOT substitute Fable 5.1 here without closing
  gap §4.2: it is the strongest reviewer on paper (AA 53, TB 57.9%, WebDev #5) but
  same-lineage as Claude (defeats the cross-lineage purpose) and either pool-capped
  (Max) or money-burning (Pro).
- **research → `grok-4.7:high`: keep.** Best xAI synthesizer + the documented X-tool
  edge (prior doc §1). No benchmark contradicts it.
- **scout/smol/tiny/commit + sonic → `grok-build-0.1`: AMEND — gate on evidence.**
  build-0.1 has no measured quality anywhere (§2 xAI). If the gate finds it, restrict
  it to commit-message/smol first and sample quality before giving it scout/sonic;
  the draft's fallback (GROK at `:low`, AA 42) is actually the evidence-backed cheap
  path. `grok-code-fast-1` MUST NOT be substituted here (AA 14, WebDev #140).
- **Cheap roles: add a Haiku-5.5 pool-relief option (proposed change).** Every Grok
  cheap token spends the one undisclosed weekly pool. Haiku 5.5-low (AA 29,
  $0.02/task, 180 tok/s, separate Anthropic pool) or -medium (AA 34, $0.05/task)
  outranks Luna-non-reasoning (AA 18) and DeepSeek-non-reasoning (AA 25) as a cheap
  rung, with 1M API context (100K in omp — watch the tier boundary: prompts over
  100K cost 5x). Proposed: if week-1 pool pressure appears, move
  scout/smol/tiny/commit to `anthropic/claude-haiku-5-5:low` before touching review
  roles — this already matches the draft's step-8 instinct, and the numbers now back
  it (Haiku-low 29 ≈ GLM-Flash-class cheap intelligence at 1/10th the $/task).
  Caveat: Haiku 5.5 has no Text/DesignArena rows yet and only 978 WebDev votes —
  keep it off design-sensitive paths.
- **code-worker → Sonnet-5.5:medium: keep, and the data strengthens it.**
  Sonnet-medium is AA 41 ($0.48/task) with the family max at TB official 61.8% #2 and
  AA TB run 63.6% (top of board) — the best agentic-coding signal in the ladder.
  Default effort for Sonnet 5.5 is `high` per Anthropic; the draft's `:medium` is a
  deliberate cost choice (AA 41 ≈ Grok-4.7-low 42 at 1/3rd the $/task) — keep, and
  escalate single hard tasks to `:high` (AA 47) rather than to another model.
- **Haiku 5.5 as chain rung (replacing 4.5): keep, with the context warning as
  written.** Numbers added: Haiku-5.5-high (AA ~41.3 row, WebDev #30) is a far
  stronger fallback than Haiku 4.5 (WebDev #119, Text #143, DesignArena GP #129);
  but omp-side context halves (200K→100K) and the new tokenizer inflates token
  counts ~30%, so long Sonnet sessions can still overflow it — chains-only, never
  primary, as drafted.
- **OpenRouter last rung: replace DeepSeek with GLM-5.3-Flash (proposed change).**
  Head-to-head: AA 42 > 39; hallucination 0.28 vs 0.54–0.97 (ambiguous);
  $0.25 vs $0.27/task; TB official 35.8% vs not listed; AA TB run 32.8% vs 26.8%.
  DeepSeek leads only on WebDev (#23 vs #26, 1619 vs 1609), speed (217 vs 58 tok/s),
  and DesignArena (#12 vs GP #26 — though different boards). For fallback chains
  whose job is safe judgment when subscriptions are exhausted, GLM-Flash wins on
  the review-relevant axes. Proposed: `openrouter/z-ai/glm-5.3-flash` as the last
  rung everywhere the draft has DeepSeek; optionally `z-ai/glm-5.3` (AA 45, TB
  41.8%, hall 0.30) as the review-chain rung specifically, keeping Flash for cheap
  chains. Also note the draft's OR id form (`openrouter/deepseek/deepseek-v4.1-flash`)
  vs catalog id (`deepseek/deepseek-v4.1-flash`) — verify omp's OR prefix convention
  before editing config.
- **Fable 5.1: do NOT add as a ladder rung now (proposed non-change).** Re reachable
  locally, AA 53 / TB 57.9% / WebDev #5 / Text #6 / DesignArena #10 are the best
  non-Opus numbers in the table — but it shares Claude lineage (no review value)
  and shares the weekly pool (no capacity value), at $10/$50 with the highest
  measured hallucination rate in its class (0.73 — treat directionally, §1). Revisit
  only if code-worker needs a same-lineage escalation above Sonnet-high.

## Sources (all read 2026-10-10 unless noted)
- https://artificialanalysis.ai/models/claude-opus-5-5 — 58, $5.98/task, 97 tok/s, 1M, Sept 2026.
- https://artificialanalysis.ai/models/claude-sonnet-5-5 — 56, $5.46/task, 142 tok/s, 1M.
- https://artificialanalysis.ai/models/claude-haiku-5-5 — 43, $0.21/task, 237 tok/s, 1M.
- https://artificialanalysis.ai/models/claude-fable-5-1 — 53, $7.63/task, 70 tok/s, 1M.
- AA effort-variant pages: claude-opus-5-5-low/medium, claude-sonnet-5-5-low/medium/high,
  claude-haiku-5-5-low/medium, claude-fable-5-1-low/medium, grok-4-7-low/high,
  grok-4-6-low/medium/xhigh, gpt-6-1-sol-low/medium, gpt-6-luna-low/non-reasoning,
  glm-5-3-low, kimi-k3-low, deepseek-v4-1-flash-non-reasoning,
  gemini-3-8-flash-low/medium — per-effort AA/speed/cost/verbosity (§1 list).
- https://artificialanalysis.ai/models/grok-4-7 — 46 xhigh, $3.74, 74 tok/s.
- https://artificialanalysis.ai/models/grok-4-6 — 44 high, $1.48, 60 tok/s.
- https://artificialanalysis.ai/models/grok-code-fast-1 — 14, Aug 2025, no price/speed.
- https://artificialanalysis.ai/models/deepseek-v4-1-flash — 39 max, $0.27, 217 tok/s.
- https://artificialanalysis.ai/models/glm-5-3-flash — 42, $0.25, 58 tok/s.
- https://artificialanalysis.ai/models/glm-5-3 — 45 max, $2.01, 83 tok/s.
- https://artificialanalysis.ai/models/kimi-k3 — 44 max, $2.00, 39 tok/s.
- https://artificialanalysis.ai/models/minimax-m3 — 29, $0.51, 101 tok/s.
- https://artificialanalysis.ai/models/qwen3-8-max — 45, $5.41, 36 tok/s.
- https://artificialanalysis.ai/models/gpt-6-1-sol — 52 max, $0.72, 57 tok/s.
- https://artificialanalysis.ai/models/gpt-6-luna — 38 max, $0.07, 137 tok/s.
- https://artificialanalysis.ai/models/gemini-3-8-flash — 41 high, $1.24, 125 tok/s.
- 404s: /models/claude-haiku-4-5, /models/claude-haiku-4-5-20251001,
  /models/claude-mythos-5-1, /models/mythos-5-1, /models/grok-build-0-1,
  /models/grok-4-7-fast.
- Embedded comparison dataset in the above pages (engineering, terminalBench40/21,
  omniscience, omniscienceHallucinationRate maxima quoted in §1).
- https://www.tbench.ai/ — Terminal-Bench 4.0 official board (headless Chromium).
- https://arena.ai/leaderboard/code/webdev — Overall Oct 8 2026, 852,934 votes, 142 models.
- https://arena.ai/leaderboard/text — Overall Oct 8 2026, 8,734,330 votes, 414 models.
- https://www.designarena.ai/leaderboard/code — Overall top-15 + General Purpose board.
- https://www.swebench.com/ — Verified board newest rows Feb 2026 (no 2026-10 candidates).
- https://platform.claude.com/docs/en/models/haiku-5-5/overview — Oct 7 2026 release,
  tiered pricing, 1M ctx, tokenizer note, defaults table (Opus med / Sonnet high /
  Haiku med / Fable high).
- https://platform.claude.com/docs/en/models/mythos-5-1/overview — Fable-equivalent,
  verification-required, Sept 1 2026, $10/$50.
- https://platform.claude.com/docs/en/models/opus-5-5/overview — Sept 22 2026 release.
- https://platform.claude.com/docs/en/models/sonnet-5-5/overview — Sept 28 2026 release.
- https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan —
  same-pool 50% cap (Max/premium) vs credits-only (Pro/standard).
- https://docs.x.ai/developers/pricing — 500K ctx + 2-tier prices (4.6/4.7),
  build-0.1 256K $1/$2, 4.7-Fast Cursor/Build-only 2x.
- https://docs.x.ai/developers/model-capabilities/text/reasoning — low/medium/high/xhigh,
  default high, cannot disable.
- https://docs.x.ai/build/overview — grok-4.7 latest, no subscription catalog.
- https://openrouter.ai/api/v1/models — catalog snapshot (ids, ctx, $/M in §1–2).
- Local: retry-disabled `ok` probes (haiku-5-5, fable-5-1), mythos-5-1 404
  (2026-10-10, this checkout).
