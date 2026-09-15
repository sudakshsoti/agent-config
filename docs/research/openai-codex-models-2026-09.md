# OpenAI Codex models — evidence for routing (read 2026-09-16)

Provider ids in scope: `openai-codex/gpt-5.6-luna`, `openai-codex/gpt-5.6-terra`,
`openai-codex/gpt-5.6-sol`, `openai-codex/gpt-6-astra`, `openai-codex/gpt-5.3-codex-spark`.
All pages below were read on 2026-09-16 unless a different page date is quoted.
Prices are USD per 1M tokens (input / output) unless stated.

## Summary

- GPT-5.6 family tiers (OpenAI's own naming): **Sol = flagship/large** (unsuffixed tier,
  `gpt-5.6` aliases to Sol), **Terra = balanced mid** (~mini tier), **Luna = small/fast**
  (~nano tier). Sources: https://openai.com/index/gpt-5-6/ ,
  https://openai.com/index/previewing-gpt-5-6-sol/ ,
  https://developers.openai.com/api/docs/models/gpt-5.6-sol ,
  https://developers.openai.com/api/docs/models/gpt-5.6-terra ,
  https://developers.openai.com/api/docs/models/gpt-5.6-luna (all read 2026-09-16).
- The user's "~USD 100/month 5x plan" is **ChatGPT Pro $100 (Pro 5x)**: "From $100/month",
  "Choose 5x or 20x higher rate limits than Plus", "5x or 20x more Codex usage than Plus".
  Source: https://learn.chatgpt.com/docs/pricing (read 2026-09-16).
- Codex/Work usage is token-metered (credits per 1M input / cached-input / output tokens),
  shared across Codex + ChatGPT Work (+ Excel where applicable), with 5-hour estimates and
  weekly limits. Source: https://learn.chatgpt.com/docs/pricing ,
  https://help.openai.com/en/articles/11481834-chatgpt-rate-card-business-enterpriseedu-credit-based-pricing (both read 2026-09-16).
- Reasoning-effort support per OpenAI dev docs (read 2026-09-16): Sol/Terra/Luna =
  `none, low, medium (default), high, xhigh, max`; Astra = `low, medium, high, xhigh, max`
  (no `none`). None of them lists `minimal`; OMP's `minimal` is **not** a provider-supported
  value for any of these five. Spark effort values could not be verified.
- Artificial Analysis current version at time of reading is **Intelligence Index v4.3**
  (10 evals incl. Terminal-Bench 4.0). Model-page scores (max effort, v4.3): Astra **53**,
  Sol **47**, Terra **42**, Luna **38**. Sources: https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index ,
  https://artificialanalysis.ai/models/gpt-6-astra , https://artificialanalysis.ai/models/gpt-5-6-sol ,
  https://artificialanalysis.ai/models/gpt-5-6-terra , https://artificialanalysis.ai/models/gpt-5-6-luna (all read 2026-09-16).
- Coding Agent Index numbers come in **two incomparable vintages**: July 2026 article
  (Sol 80 / Terra 77 / Luna 75) vs September 2026 Astra article (Astra 62, Sol 55 on a
  rebased index). Do not compare 80 with 62. Sources:
  https://artificialanalysis.ai/articles/gpt-5-6-has-landed (2026-07-09, read 2026-09-16),
  https://artificialanalysis.ai/articles/benchmarking-gpt-6-astra (2026-09-09, read 2026-09-16).
- GPT-5.3-Codex-Spark is a Pro-only research preview (text-only, 128k context, >1000 tok/s
  on Cerebras, own separate rate limit, no API at launch). No Artificial Analysis page
  (HTTP 404), no llm-stats data (page exists but JS/bot-gated, `noindex`), no arena rows
  observed. Source: https://openai.com/index/introducing-gpt-5-3-codex-spark/ (2026-02-12, read 2026-09-16).
- No OpenAI page found that authorises third-party harnesses (e.g. OMP/Pi `openai-codex`
  provider) to consume a ChatGPT plan via Codex OAuth. The docs name only official clients;
  the Terms prohibit sharing credentials / making accounts available and circumventing
  limits. See Plans section and Gaps.

## Models

### `openai-codex/gpt-5.6-luna` → `gpt-5.6-luna` (small tier)

- Identity/release: GPT-5.6 Luna, "designed for cost-sensitive, high-volume workloads",
  "roughly corresponds to the nano model tier used in earlier GPT-5 families".
  Released 2026-07-09 (GA with Sol/Terra). Sources: https://developers.openai.com/api/docs/models/gpt-5.6-luna ,
  https://llm-stats.com/models/gpt-5.6-luna , https://openai.com/index/gpt-5-6/ (all read 2026-09-16).
- Context window: 1,050,000-token context window; max input 922,000; max output 128,000;
  text+image in, text out; knowledge cutoff 2026-02-16.
  Source: https://developers.openai.com/api/docs/models/gpt-5.6-luna (read 2026-09-16).
- API price per 1M input/output tokens:
  - Launch list price: $1 / $6 (https://openai.com/index/previewing-gpt-5-6-sol/ , read 2026-09-16).
  - Current dev-docs price: **$0.20** in / **$1.20** out; cached input $0.02; cache writes 1.25x;
    >272K-input prompts billed 2x in / 1.5x out.
    Source: https://developers.openai.com/api/docs/models/gpt-5.6-luna (read 2026-09-16).
  - llm-stats.com lists $0.200 in / $0.020 cached / $1.20 out, 1.1M in / 128K out, TTFT p95 4.27s,
    output p5 60 char/s, LLM Stats Score 45.1 (#32 of 369), cost rank #106 ($0.25/1M blended).
    Source: https://llm-stats.com/models/gpt-5.6-luna (read 2026-09-16).
  - Codex credit rates: 5 in / 0.5 cached / 30 out credits per 1M tokens.
    Source: https://help.openai.com/en/articles/11481834-chatgpt-rate-card-business-enterpriseedu-credit-based-pricing (read 2026-09-16).
- Artificial Analysis (v4.3, max effort, read 2026-09-16):
  - Intelligence Index **38** (#4 in its price class on the model page; page header shows max variant).
    Source: https://artificialanalysis.ai/models/gpt-5-6-luna
  - Output speed **116.7 tok/s** (#54 of 176 in class); cost per Index task **$0.18**.
    Source: https://artificialanalysis.ai/models/gpt-5-6-luna
  - Coding Agent Index **75 (max)** — July-2026 vintage only (see note above); per-task cost ~80%
    below Sol. SWE-bench / Terminal-Bench per-model numeric cells were not captured from the
    model page (component charts are JS-rendered); not fabricated.
    Source: https://artificialanalysis.ai/articles/gpt-5-6-has-landed
  - SWE-bench / Terminal-Bench standalone scores on artificialanalysis.ai: **not extracted**
    (could not be verified; see Gaps).
- lmarena.ai (arena.ai, live leaderboard snapshot read 2026-09-16 via page extraction):
  - Text Arena: `gpt-5.6-luna-xhigh` shown at score **1452 ±5**, 28,547 votes
    (displayed rank 50 in snapshot; leaderboard order shifts live).
  - WebDev Arena: `gpt-5.6-luna-xhigh (codex-harness)` rank **37**, score **1519 ±8**, 7,828 votes,
    listed $0.20/$1.20, 1M context. Source: https://arena.ai/leaderboard/code/webdev
- Supported reasoning efforts: `none, low, medium (default), high, xhigh, max`.
  `minimal` is **not** supported. Source: https://developers.openai.com/api/docs/models/gpt-5.6-luna (read 2026-09-16).

### `openai-codex/gpt-5.6-terra` → `gpt-5.6-terra` (mid tier)

- Identity/release: GPT-5.6 Terra, "designed for workloads that balance intelligence and cost",
  "roughly corresponds to the mini model tier used in earlier GPT-5 families".
  Released 2026-07-09. Sources: https://developers.openai.com/api/docs/models/gpt-5.6-terra ,
  https://llm-stats.com/models/gpt-5.6-terra (both read 2026-09-16).
- Context window: 1,050,000-token context window; max input 922,000; max output 128,000;
  text+image in, text out; knowledge cutoff 2026-02-16.
  Source: https://developers.openai.com/api/docs/models/gpt-5.6-terra (read 2026-09-16).
- API price per 1M input/output tokens:
  - Launch list price: $2.50 / $15 (https://openai.com/index/previewing-gpt-5-6-sol/ , read 2026-09-16).
  - Current dev-docs price: **$2** in / **$12** out; cached input $0.2; cache writes 1.25x;
    >272K-input prompts 2x in / 1.5x out.
    Source: https://developers.openai.com/api/docs/models/gpt-5.6-terra (read 2026-09-16).
  - llm-stats.com lists $2.00 in / $0.200 cached / $12.00 out, 1.1M in / 128K out, TTFT p95 7.06s,
    output p5 89 char/s (≈88.8), LLM Stats Score 50.8 (#16 of 369), cost rank #21 ($2.48/1M blended).
    Source: https://llm-stats.com/models/gpt-5.6-terra (read 2026-09-16).
  - Codex credit rates: 50 in / 5 cached / 300 out credits per 1M tokens.
    Source: https://help.openai.com/en/articles/11481834-chatgpt-rate-card-business-enterpriseedu-credit-based-pricing (read 2026-09-16).
- Artificial Analysis (v4.3, max effort, read 2026-09-16):
  - Intelligence Index **42** (#27 of 199 overall on the model page).
    Source: https://artificialanalysis.ai/models/gpt-5-6-terra
  - Output speed **101.2 tok/s** (#49 of 199); cost per Index task **$1.40**.
    Source: https://artificialanalysis.ai/models/gpt-5-6-terra
  - Coding Agent Index **77.4–77 (max)** — July-2026 vintage (Vellum cites 77.4; AA article says 77),
    ~60% per-task cost reduction vs Sol. Per-model SWE-bench / Terminal-Bench cells not captured;
    not fabricated. Sources: https://artificialanalysis.ai/articles/gpt-5-6-has-landed ,
    https://www.vellum.ai/blog/gpt-5-6-sol-terra-luna-explained (both read 2026-09-16).
  - SWE-bench / Terminal-Bench standalone scores on artificialanalysis.ai: **not extracted** (see Gaps).
- lmarena.ai (snapshot read 2026-09-16):
  - Text Arena: `gpt-5.6-terra-xhigh` score **1466 ±5**, 28,119 votes (displayed rank 28 in snapshot).
    Source: https://arena.ai/leaderboard/text
  - WebDev Arena: `gpt-5.6-terra-xhigh (codex-harness)` rank **35**, score **1521 ±8**, 7,694 votes,
    listed $2/$12, 1M context. Source: https://arena.ai/leaderboard/code/webdev
- Supported reasoning efforts: `none, low, medium (default), high, xhigh, max`.
  `minimal` is **not** supported. Source: https://developers.openai.com/api/docs/models/gpt-5.6-terra (read 2026-09-16).

### `openai-codex/gpt-5.6-sol` → `gpt-5.6-sol` (large/flagship tier)

- Identity/release: GPT-5.6 Sol, "flagship model in the GPT-5.6 family", "roughly corresponds
  to the unsuffixed model tier used in earlier GPT-5 families"; `gpt-5.6` alias routes to Sol.
  GA 2026-07-09 after limited preview. Sources: https://developers.openai.com/api/docs/models/gpt-5.6-sol ,
  https://openai.com/index/gpt-5-6/ (both read 2026-09-16).
- Context window: 1,050,000-token context window; max input 922,000; max output 128,000;
  text+image in, text out; knowledge cutoff 2026-02-16.
  Source: https://developers.openai.com/api/docs/models/gpt-5.6-sol (read 2026-09-16).
- API price per 1M input/output tokens:
  - Launch list price: $5 / $30 (https://openai.com/index/previewing-gpt-5-6-sol/ , read 2026-09-16;
    also https://artificialanalysis.ai/articles/gpt-5-6-has-landed ).
  - Current dev-docs price: **$4** in / **$20** out (promo "available at least through 2026-11-21");
    cached input $0.4; cache writes 1.25x; >272K-input prompts 2x in / 1.5x out.
    Source: https://developers.openai.com/api/docs/models/gpt-5.6-sol (read 2026-09-16).
  - llm-stats.com still lists launch pricing: $5.00 in / $0.500 cached / $30.00 out, 1.1M in / 128K out,
    TTFT p95 5.44s, output p5 22 char/s, cost badge $6.19/1M blended. LLM Stats Score page shows
    "Score pending" in the static snapshot for Sol (rank not captured); benchmark participation
    verified: GPQA #2 of 10 (0.95, max effort), HealthBench Consensus #1 of 4 (0.95),
    Connectors #1 of 3 (1.00), Capture-the-Flag (internal) #1 of 3 (0.97); dataset list includes
    Terminal-Bench 2.1/4.0, SWE-Bench Pro, DeepSWE/1.1, SEC-bench Pro, ExploitBench, ExploitGym,
    OSWorld 2.0 — per-benchmark numeric scores for those coding rows were **not** captured
    (expandable JS rows). Source: https://llm-stats.com/models/gpt-5.6-sol (read 2026-09-16).
  - Codex credit rates: 100 in / 10 cached / 500 out credits per 1M tokens.
    Source: https://help.openai.com/en/articles/11481834-chatgpt-rate-card-business-enterpriseedu-credit-based-pricing (read 2026-09-16).
- Artificial Analysis (v4.3, max effort, read 2026-09-16):
  - Intelligence Index **47** (#14 of 199 overall on the model page; the July article reported 59
    on Index v4.1 — version difference, do not mix).
    Source: https://artificialanalysis.ai/models/gpt-5-6-sol
  - Output speed **64.7 tok/s** (#81 of 199); cost per Index task **$1.99**.
    Source: https://artificialanalysis.ai/models/gpt-5-6-sol
  - Coding Agent Index **80 (max)** — July-2026 vintage (led DeepSWE, Terminal-Bench v2,
    SWE-Atlas-QnA in Codex harness at that time). September article rebases Sol (max) to **55**
    on the new scale. SWE-bench / Terminal-Bench standalone per-model scores: **not extracted**.
    Sources: https://artificialanalysis.ai/articles/gpt-5-6-has-landed ,
    https://artificialanalysis.ai/articles/benchmarking-gpt-6-astra
- lmarena.ai (snapshot read 2026-09-16):
  - Text Arena: `gpt-5.6-sol-xhigh` score **1483 ±5**, 27,069 votes, listed $4/$20
    (displayed rank 9 in snapshot; third-party trackers show ~18 as the board moves).
    Source: https://arena.ai/leaderboard/text
  - WebDev Arena: `gpt-5.6-sol-xhigh (codex-harness)` rank **14**, score **1617 ±7**, 11,916 votes,
    listed $4/$20, 1.1M context. Source: https://arena.ai/leaderboard/code/webdev
- Supported reasoning efforts: `none, low, medium (default), high, xhigh, max`.
  `minimal` is **not** supported. Source: https://developers.openai.com/api/docs/models/gpt-5.6-sol (read 2026-09-16).

### `openai-codex/gpt-6-astra` → `gpt-6-astra` (next-gen flagship)

- Identity/release: GPT-6 Astra, "most capable model, built for the hardest end-to-end work";
  model id `gpt-6-astra`. Limited preview 2026-09-03, stable public release 2026-09-04 per
  Wikipedia; OpenAI business post says "introduced last week, now in ChatGPT Work, Codex, API".
  llm-stats lists release 2026-09-04. Sources: https://developers.openai.com/api/docs/models/gpt-6-astra ,
  https://openai.com/index/gpt-6-astra-next-generation-work/ , https://llm-stats.com/models/gpt-6-astra ,
  https://en.wikipedia.org/wiki/GPT-6_Astra (all read 2026-09-16).
- Context window: 1,050,000-token context window; max input 922,000; max output 128,000;
  text+image in, text out; knowledge cutoff 2026-04-30.
  Source: https://developers.openai.com/api/docs/models/gpt-6-astra (read 2026-09-16).
- API price per 1M input/output tokens: **$10** in / **$50** out; cached input $1.00;
  cache writes $12.50 (1.25x); >272K-input prompts 2x in+cache / 1.5x out; Fast mode 2x API rates.
  Sources: https://developers.openai.com/api/docs/models/gpt-6-astra ,
  https://openai.com/index/gpt-6-astra-next-generation-work/ ("starts at $10/$50", read 2026-09-16).
  llm-stats.com concurs ($10.00 / $1.00 / $50.00, 1.1M/128K, TTFT p95 9.70s, output p5 13 char/s,
  LLM Stats Score 59.6, #1 of 369). Source: https://llm-stats.com/models/gpt-6-astra (read 2026-09-16).
  Codex credit rates: 250 in / 25 cached / 1,250 out credits per 1M; Fast mode 2.5x in Codex/Work.
  Sources: https://help.openai.com/en/articles/11481834-chatgpt-rate-card-business-enterpriseedu-credit-based-pricing ,
  https://learn.chatgpt.com/docs/pricing (read 2026-09-16).
- Artificial Analysis (v4.3, max effort, read 2026-09-16):
  - Intelligence Index **53** (#3 of 199), cost per task **$3.26**, output speed **54.0 tok/s** (#111).
    Source: https://artificialanalysis.ai/models/gpt-6-astra
  - Coding Agent Index **62 (max)** in Codex, level with Claude Fable 5.1 (Sept-2026 scale);
    components cited: Terminal-Bench v4.0 56% vs Sol 37%, SWE-Atlas-QnA 62% vs 54%, DeepSWE 68% vs 72%.
    Standalone Terminal-Bench 4.0 board: Astra xhigh **59.6%**, Astra max **59.1%** (top of board).
    Sources: https://artificialanalysis.ai/articles/benchmarking-gpt-6-astra ,
    https://artificialanalysis.ai/evaluations/terminalbench-4-0
  - Other Sept-2026 figures: Intelligence cost frontier $0.82 (low) → $3.26 (max) per task;
    27k output tokens/task at max; AutomationBench-AA 69%; GDP.pdf 31% all-pass.
    Source: https://artificialanalysis.ai/articles/benchmarking-gpt-6-astra
  - SWE-bench standalone score on artificialanalysis.ai: **not extracted** (DeepSWE reported instead).
- lmarena.ai (snapshot read 2026-09-16):
  - Text Arena: `gpt-6-astra-max` score **1480 ±12**, 2,693 votes (displayed rank 5 in snapshot).
    Source: https://arena.ai/leaderboard/text
  - WebDev Arena: `gpt-6-astra-max` rank **1**, score **1800 ±16**, 2,281 votes, listed $10/$50, 1.1M.
    Source: https://arena.ai/leaderboard/code/webdev
- Supported reasoning efforts: `low, medium, high, xhigh, max` (no `none` listed).
  `minimal` is **not** supported. Source: https://developers.openai.com/api/docs/models/gpt-6-astra (read 2026-09-16).

### `openai-codex/gpt-5.3-codex-spark` → `gpt-5.3-codex-spark` (speed tier)

- Identity/release: GPT-5.3-Codex-Spark, "smaller version of GPT-5.3-Codex", "first model
  designed for real-time coding", research preview announced 2026-02-12, Cerebras-powered,
  ">1000 tokens per second", "15x faster generation". Pro-only preview at launch; small set
  of API design partners only. Source: https://openai.com/index/introducing-gpt-5-3-codex-spark/ (read 2026-09-16).
- Context window: **128k**, text-only. Source: https://openai.com/index/introducing-gpt-5-3-codex-spark/ (read 2026-09-16).
- Benchmarks: SWE-Bench Pro and Terminal-Bench 2.0 performance referenced qualitatively
  ("strong performance … in a fraction of the time") — **no numeric scores published** on the page.
  Source: https://openai.com/index/introducing-gpt-5-3-codex-spark/ (read 2026-09-16).
- Artificial Analysis: **not listed** (https://artificialanalysis.ai/models/gpt-5-3-codex-spark → HTTP 404,
  read 2026-09-16). No Intelligence Index, Coding Index, SWE-bench, Terminal-Bench, speed, or price.
- llm-stats.com: page https://llm-stats.com/models/gpt-5.3-codex-spark exists but is bot/JS-gated
  (`noindex`, human-verification wall on fetch, read 2026-09-16) — scores and price **not listed**
  (could not be verified; see Gaps).
- lmarena.ai text and WebDev arenas: **not listed** (no `codex-spark` rows in either extracted
  leaderboard snapshot, read 2026-09-16). Sources: https://arena.ai/leaderboard/text ,
  https://arena.ai/leaderboard/code/webdev
- API price per 1M input/output: **not published** (not available through API keys at launch;
  research preview). Source: https://openai.com/index/introducing-gpt-5-3-codex-spark/ (read 2026-09-16).
- Codex credit rates: row shows "research preview" with **no numeric credit rates**; usage governed
  by a **separate usage limit** outside standard limits.
  Sources: https://learn.chatgpt.com/docs/pricing , https://help.openai.com/en/articles/11481834-chatgpt-rate-card-business-enterpriseedu-credit-based-pricing (read 2026-09-16).
- Supported reasoning efforts: **could not be verified** (no `reasoning.effort` statement found;
  dev-docs model page https://developers.openai.com/api/docs/models/gpt-5.3-codex-spark → HTTP 404,
  read 2026-09-16). OMP's `minimal|low|medium|high|xhigh` support for Spark is therefore **unknown**.

## Plans and limits

Plan identification (all read 2026-09-16):

- The "~USD 100/month 5x plan" is **ChatGPT Pro $100**, i.e. **Pro 5x**: "From $100/month",
  "Choose 5x or 20x higher rate limits than Plus", "5x or 20x more Codex usage than Plus",
  includes GPT-5.3-Codex-Spark (research preview).
  Source: https://learn.chatgpt.com/docs/pricing
- Neighbours: Plus **$20/month** ("a few focused coding sessions each week"); Pro 20x **$200/month**;
  Go $8/month; Free $0. Pro split into 5x/20x on 2026-04-09; as of **2026-09-10 new Pro $200 (20x)
  sign-ups/upgrades are temporarily paused** (existing Pro $200 unaffected).
  Sources: https://learn.chatgpt.com/docs/pricing ,
  https://help.openai.com/en/articles/9793128-about-chatgpt-pro-plans ,
  https://www.cloudzero.com/blog/openai-codex-pricing/ (third-party explainer, updated 2026-09-04)

What counts against the limit:

- Token-metered credits: input, cached input (~10% of input), and output tokens per model.
  Credit rates (credits/1M): Astra 250/25/1250; Sol 100/10/500; Terra 50/5/300; Luna 5/0.5/30;
  Spark: "research preview" (no numeric rate). Typical GPT-5.6 task: 5–30 credits/message.
  Sources: https://learn.chatgpt.com/docs/pricing , https://help.openai.com/en/articles/11481834-chatgpt-rate-card-business-enterpriseedu-credit-based-pricing
- Shared pool: Codex + ChatGPT Work (+ ChatGPT for Excel, Voice-in-desktop tasks) draw from the
  **same agentic usage/credit pool**; local messages and cloud chats share the allowance.
  Sources: https://learn.chatgpt.com/docs/pricing , https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan
- Multipliers: Fast mode costs extra (Astra 2.5x in Codex/Work per pricing page; API Fast mode 2x;
  third-party trackers cite 2.5x/2x for older models — OpenAI page governs). Image generation
  burns limits ~3–5x faster. Sources: https://learn.chatgpt.com/docs/pricing ,
  https://developers.openai.com/api/docs/models/gpt-6-astra

Reset windows:

- **5-hour window**: published estimates are "local messages per five-hour period" (Plus baseline):
  Astra 5–45; Sol 10–100; Terra 25–200; Luna 250–2,000 (GPT-5.5 15–80; GPT-5.4 20–100;
  GPT-5.4 mini 60–350 for reference). Pro 5x multiplies by 5 (e.g. Sol 50–500, Luna 1,250–10,000);
  Pro 20x by 20. Cloud chats use Sol and "may use more of your allowance than local messages".
  Estimates "are not fixed message limits". Source: https://learn.chatgpt.com/docs/pricing
- **Weekly limits**: "Local messages and cloud chats share your plan's usage allowance. Weekly
  limits may also apply." Dashboard (`/status` in CLI) shows current limits/reset times.
  Source: https://learn.chatgpt.com/docs/pricing
- Banked rate-limit resets (referral promo) refresh 5-hour **and** weekly windows when redeemed.
  Source: https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan

Per-model / per-effort differences:

- Model tier changes consumption ~20x end-to-end: Sol 100/500 vs Luna 5/30 credits per 1M in/out
  (20x in, ~16.7x out); Astra 250/1250 is 2.5x Sol. Legacy per-message averages (Enterprise legacy
  card): local task ≈ 16 Astra / 11 Sol / 6 Terra / 1 Luna credits.
  Source: https://help.openai.com/en/articles/11481834-chatgpt-rate-card-business-enterpriseedu-credit-based-pricing
- Reasoning effort: for **Chat** (fixed per-message billing), "selecting a higher reasoning effort
  does not increase the per-message credit rate" (Medium/High/Extra High all 10 credits on Sol).
  For **Codex/Work** (token-metered), effort is not a separate row — "Ultra uses maximum reasoning
  and may run additional agents … credit usage still depends on the model used and the tokens
  produced". So higher effort costs more **through tokens**, not through a rate change.
  Source: https://help.openai.com/en/articles/11481834-chatgpt-rate-card-business-enterpriseedu-credit-based-pricing
- Spark: separate usage limit, Pro-only, may queue under load; usage did not count toward standard
  limits during preview. Source: https://openai.com/index/introducing-gpt-5-3-codex-spark/

Shared with ChatGPT / overage / fallback:

- Codex rides on the ChatGPT subscription (no standalone Codex sub); included plan usage is
  consumed first, then purchased **credits** (pay-as-you-go add-on, no plan change). Credits valid
  12 months, non-refundable, non-transferable; auto-reload optional; balance can go negative
  mid-turn (later purchases offset it first). If a limit hits mid-turn, the agent finishes that
  turn under fair use, then stops. Alternative fallbacks: switch to a smaller model (Terra/Luna),
  apply a banked reset, upgrade, wait, or run extra local chats on an API key at standard API rates
  (no cloud features on API-key auth). Support does **not** reset limits.
  Sources: https://help.openai.com/en/articles/12642688-using-credits-for-flexible-usage-in-chatgpt-freegopluspro-sora ,
  https://learn.chatgpt.com/docs/pricing , https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan
- "Local messages per 5 hours" per tier: table above (Plus → ×5 Pro 5x → ×20 Pro 20x). No separate
  published weekly numeric cap was found on the official pages (weekly limit existence is stated,
  its number is not).

Third-party harness (Codex OAuth) coverage:

- OpenAI's auth docs describe **two** sign-in methods for the **official** surfaces only
  (ChatGPT desktop app, Codex CLI, IDE extension, Codex cloud/web): "Sign in with ChatGPT for
  subscription access" or "Sign in with an API key for usage-based access". No page found that
  permits or describes third-party harnesses (OMP/Pi `openai-codex` provider) consuming plan
  entitlements via the ChatGPT login. Source: https://learn.chatgpt.com/docs/auth (redirect of
  developers.openai.com/codex/auth, read 2026-09-16).
- Conversely, the Terms of Use prohibit: sharing account credentials "or mak[ing] your account
  available to anyone else"; "automatically or programmatically extract[ing] data"; "interfer[ing]
  with or disrupt[ing] our Services, including circumvent[ing] any rate limits or restrictions or
  bypass[ing] any protective measures"; "reselling access or using ChatGPT to power third-party
  services" (latter quoted in https://help.openai.com/en/articles/9793128-about-chatgpt-pro-plans ).
  The account-sharing policy states accounts are for the individual who created them.
  Sources: https://openai.com/policies/row-terms-of-use/ ,
  https://help.openai.com/en/articles/10471989-openai-account-sharing-policy (read 2026-09-16).
- Net: **could not verify any plan coverage for third-party-harness OAuth usage**; the written
  terms point the other way, but no page explicitly names OMP/Pi-style providers. Routing plan
  usage through anything but OpenAI's own clients should be treated as unconfirmed/against-terms
  until OpenAI states otherwise. See Gaps.

## Gaps

- llm-stats.com per-benchmark **numeric coding scores** (SWE-Bench Pro, Terminal-Bench, DeepSWE,
  SEC-bench) for Sol/Terra/Luna/Astra: observed the dataset names in Sol's "Performance Across
  Datasets" list, but score cells sit behind JS-expanded rows that the static fetch did not render;
  only GPQA (#2, 0.95), HealthBench Consensus (#1, 0.95), Connectors (#1, 1.00), CTF-internal
  (#1, 0.97) ranks/scores were captured for Sol. Terra/Luna/Astra benchmark tables were not
  expanded (navigation timeout on the batch pass). LLM Stats Score / price / latency figures above
  are verified; row-level coding scores are not. Source pages: https://llm-stats.com/models/gpt-5.6-sol ,
  https://llm-stats.com/models/gpt-5.6-terra , https://llm-stats.com/models/gpt-5.6-luna ,
  https://llm-stats.com/models/gpt-6-astra (read 2026-09-16).
- llm-stats.com GPT-5.3-Codex-Spark page: exists but returned a bot-verification wall with
  `noindex` meta on fetch — no scores, price, or context could be verified there.
  Source: https://llm-stats.com/models/gpt-5.3-codex-spark (read 2026-09-16).
- Artificial Analysis per-model SWE-bench / Terminal-Bench standalone scores for Sol, Terra, Luna:
  model pages render component-evaluation charts via JS; the static fetch captured only the
  Intelligence Index score, speed, cost/task, and class ranks. Coding figures cited come from AA's
  two articles (different index vintages — flagged inline). Could not verify a single-vintage
  per-model SWE-bench column. Sources: https://artificialanalysis.ai/models/gpt-5-6-sol ,
  https://artificialanalysis.ai/models/gpt-5-6-terra , https://artificialanalysis.ai/models/gpt-5-6-luna (read 2026-09-16).
- lmarena.ai ranks are live-snapshot values (arena.ai pages are JS-rendered; text/WebDev rows
  extracted via headless-page text on 2026-09-16). Ranks move; scores/votes quoted alongside so the
  claim stays checkable. Legacy lmarena-ai HuggingFace Space exposes only metadata via static fetch
  (leaderboard table itself not retrievable). Sources: https://arena.ai/leaderboard/text ,
  https://arena.ai/leaderboard/code/webdev , https://huggingface.co/spaces/lmarena-ai/arena-leaderboard (read 2026-09-16).
- Spark reasoning-effort values and any API/credit price: no statement found (dev-docs model page
  404s; announcement silent on effort values). OMP effort support for Spark is unknown.
- Numeric weekly cap for Pro 5x and any per-model weekly split: existence stated, number not
  published on the official pages checked. Third-party trackers (CloudZero, Halv, TraceCheck)
  describe 5-hour/weekly mechanics but are not primary sources and were not used for numbers.
- Explicit OpenAI statement on third-party-harness plan usage (allow/deny for `openai-codex`-style
  providers): not found. The "Using Codex with your ChatGPT plan" and auth docs enumerate only
  official clients; relevant prohibitions are quoted above but do not name harnesses.

## Sources

- https://openai.com/index/gpt-5-6/ — GPT-5.6 GA post (2026-07-09; updates 2026-07-30 price cuts, 2026-08-21 Sol promo). Read 2026-09-16.
- https://openai.com/index/previewing-gpt-5-6-sol/ — GPT-5.6 preview, tier positioning, launch prices ($5/$30, $2.50/$15, $1/$6), cache terms. Read 2026-09-16.
- https://developers.openai.com/api/docs/models/gpt-5.6-sol — Sol tier (~unsuffixed), efforts, 1.05M context, promo $4/$20 pricing. Read 2026-09-16.
- https://developers.openai.com/api/docs/models/gpt-5.6-terra — Terra tier (~mini), efforts, 1.05M context, $2/$12 pricing. Read 2026-09-16.
- https://developers.openai.com/api/docs/models/gpt-5.6-luna — Luna tier (~nano), efforts, 1.05M context, $0.20/$1.20 pricing. Read 2026-09-16.
- https://developers.openai.com/api/docs/models/gpt-6-astra — Astra id, efforts (low–max), 1.05M context, $10/$50 pricing, cutoff 2026-04-30. Read 2026-09-16.
- https://openai.com/index/gpt-6-astra-next-generation-work/ — Astra launch, Codex availability, $10/$50 start. Read 2026-09-16.
- https://openai.com/index/introducing-gpt-5-3-codex-spark/ — Spark preview (2026-02-12): 128k, text-only, >1000 tok/s, separate limits, no API at launch. Read 2026-09-16.
- https://developers.openai.com/api/docs/models/gpt-5.3-codex-spark — HTTP 404 (no dev-docs page). Read 2026-09-16.
- https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index — Index v4.3 definition (10 evals). Read 2026-09-16.
- https://artificialanalysis.ai/models/gpt-5-6-sol — Sol (max) v4.3: 47, 64.7 tok/s, $1.99/task. Read 2026-09-16.
- https://artificialanalysis.ai/models/gpt-5-6-terra — Terra (max) v4.3: 42, 101.2 tok/s, $1.40/task. Read 2026-09-16.
- https://artificialanalysis.ai/models/gpt-5-6-luna — Luna (max) v4.3: 38, 116.7 tok/s, $0.18/task. Read 2026-09-16.
- https://artificialanalysis.ai/models/gpt-6-astra — Astra (max) v4.3: 53, 54.0 tok/s, $3.26/task. Read 2026-09-16.
- https://artificialanalysis.ai/models/gpt-5-3-codex-spark — HTTP 404 (not listed). Read 2026-09-16.
- https://artificialanalysis.ai/articles/gpt-5-6-has-landed (2026-07-09) — July-vintage Coding Index (Sol 80, Terra 77, Luna 75), launch prices. Read 2026-09-16.
- https://artificialanalysis.ai/articles/benchmarking-gpt-6-astra (2026-09-09) — Sept-vintage Coding Index (Astra 62, Sol 55), TB 4.0 / AutomationBench / GDP.pdf figures. Read 2026-09-16.
- https://artificialanalysis.ai/evaluations/terminalbench-4-0 — TB 4.0 board (Astra xhigh 59.6%, max 59.1%). Read 2026-09-16.
- https://llm-stats.com/models/gpt-5.6-sol — Sol price/context/latency + benchmark participation. Read 2026-09-16.
- https://llm-stats.com/models/gpt-5.6-terra — Terra Score 50.8 (#16/369), price, latency. Read 2026-09-16.
- https://llm-stats.com/models/gpt-5.6-luna — Luna Score 45.1 (#32/369), price, latency. Read 2026-09-16.
- https://llm-stats.com/models/gpt-6-astra — Astra Score 59.6 (#1/369), price, latency. Read 2026-09-16.
- https://llm-stats.com/models/gpt-5.3-codex-spark — exists, bot-gated/`noindex`, no data captured. Read 2026-09-16.
- https://arena.ai/leaderboard/text — Text Arena snapshot (Sol-xhigh 1483, Terra-xhigh 1466, Luna-xhigh 1452, Astra-max 1480). Read 2026-09-16.
- https://arena.ai/leaderboard/code/webdev — WebDev snapshot (Astra-max #1 1800; Sol-xhigh #14 1617; Terra-xhigh #35 1521; Luna-xhigh #37 1519). Read 2026-09-16.
- https://huggingface.co/spaces/lmarena-ai/arena-leaderboard — Space metadata only (table not statically retrievable). Read 2026-09-16.
- https://learn.chatgpt.com/docs/pricing — Codex pricing/plan cards, 5-hour estimates table, credit rates, overage, Spark separate limit. Read 2026-09-16.
- https://help.openai.com/en/articles/11481834-chatgpt-rate-card-business-enterpriseedu-credit-based-pricing — token credit rates, effort/Ultra notes, legacy per-message averages. Read 2026-09-16.
- https://help.openai.com/en/articles/12642688-using-credits-for-flexible-usage-in-chatgpt-freegopluspro-sora — credits mechanics (12-mo expiry, auto-reload, negative balances). Read 2026-09-16.
- https://help.openai.com/en/articles/9793128-about-chatgpt-pro-plans — Pro 5x vs 20x, Pro $200 pause (2026-09-10), no-credential-sharing clause. Read 2026-09-16.
- https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan — official clients, shared allowance, banked resets, no Support resets. Read 2026-09-16.
- https://learn.chatgpt.com/docs/auth (via developers.openai.com/codex/auth) — two sign-in methods, official surfaces only. Read 2026-09-16.
- https://openai.com/policies/row-terms-of-use/ (effective 2026-01-01) — credential sharing, extraction, circumvention prohibitions. Read 2026-09-16.
- https://help.openai.com/en/articles/10471989-openai-account-sharing-policy — individual-use accounts. Read 2026-09-16.
- https://www.cloudzero.com/blog/openai-codex-pricing/ (updated 2026-09-04) — third-party explainer only; used for plan-history context (Pro split 2026-04-09), not for numbers. Read 2026-09-16.
- https://en.wikipedia.org/wiki/GPT-6_Astra — Astra release dates (2026-09-03 preview / 2026-09-04 stable); secondary source, dates cross-checked with OpenAI/llm-stats. Read 2026-09-16.
