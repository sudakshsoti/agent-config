# OpenCode Go — models, limits, and routing evidence (2026-09-16)

All pages read 2026-09-16 unless noted. Every number below carries its source URL.
"Not listed" means the model was absent from that site's page/list on that date, not that it scores zero.

## Summary

- OpenCode Go is a **$10/month** subscription for curated open coding models; limits are **monthly dollar amounts per model**, with **5-hour = 20%**, **weekly = 50%**, **monthly = 100%** of that amount. Source: https://opencode.ai/docs/go (read 2026-09-16).
- Per-model monthly caps for the five routed models: GLM-5.3-Flash **$60**, DeepSeek V4.1 Flash **$60** (temporary 4x promo, was $15, ends Sep 20), DeepSeek V4 Flash **$30**, Kimi K3 **$15**, Muse Spark 1.3 Contributor **$60**. Source: usage-limits table on https://opencode.ai/docs/go.
- At the limit, requests block unless the **"Use balance"** Zen-credit fallback is enabled; free models keep working. Source: https://opencode.ai/docs/go ("Usage beyond limits", "If you reach the usage limit, you can continue using the free models.").
- Artificial Analysis Intelligence Index **v4.3** (read 2026-09-16): Kimi K3 (max) **44**, GLM-5.3-Flash **42**, DeepSeek V4.1 Flash (max) **40**, DeepSeek V4 Flash 0731 (max) **35**, Muse Spark 1.3 (max) **48**. AA output speed: Muse 220.8, V4 Flash 214.9, V4.1 Flash 212.1, GLM Flash 114.4, Kimi K3 34.8 tok/s.
- AA publishes no per-model "Coding Index" value on the model pages read; that column is recorded as not listed (see Gaps).
- Vendor reasoning-effort support (primary docs): GLM-5.3-Flash accepts only **low/high/max** (thinking forced on); DeepSeek V4.x accepts **low/high/max** (default high) with OMP-style mapping minimal/low→low, medium/high/xhigh→high, max/ultra→max; Kimi K3 accepts **low/high/max** (default max), always-on thinking; Muse Spark accepts **minimal/low/medium/high/xhigh** (`none` → HTTP 400).
- Repo-note check: the claim "DeepSeek V4.1 Flash only high/max" is **not** what vendor docs say — vendor accepts `low` too (mapped to actual low effort). The "GLM 5.3 Flash only low/high/max" claim is **confirmed** by vendor docs.
- Muse Spark `contributor` variant terms: ~12.5x discounted pricing ($0.10/$0.20 per 1M in/out vs $1.25/$4.25 standard) **in exchange for permission to use prompts/completions to train future Meta models**; limited to regions in Meta's Geographic Use Policy; Go privacy table marks it Training: Yes, retention: Not ZDR. Sources: https://dev.meta.ai/docs/pricing-rate-limits, https://opencode.ai/docs/go (Privacy).
- Go serves GLM/DeepSeek/Kimi over `/v1/chat/completions` and Muse Spark over `/v1/responses`; OMP config form is `opencode-go/<model-id>`. Source: https://opencode.ai/docs/go (Endpoints).
- DeepSeek has **retired** `deepseek-v4-flash`/`deepseek-v4-flash-vision-exp` server-side: those names are still accepted but served by V4.1 Flash and billed at Flash price. Source: https://api-docs.deepseek.com/quick_start/pricing/.

## Models

### opencode-go/muse-spark-1.3-contributor

- Identity/release: Meta Muse Spark 1.3, released **September 2, 2026** (https://openrouter.ai/meta/muse-spark-1.3-contributor, https://llm-stats.com/models/muse-spark-1.3, https://artificialanalysis.ai/models/muse-spark-1-3/ — all read 2026-09-16). Proprietary multimodal reasoning model; contributor tier is the training-eligible discounted variant (https://dev.meta.ai/docs/pricing-rate-limits).
- Context window: **1M tokens** input (https://artificialanalysis.ai/models/muse-spark-1-3/, https://llm-stats.com/models/muse-spark-1.3 — 1.0M in / ~944K out).
- Artificial Analysis: Intelligence Index v4.3 = **48** (ranked #13/199 in its class display; page title "Muse Spark 1.3 (max)"), output speed **220.8 tok/s** (#9), AA list price $1.25 in / $4.25 out per 1M (standard tier; contributor $0.10/$0.20). Coding Index: **not listed** (no Coding Index value on the model page). Source: https://artificialanalysis.ai/models/muse-spark-1-3/.
- Vendor API list price per 1M: contributor tier **$0.10 input / $0.20 output / $0.002 cached input**; standard tier $1.25/$4.25/$0.15. Source: https://dev.meta.ai/docs/pricing-rate-limits. Go's own metered rates match contributor exactly ($0.10/$0.20/$0.002, $60/mo cap). Source: https://opencode.ai/docs/go.
- llm-stats.com: release Sep 2, 2026; $0.10 in / $0.002 cached / $0.20 out via Meta Model API; 1.0M context; TTFT p95 6.01s. Benchmark scores: **not listed** (page shows "Score pending"; no dataset scores rendered). Source: https://llm-stats.com/models/muse-spark-1.3.
- lmarena.ai: text leaderboard `muse-spark-1.3-max` **rank 8, rating 1493.1** (rank range 1–24); WebDev-category snapshot `muse-spark-1.3-max` **rank 8, rating 1651.9**, `muse-spark-1.3 (xHigh)` rank 12, 1623.1. Source: https://lmarena.ai/leaderboard (snapshot embedded in page, read 2026-09-16).
- Supported reasoning efforts: **minimal, low, medium, high, xhigh**; `none` returns HTTP 400 on Muse Spark; omitted parameter reasons at a model-determined level. Chat Completions uses top-level `reasoning_effort`; Responses API nests it as `reasoning.effort`. Reasoning tokens bill as output tokens. Source: https://ai.developer.meta.com/docs/features/reasoning. OMP `minimal|low|medium|high|xhigh` therefore all map to real levels.
- Go endpoint: `muse-spark-1.3-contributor` → `https://opencode.ai/zen/go/v1/responses` (`@ai-sdk/openai`). Source: https://opencode.ai/docs/go.

### opencode-go/glm-5.3-flash

- Identity/release: Z AI (Zhipu) GLM-5.3-Flash, launched **August 26, 2026** (https://www.eigent.ai/blog/glm-5-3-flash-multimodal-model — "Z.ai launched GLM-5.3-Flash on August 26, 2026"; AA page says "Released August 2026": https://artificialanalysis.ai/models/glm-5-3-flash/). 320B total / 18B active MoE, MIT license, open weights (https://artificialanalysis.ai/models/glm-5-3-flash/).
- Context window: **1M tokens** (https://artificialanalysis.ai/models/glm-5-3-flash/, https://developers.cloudflare.com/workers-ai/models/glm-5.3-flash/).
- Artificial Analysis: Intelligence Index v4.3 = **42** (#3/113 in class), output speed **114.4 tok/s** (#13), AA price $0.15 in / $0.50 out per 1M, 83% cache discount. Coding Index: **not listed**. Source: https://artificialanalysis.ai/models/glm-5-3-flash/.
- Vendor API list price per 1M (proxy; Z.ai direct pricing page not fetched): **$0.15 input / $0.50 output / $0.03 cached** per Cloudflare Workers AI (https://developers.cloudflare.com/workers-ai/models/glm-5.3-flash/). Identical to Go's metered rates ($0.15/$0.50/$0.03, $60/mo cap): https://opencode.ai/docs/go.
- llm-stats.com: **page blocked by human-verification wall on 2026-09-16** — no scores or prices verifiable there. Search-engine meta text only ("Compare GLM 5 3 Flash pricing, context limits, latency and benchmark results"). Recorded as not verified, not as zero.
- lmarena.ai: text leaderboard `glm-5.3-flash` **rank 29, rating 1475.4** (range 14–49); WebDev-category `glm-5.3-flash` **rank 17, rating 1607.1**. Source: https://lmarena.ai/leaderboard (read 2026-09-16).
- Supported reasoning efforts: vendor API accepts **only `low`, `high`, `max`** — "For GLM-5.3 and GLM-5.3-FLASH, only `max`, `high` and `low` are supported. Any other input will result in an error." Thinking cannot be disabled (forced thinking; `thinking.type: disabled` errors). Coding-Plan mapping: none/minimal/low→low, medium/high→high, xhigh/max→max. Source: https://docs.z.ai/guides/capabilities/thinking (read 2026-09-16). Confirms the repo note; OMP `minimal`/`medium`/`xhigh` have no distinct vendor level.
- Go endpoint: `glm-5.3-flash` → `https://opencode.ai/zen/go/v1/chat/completions` (`@ai-sdk/openai-compatible`). Source: https://opencode.ai/docs/go.

### opencode-go/deepseek-v4.1-flash

- Identity/release: DeepSeek V4.1 Flash, released **September 10, 2026** (https://api-docs.deepseek.com/updates/ — "Date: 2026-09-10 … DeepSeek-V4.1-Flash Release"; https://llm-stats.com/models/deepseek-v4.1-flash). 552B MoE (+196B Engram memory params per llm-stats), MIT license, native vision, 1M context (https://llm-stats.com/models/deepseek-v4.1-flash).
- Context window: **1M** input, 384K max output (https://api-docs.deepseek.com/quick_start/pricing/).
- Artificial Analysis: Intelligence Index v4.3 = **40** (#6/113, "Reasoning, Max Effort"), output speed **212.1 tok/s** (#4), AA price $0.30 in / $1.20 out per 1M (peak), 98% cache discount. Coding Index: **not listed**. Source: https://artificialanalysis.ai/models/deepseek-v4-1-flash/.
- Vendor API list price per 1M (official): cache-miss input **$0.30 peak / $0.15 off-peak**; cache-hit **$0.006 / $0.003**; output **$1.20 / $0.60**. Peak = 01:00–04:00 and 06:00–10:00 UTC Mon–Fri; off-peak = all else. Source: https://api-docs.deepseek.com/quick_start/pricing/. Go meters the same peak/off-peak pairs ($0.30/$1.20 peak, $0.15/$0.60 off-peak) with a $60/mo cap under a "4x · Ends Sep 20" promo (was $15). Source: https://opencode.ai/docs/go.
- llm-stats.com: release Sep 10, 2026; cheapest tracked provider Fireworks $0.22 in / $0.007 cached / $0.66 out; 1.0M context; MIT. Benchmark scores: **not listed** ("Score pending" across neighbours; no dataset scores rendered). Source: https://llm-stats.com/models/deepseek-v4.1-flash.
- lmarena.ai: text leaderboard — **not listed** (no text-overall entry; only `deepseek-v4.1-flash-max` in the WebDev-category snapshot: **rank 16, rating 1614.0**). Source: https://lmarena.ai/leaderboard (read 2026-09-16).
- Supported reasoning efforts: vendor `reasoning_effort` accepts **low, high, max**; thinking on by default at **high**. Requested→actual mapping: minimal→low, low→low, medium→high, high→high, xhigh→high, max→max, ultra→max. Anthropic-format maps to `reasoning.effort: none/low/high/max`. Source: https://api-docs.deepseek.com/guides/thinking_mode (read 2026-09-16). Correction to the repo note: `low` is a real accepted level, not only high/max.
- Go endpoint: `deepseek-v4.1-flash` → `https://opencode.ai/zen/go/v1/chat/completions`. Source: https://opencode.ai/docs/go.

### opencode-go/deepseek-v4-flash

- Identity/release: DeepSeek V4 Flash (0731), GA **July 31, 2026** (AA page "Released July 2026": https://artificialanalysis.ai/models/deepseek-v4-flash/; GA date Jul 31 per https://www.morphllm.com/deepseek-v4). 284B MoE, MIT. **Retired server-side**: DeepSeek's pricing page states legacy `deepseek-v4-flash` / `deepseek-v4-flash-vision-exp` names are still accepted but "the corresponding models have been retired, their requests are served by the DeepSeek-V4.1-Flash model and billed at the Flash price" (https://api-docs.deepseek.com/quick_start/pricing/).
- Context window: **1M** (https://artificialanalysis.ai/models/deepseek-v4-flash/).
- Artificial Analysis ("DeepSeek V4 Flash 0731, Reasoning, Max Effort"): Intelligence Index v4.3 = **35** (#8/113), output speed **214.9 tok/s** (#3), AA price $0.44 in / $1.32 out per 1M. Coding Index: **not listed**. Source: https://artificialanalysis.ai/models/deepseek-v4-flash/.
- Vendor API list price per 1M: **no longer listed separately** — retired; current official Flash price (V4.1 Flash, which now serves these requests) is $0.30/$1.20 peak, $0.15/$0.60 off-peak (https://api-docs.deepseek.com/quick_start/pricing/). Go meters V4 Flash at off-peak $0.15/$0.60/$0.003 and peak $0.30/$1.20/$0.006 with a **$30/mo** cap (no 4x promo). Source: https://opencode.ai/docs/go.
- llm-stats.com: **page content blocked (generic leaderboard shell, no model meta) on 2026-09-16** — recorded as not verified.
- lmarena.ai: text leaderboard `deepseek-v4-flash` **rank 92, rating 1435.6** (range 79–108); `deepseek-v4-flash-high-preview` rank 87, 1437.9; WebDev-category `deepseek-v4-flash-high` rank 22, 1580.2. Source: https://lmarena.ai/leaderboard (read 2026-09-16).
- Supported reasoning efforts: same V4-family thinking-mode API — **low/high/max** with the minimal→low … xhigh→high mapping (https://api-docs.deepseek.com/guides/thinking_mode). OMP `medium` runs as high per the mapping table.
- Go endpoint: `deepseek-v4-flash` → `https://opencode.ai/zen/go/v1/chat/completions`. Source: https://opencode.ai/docs/go.

### opencode-go/kimi-k3

- Identity/release: Moonshot AI Kimi K3, hosted service live **July 16, 2026** (https://llm-stats.com/models/kimi-k3; https://www.verdent.ai/guides/agents/kimi-k3-api-guide). 2.8T total params (AA: https://artificialanalysis.ai/models/kimi-k3/); Kimi K3 license (open-weights with $20M MaaS clause per llm-stats); always-on reasoning.
- Context window: **1M tokens** in and out (https://llm-stats.com/models/kimi-k3; https://artificialanalysis.ai/models/kimi-k3/).
- Artificial Analysis ("Kimi K3 (max)"): Intelligence Index v4.3 = **44** (#2/113), output speed **34.8 tok/s** (#58 — notably slow), AA price $3.00 in / $15.00 out per 1M, 90% cache discount. Coding Index: **not listed**. Source: https://artificialanalysis.ai/models/kimi-k3/.
- Vendor API list price per 1M: **$3.00 cache-miss input / $0.30 cache-hit / $15.00 output** (https://llm-stats.com/models/kimi-k3 — Moonshot AI row; also https://benchlm.ai/moonshot/api-pricing). Matches Go's metered rates exactly ($3.00/$15.00/$0.30, **$15/mo** cap — the lowest cap of the five). Source: https://opencode.ai/docs/go.
- llm-stats.com: release Jul 16, 2026; input text/image/video, output text; context 1.0M/1.0M; cheapest provider DeepInfra $2.85/$0.285/$14.25. Benchmark scores: **not listed** ("Score pending"). Source: https://llm-stats.com/models/kimi-k3.
- lmarena.ai: text leaderboard `kimi-k3-max` **rank 17, rating 1484.8** (range 7–30); image-to-WebDev `kimi-k3-max` rank 12, 1578.9; no plain-WebDev entry (not listed there). Source: https://lmarena.ai/leaderboard (read 2026-09-16).
- Supported reasoning efforts: **low, high, max (default max)** via top-level `reasoning_effort`; thinking always on. Source: https://platform.kimi.ai/docs/guide/kimi-k3-quickstart (read 2026-09-16 via fetch: "Reasoning effort supports low, high, and max (default max)"). Consistent with the repo note (only low/high/max distinct).
- Go endpoint: `kimi-k3` → `https://opencode.ai/zen/go/v1/chat/completions`. Source: https://opencode.ai/docs/go.

## Plans and limits

- Price: **$10/month**. Verbatim: "OpenCode Go is a low cost **$10/month subscription** that gives you reliable access to popular open coding models." One workspace member subscribes; key is pasted via `/connect` → `OpenCode Go`. Source: https://opencode.ai/docs/go.
- What counts: **monthly dollar amounts** of token usage. "Usage limits are defined as monthly dollar amounts." Token prices are per 1M tokens; Go meters input, output, cached read, and (some models) cached write. Source: https://opencode.ai/docs/go.
- Reset windows (verbatim): "Each model has the following usage limits: 5-hour — 20% of the monthly limit; weekly — 50%; and monthly — 100%. For example, if a model has a $60 monthly limit, you can spend up to: **5-hour limit** — $12 of usage; **Weekly limit** — $30 of usage; **Monthly limit** — $60 of usage." Source: https://opencode.ai/docs/go.
- Per-model differences (monthly cap → 5h/weekly derived; estimated requests/month from Go's table): GLM-5.3-Flash $60 → $12/$30, ~31,580 req/mo; DeepSeek V4.1 Flash **$60** (struck-through $15, "4x · Ends Sep 20") → ~130,000 req/mo; DeepSeek V4 Flash $30 → ~65,000 req/mo; Kimi K3 $15 → ~490 req/mo; Muse Spark 1.3 Contributor $60 → ~226,600 req/mo. Token basis per request is published per model (e.g. Muse 620 in / 71,400 cached / 300 out). Peak/off-peak split applies to all DeepSeek V4 rows (peak 01:00–04:00 and 06:00–10:00 UTC Mon–Fri). Source: https://opencode.ai/docs/go.
- At the limit / overage (verbatim): "If you reach the usage limit, you can continue using the free models." "If you also have credits on your Zen balance, you can enable the **Use balance** option in the console. When enabled, Go will fall back to your Zen balance after you've reached your usage limits instead of blocking requests." Usage is tracked in the console. No per-request overage fee inside Go itself is described. Source: https://opencode.ai/docs/go.
- Reasoning-effort effect on consumption: **not stated** in the Go docs — usage is purely tokens × the table rate (reasoning tokens bill as output at the vendor level per Meta/DeepSeek/Kimi docs). No per-model weighting/multiplier beyond the token prices is documented. "Why some models have lower usage" explains caps via bulk discounts/reserved capacity, not multipliers. Source: https://opencode.ai/docs/go.
- Contributor data terms: Go privacy table — Muse Spark 1.3/1.2 Contributor: **Model training: Yes; Data retention: Not ZDR**; all other Go models: Not used / 0 days (DeepSeek rows 0 days*, * = "ZDR agreement is renewed monthly. The current agreement is valid through September 30, 2026"). Meta's wording: "Heavily discounted token pricing in exchange for permission to use your prompts and completions to train future Meta models. Availability is limited to regions permitted by Meta's Geographic Use Policy." Sources: https://opencode.ai/docs/go, https://dev.meta.ai/docs/pricing-rate-limits.
- Full included-model list on the page (read 2026-09-16): Grok 4.6, GLM-5.3-Flash, GLM-5.3, GLM-5.2, GLM-5.1, GPT 5.6 Luna, Kimi K3, Kimi K2.7 Code, Kimi K2.6, LongCat-2.0, MiMo-V2.5, MiMo-V2.5-Pro, MiniMax M3, MiniMax M2.7, Muse Spark 1.3 Contributor, Muse Spark 1.2 Contributor, Qwen3.8 Max, Qwen3.8 Flash, Qwen3.7 Max, Qwen3.7 Plus, Qwen3.6 Plus, DeepSeek V4.1 Flash, DeepSeek V4 Pro, DeepSeek V4 Flash, DeepSeek V4 Flash Vision Exp, Hy4 preview, Hy3. Note: the pricing table additionally lists MiniMax M2.5, which is absent from the bullet list. Model IDs/endpoints: GLM/DeepSeek/Kimi → `/v1/chat/completions`; Muse/Grok/GPT-Luna → `/v1/responses`; MiniMax/Qwen → `/v1/messages`; full list fetchable at `https://opencode.ai/zen/go/v1/models`. Source: https://opencode.ai/docs/go.
- Minimum omp/opencode versions: **not found** in the Go docs (no version floor stated on the page).
- Abuse/client rules (verbatim requirements): typical coding-agent traffic; identify with own user agent (e.g. `my-coding-agent/1.0`); send stable `x-opencode-session` per conversation. Validated clients include OpenCode, Pi ("Current builds send session information… Update older installations"), Claude Code, Codex, Hermes, ZCode, jcode ≥ v0.81.6, Kilo Code CLI. Source: https://opencode.ai/docs/go.

## Gaps

- Artificial Analysis "Coding Index": no per-model Coding Index value appears on any of the five AA model pages read 2026-09-16 (pages report Intelligence Index v4.3, speed, price, verbosity). AA's coding-specific leaderboard (Terminal-Bench/SWE-bench composites) could not be resolved to per-model numbers from primary pages; recorded as not listed rather than estimated.
- llm-stats.com model pages for `glm-5-3-flash` and `deepseek-v4-flash` were blocked by a human-verification wall on 2026-09-16 (generic shell only); their llm-stats prices/scores are unverified. The `deepseek-v4.1-flash`, `kimi-k3`, and `muse-spark-1.3` pages rendered fully but show "Score pending" and no dataset benchmark scores.
- lmarena.ai detail pages (`lmarena.ai/leaderboard/text`) render as JS shells via fetch; all arena numbers above come from the embedded snapshot JSON in `https://lmarena.ai/leaderboard` (847 text-overall entries plus category snapshots, read 2026-09-16). `https://lmarena.ai/leaderboard/webdev` returned a data-less shell, so WebDev-category rows are cited to the main leaderboard page snapshot, not a dedicated WebDev page. DeepSeek V4.1 Flash has no text-overall arena entry (WebDev only); Kimi K3 has no plain-WebDev entry (image-to-WebDev only).
- Vendor-direct (non-proxy) list prices not verified on vendor pages: Z.ai's own GLM-5.3-Flash price page and Moonshot's official Kimi pricing page were not fetched (proxies used: Cloudflare Workers AI docs; llm-stats Moonshot row + benchlm.ai). Go's metered rates match the proxies exactly.
- Z.ai GLM-5.3 vs 5.3-Flash pricing nuance: third-party pages (e.g. https://evolink.ai/glm-5-3) quote GLM-5.3 at $1.40/$4.40; not vendor-verified, kept out of the per-model sections.
- No Go-docs statement found on: minimum omp/opencode versions, whether reasoning effort changes Go consumption, request-counting vs token-counting edge cases, or what "weekly" window boundaries are (rolling vs calendar).
- First-month pricing: a secondary search result (https://opencode.ai/v2/docs/console/go) mentions "$5 for your first month, then $10/month" but that page was not read directly; only the $10/month figure from https://opencode.ai/docs/go is primary-sourced here.
- AA Intelligence Index figures are effort-specific variants ("(max)" / "Reasoning, Max Effort"); OMP routes some roles at lower efforts, where scores would differ — AA does not publish per-effort scores on the pages read.

## Sources

- https://opencode.ai/docs/go — Go plan, model list, usage-limit mechanics and tables, endpoints, privacy, client rules (read 2026-09-16).
- https://api-docs.deepseek.com/quick_start/pricing/ — V4.1 Flash prices, peak hours, V4 Flash retirement note (read 2026-09-16).
- https://api-docs.deepseek.com/guides/thinking_mode — DeepSeek reasoning_effort values and OMP-ladder mapping (read 2026-09-16).
- https://api-docs.deepseek.com/updates/ — V4.1 Flash Sep 10 2026 release (found via search, page read 2026-09-16).
- https://docs.z.ai/guides/capabilities/thinking — GLM-5.3/Flash low/high/max-only efforts, forced thinking (read 2026-09-16).
- https://platform.kimi.ai/docs/guide/kimi-k3-quickstart — Kimi K3 low/high/max, default max (fetched 2026-09-16).
- https://ai.developer.meta.com/docs/features/reasoning — Muse reasoning_effort minimal–xhigh, none→400 (read 2026-09-16).
- https://dev.meta.ai/docs/pricing-rate-limits — Muse contributor vs standard pricing, training-exchange terms (read 2026-09-16).
- https://artificialanalysis.ai/models/muse-spark-1-3/ — Muse AA scores (read 2026-09-16).
- https://artificialanalysis.ai/models/glm-5-3-flash/ — GLM AA scores (read 2026-09-16).
- https://artificialanalysis.ai/models/deepseek-v4-1-flash/ — V4.1 Flash AA scores (read 2026-09-16).
- https://artificialanalysis.ai/models/deepseek-v4-flash/ — V4 Flash AA scores (read 2026-09-16).
- https://artificialanalysis.ai/models/kimi-k3/ — Kimi AA scores (read 2026-09-16).
- https://llm-stats.com/models/deepseek-v4.1-flash — V4.1 release/pricing/context (read 2026-09-16).
- https://llm-stats.com/models/kimi-k3 — Kimi release/pricing/context (read 2026-09-16).
- https://llm-stats.com/models/muse-spark-1.3 — Muse release/pricing/context (read 2026-09-16).
- https://lmarena.ai/leaderboard — text and WebDev arena ranks/ratings snapshot (read 2026-09-16).
- https://developers.cloudflare.com/workers-ai/models/glm-5.3-flash/ — GLM Flash price proxy (read 2026-09-16).
- https://openrouter.ai/meta/muse-spark-1.3-contributor — Muse 1.3 Sep 2 2026 release (found via search 2026-09-16).
- https://www.eigent.ai/blog/glm-5-3-flash-multimodal-model — GLM Flash Aug 26 2026 launch (found via search 2026-09-16).
- https://www.morphllm.com/deepseek-v4 — DeepSeek V4 Flash Jul 31 2026 GA (found via search 2026-09-16).
- https://www.verdent.ai/guides/agents/kimi-k3-api-guide — Kimi K3 Jul 16 2026 hosted launch (found via search 2026-09-16).
- https://benchlm.ai/moonshot/api-pricing — Kimi $3/$15 official-price corroboration (found via search 2026-09-16).
