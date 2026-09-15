# Anthropic Claude 5 family — evidence for routing (read 2026-09-16)

API ids in scope: `claude-opus-5`, `claude-sonnet-5`, `claude-fable-5-1`,
`claude-fable-5`, `claude-haiku-4-5`, and for context `claude-opus-4-8`.
All pages below were read on 2026-09-16 unless a different page date is quoted.
Prices are USD per 1M tokens (input / output) unless stated.
"Not listed" means the model was absent from that site's page/list on that date, not that it scores zero.

## Summary

- Current lineup per Anthropic's own overview: **Fable 5.1** = demanding reasoning / long-horizon agentic work (slower, $10/$50), **Opus 5** = complex agentic coding and enterprise work (moderate, $5/$25), **Sonnet 5** = best speed/intelligence blend (fast, $2/$10), **Haiku 4.5** = fastest, near-frontier (fastest, $1/$5). Source: https://platform.claude.com/docs/en/models/overview (read 2026-09-16).
- Release dates (Anthropic model pages, read 2026-09-16): Fable 5.1 **September 1, 2026** (https://platform.claude.com/docs/en/models/fable-5-1/overview); Opus 5 **July 24, 2026** (https://platform.claude.com/docs/en/models/opus-5/overview); Sonnet 5 **June 30, 2026** (https://platform.claude.com/docs/en/models/sonnet-5/overview); Fable 5 **June 9, 2026**, legacy (https://platform.claude.com/docs/en/models/fable-5/overview); Opus 4.8 **May 28, 2026**, legacy (https://platform.claude.com/docs/en/models/opus-4-8/overview); Haiku 4.5 **October 15, 2025** (https://platform.claude.com/docs/en/models/haiku-4-5/overview).
- Context / max output (same six pages): Fable 5.1, Opus 5, Sonnet 5, Fable 5, Opus 4.8 = **1M context / 128K max output** (Opus 5, Sonnet 5, Opus 4.8 also support 300K output on the Batch API with the `output-300k-2026-03-24` beta header); Haiku 4.5 = **200K / 64K**.
- Thinking/effort (https://platform.claude.com/docs/en/build-with-claude/effort, https://platform.claude.com/docs/en/models/overview — read 2026-09-16): Fable 5.1, Fable 5, Opus 5, Opus 4.8, Sonnet 5 use **adaptive thinking, default effort `high`**, with levels `low/medium/high/xhigh/max` (`xhigh` on Fable 5.1, Fable 5, Opus 5, Opus 4.8, Sonnet 5; `max` on all five plus Sonnet 4.6/Opus 4.6). Fable 5.1 and Fable 5 thinking is **always on**; Opus 5 thinking cannot be disabled at `xhigh`/`max` (400 error). Haiku 4.5 uses manual **extended thinking** (`budget_tokens`) and does **not** support the effort parameter.
- Official API pricing per 1M (https://platform.claude.com/docs/en/about-claude/pricing — read 2026-09-16): Fable 5.1 **$10 in / $50 out / $0.25 cache read** (2.5%, plus $12.50 5m-write / $20 1h-write); Fable 5 **$10 / $50 / $1.00** cache read; Opus 5 and Opus 4.8 **$5 / $25 / $0.50** ($6.25/$10 writes); Sonnet 5 **$2 / $10 / $0.20** ($2.50/$4 writes — the $2/$10 launch pricing scheduled to rise Sep 1, 2026 is now permanent); Haiku 4.5 **$1 / $5 / $0.10** ($1.25/$2 writes).
- Artificial Analysis Intelligence Index **v4.3** (max effort, read 2026-09-16): Fable 5.1 **53** (#1/199), Opus 5 **51** (#7/199), Fable 5 **50** (#8/199), Opus 4.8 **42** (#28/199), Sonnet 5 **38** (#42/199). AA output speed: Sonnet 5 **83.9**, Fable 5.1 **66.0**, Fable 5 **64.5**, Opus 4.8 **56.1**, Opus 5 **50.0 tok/s**. Haiku 4.5 has **no AA model page** (HTTP 404 on both slugs tried) — recorded as not listed. Sources: https://artificialanalysis.ai/models/claude-fable-5-1/ , https://artificialanalysis.ai/models/claude-opus-5/ , https://artificialanalysis.ai/models/claude-fable-5/ , https://artificialanalysis.ai/models/claude-opus-4-8/ , https://artificialanalysis.ai/models/claude-sonnet-5/ .
- DesignArena overall Text-to-HTML board (scraped via headless Chromium 2026-09-16; live board, values drift): Fable 5.1 **#6, 1346**; Opus 5 **#8, 1338**; Fable 5 **#12, 1325**. Sonnet 5, Haiku 4.5 and Opus 4.8 are **not listed** in the rendered overall slice (page renders the top ~20; expanding did not reveal further rows). Source: https://www.designarena.ai/leaderboard/code.
- DesignArena task boards (same scrape; full ranked lists, 159–172 rows each): Fable 5.1 beats Opus 5 on four of five boards; Opus 5 beats Fable 5.1 on UI Components. Sonnet 5 sits ranks 22–37 (1261–1297); Opus 4.8 ranks 30–45 (1252–1270); Haiku 4.5 ranks 106–118 (1115–1155). See per-model rows below.
- LMArena text-overall (https://lmarena.ai/leaderboard/text — board dated Sep 13, 2026, 8,146,274 votes, 402 models; read 2026-09-16): `claude-fable-5` **rank 1, 1506 ±5** (30,057 votes); `claude-fable-5.1-max` **rank 5, 1498 ±8**; `claude-opus-5-high` **rank 10, 1493 ±4**; `claude-opus-5-max` **rank 14, 1487 ±5**; `claude-opus-4-8-high` **rank 21, 1481 ±4**; `claude-opus-4-8` **rank 35, 1473 ±4**; `claude-sonnet-5-high` **rank 51, 1461 ±5**; `claude-haiku-4-5-20251001` **rank 129, 1415 ±3**. Unsuffixed `claude-sonnet-5`, `claude-opus-5`, `claude-fable-5.1` rows are **not listed** (only suffixed effort variants appear).
- LMArena WebDev (https://lmarena.ai/leaderboard/code/webdev — board dated Sep 12, 2026, 679,295 votes, 128 models; read 2026-09-16): `claude-fable-5.1-max` **rank 2, 1758 +14/-14** (3,036 votes); `claude-opus-5-max` **rank 3, 1687 ±7**; `claude-opus-5-high` **rank 7, 1660 ±7**; `claude-fable-5` **rank 10, 1628 ±7**; `claude-opus-4-8-high` **rank 24, 1559 ±7**; `claude-opus-4-8` **rank 30, 1539 ±6**; `claude-sonnet-5-high` **rank 33, 1537 ±7**; `claude-haiku-4-5-20251001` **rank 104 (spread 99–106), 1329 ±5**.
- Plan gating (https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan — read 2026-09-16): on **Max, premium Team seats, premium seat-based Enterprise seats**, Fable 5 and 5.1 are plan-included up to **50% of weekly limits**, then usage credits or switch models. On **Pro, standard Team/Enterprise seats** both Fable models are **usage-credits-only from the first message** (standard API rates). The 50%-promo for Fable 5 on other plans ended Jul 19, 2026; Fable 5.1 was never in it.
- Third-party/non-Anthropic clients (https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan — read 2026-09-16): the June 15, 2026 move of Agent SDK / `claude -p` / third-party-app usage off plan limits into a separate monthly credit (Pro $20, Max 5x $100, Max 20x $200) is **paused — "For now, nothing has changed: Claude Agent SDK, `claude -p`, and third-party app usage still draw from your subscription's usage limits."** The monthly credit is not available. So a subscription currently covers third-party-harness usage via plan limits, with usage-credits fallback only if enabled.

## Models

### `claude-opus-5`

- Identity/release: Claude Opus 5, "for complex agentic coding and enterprise work", released **July 24, 2026**; status Active (latest); retirement not sooner than July 24, 2027. Source: https://platform.claude.com/docs/en/models/opus-5/overview (read 2026-09-16).
- Context window: **1M tokens**; max output **128K** (300K on Batch API with `output-300k-2026-03-24` beta). Reliable knowledge cutoff May 2026, training cutoff May 2026. Source: same page.
- API price per 1M: **$5 in / $25 out**; 5m cache write $6.25, 1h write $10, cache read **$0.50** (10%). Batch 50% off. Fast-mode preview prices Opus 5 at $10/$50. Sources: https://platform.claude.com/docs/en/about-claude/pricing , https://platform.claude.com/docs/en/models/opus-5/overview (read 2026-09-16).
- Supported thinking/effort: **adaptive thinking, default `high`**; levels `low, medium, high, xhigh, max`. Thinking cannot be disabled at `xhigh`/`max` (400). At `xhigh`/`max` set large `max_tokens` (64K starting default suggested). Sources: https://platform.claude.com/docs/en/build-with-claude/effort , https://platform.claude.com/docs/en/models/overview (read 2026-09-16).
- Artificial Analysis (v4.3, max effort, read 2026-09-16): Intelligence Index **51** (#7/199); output speed **50.0 tok/s** (#127); price $5/$25, 90% cache discount; cost per Index task $5.86. Coding Index: **not listed** (no Coding Index value on the model page). Source: https://artificialanalysis.ai/models/claude-opus-5/
- DesignArena (scraped 2026-09-16, https://www.designarena.ai/leaderboard/code): overall **#8, 1338**; General Purpose **#7, 1318**; Landing Page **#11, 1321**; Dashboard **#12, 1312**; Productivity **#12, 1296**; UI Components **#5, 1361**.
- lmarena.ai (read 2026-09-16): text-overall `claude-opus-5-high` **rank 10, 1493 ±4** (42,617 votes), `claude-opus-5-max` **rank 14, 1487 ±5** (20,706 votes); unsuffixed `claude-opus-5` **not listed**. WebDev `claude-opus-5-max` **rank 3, 1687 +7/-7** (12,087 votes), `claude-opus-5-high` **rank 7, 1660 +7/-7** (12,566 votes). Sources: https://lmarena.ai/leaderboard/text , https://lmarena.ai/leaderboard/code/webdev

### `claude-sonnet-5`

- Identity/release: Claude Sonnet 5, "the best combination of speed and intelligence", released **June 30, 2026**; Active (latest); retirement not sooner than June 30, 2027. Drop-in upgrade for Sonnet 4.6 with three behavior changes: adaptive thinking on by default, manual extended thinking → 400, non-default sampling params → 400. Source: https://platform.claude.com/docs/en/models/sonnet-5/overview (read 2026-09-16).
- Context window: **1M tokens**; max output **128K** (300K on Batch API beta). Reliable knowledge cutoff Jan 2026, training cutoff Jan 2026. Source: same page.
- API price per 1M: **$2 in / $10 out**; 5m write $2.50, 1h write $4, cache read **$0.20**. The $2/$10 launch pricing (due to rise Sep 1, 2026) is now permanent. Batch 50% off. Source: https://platform.claude.com/docs/en/about-claude/pricing (read 2026-09-16).
- Supported thinking/effort: **adaptive, default `high`**; `xhigh` and `max` available; `medium` documented as comparable to Sonnet 4.6 at high effort. Sources: https://platform.claude.com/docs/en/build-with-claude/effort , https://platform.claude.com/docs/en/models/overview (read 2026-09-16).
- Artificial Analysis (v4.3, max effort, read 2026-09-16): Intelligence Index **38** (#42/199); output speed **83.9 tok/s** (#70); price $2/$10, 90% cache discount; cost per Index task $5.09. Coding Index: **not listed**. Source: https://artificialanalysis.ai/models/claude-sonnet-5/
- DesignArena (scraped 2026-09-16, https://www.designarena.ai/leaderboard/code): overall **not listed** (outside rendered top-20 slice); General Purpose **#37, 1263**; Landing Page **#29, 1289**; Dashboard **#30, 1280**; Productivity **#37, 1261**; UI Components **#22, 1297**.
- lmarena.ai (read 2026-09-16): text-overall `claude-sonnet-5-high` **rank 51, 1461 ±5** (35,301 votes); unsuffixed `claude-sonnet-5` **not listed**. WebDev `claude-sonnet-5-high` **rank 33, 1537 +7/-7** (9,296 votes); unsuffixed `claude-sonnet-5` **not listed**. Sources: https://lmarena.ai/leaderboard/text , https://lmarena.ai/leaderboard/code/webdev

### `claude-fable-5-1`

- Identity/release: Claude Fable 5.1, "for demanding reasoning and long-horizon agentic work", released **September 1, 2026**; Active (latest); retirement not sooner than September 1, 2027. Same input/output prices as Fable 5 with cache reads at a quarter of the cost. Source: https://platform.claude.com/docs/en/models/fable-5-1/overview (read 2026-09-16).
- Context window: **1M tokens**; max output **128K**. Reliable knowledge cutoff Jun 2026, training cutoff Jun 2026. Source: same page.
- API price per 1M: **$10 in / $50 out**; 5m write $12.50, 1h write $20, cache read **$0.25** (2.5%). Batch 50% off. Source: https://platform.claude.com/docs/en/about-claude/pricing (read 2026-09-16).
- Supported thinking/effort: **adaptive, always on**, default `high`; **all five levels** (`low/medium/high/xhigh/max`); per-message effort switching (beta) preserves prompt cache; forced tool use returns an error. Sources: https://platform.claude.com/docs/en/build-with-claude/effort , https://platform.claude.com/docs/en/models/fable-5-1/overview (read 2026-09-16).
- Artificial Analysis (v4.3, max effort with default fallback, read 2026-09-16): Intelligence Index **53** (#1/199); output speed **66.0 tok/s** (#80); price $10/$50, 98% cache discount; cost per Index task $7.63. Coding Index: **not listed**. Source: https://artificialanalysis.ai/models/claude-fable-5-1/
- DesignArena (scraped 2026-09-16, https://www.designarena.ai/leaderboard/code): overall **#6, 1346**; General Purpose **#2, 1348**; Landing Page **#7, 1332**; Dashboard **#5, 1328**; Productivity **#4, 1318**; UI Components **#12, 1335**.
- lmarena.ai (read 2026-09-16): text-overall `claude-fable-5.1-max` **rank 5, 1498 ±8** (5,783 votes); unsuffixed `claude-fable-5.1` **not listed**. WebDev `claude-fable-5.1-max` **rank 2, 1758 +14/-14** (3,036 votes). Sources: https://lmarena.ai/leaderboard/text , https://lmarena.ai/leaderboard/code/webdev

### `claude-fable-5`

- Identity/release: Claude Fable 5, released **June 9, 2026**; status Active (**legacy** — Anthropic recommends migrating to Fable 5.1); retirement not sooner than June 9, 2027. Source: https://platform.claude.com/docs/en/models/fable-5/overview (read 2026-09-16).
- Context window: **1M tokens**; max output **128K**. Reliable knowledge cutoff Jan 2026, training cutoff Jan 2026. Source: same page.
- API price per 1M: **$10 in / $50 out**; 5m write $12.50, 1h write $20, cache read **$1.00** (10%). Batch 50% off. Source: https://platform.claude.com/docs/en/about-claude/pricing (read 2026-09-16).
- Supported thinking/effort: **adaptive, always on**, default `high`; `xhigh` and `max` available (start at `high`, step up for capability-sensitive work, down for routine work). Source: https://platform.claude.com/docs/en/build-with-claude/effort (read 2026-09-16).
- Artificial Analysis (v4.3, max effort with Opus 4.8 fallback, read 2026-09-16): Intelligence Index **50** (#8/199); output speed **64.5 tok/s** (#82); price $10/$50, 90% cache discount; cost per Index task $8.75. Coding Index: **not listed**. Source: https://artificialanalysis.ai/models/claude-fable-5/
- DesignArena (scraped 2026-09-16, https://www.designarena.ai/leaderboard/code): overall **#12, 1325**; General Purpose **#6, 1320**; Landing Page **#9, 1325**; Dashboard **#11, 1313**; Productivity **#7, 1307**; UI Components **#14, 1331**.
- lmarena.ai (read 2026-09-16): text-overall `claude-fable-5` **rank 1, 1506 ±5** (30,057 votes). WebDev `claude-fable-5` **rank 10, 1628 +7/-7** (10,081 votes). Sources: https://lmarena.ai/leaderboard/text , https://lmarena.ai/leaderboard/code/webdev

### `claude-haiku-4-5`

- Identity/release: Claude Haiku 4.5, "the fastest model with near-frontier intelligence", released **October 15, 2025**; Active (latest); retirement not sooner than October 15, 2026. API id `claude-haiku-4-5-20251001`, alias `claude-haiku-4-5`. Source: https://platform.claude.com/docs/en/models/haiku-4-5/overview (read 2026-09-16).
- Context window: **200K tokens**; max output **64K**. Reliable knowledge cutoff Feb 2025, training cutoff Jul 2025. Source: same page.
- API price per 1M: **$1 in / $5 out**; 5m write $1.25, 1h write $2, cache read **$0.10**. Batch 50% off. Source: https://platform.claude.com/docs/en/about-claude/pricing (read 2026-09-16).
- Supported thinking/effort: manual **extended thinking** (`thinking.type: "enabled"` + `budget_tokens`); the **effort parameter is not supported**. Source: https://platform.claude.com/docs/en/models/overview (read 2026-09-16).
- Artificial Analysis: **not listed** — https://artificialanalysis.ai/models/claude-haiku-4-5/ and https://artificialanalysis.ai/models/claude-haiku-4-5-20251001/ both return HTTP 404 (read 2026-09-16). No Intelligence Index, speed, or price verifiable there.
- DesignArena (scraped 2026-09-16, https://www.designarena.ai/leaderboard/code): overall **not listed** (outside rendered top-20 slice); General Purpose **#118, 1140**; Landing Page **#114, 1119**; Dashboard **#109, 1151**; Productivity **#106, 1155**; UI Components **#110, 1115**.
- lmarena.ai (read 2026-09-16): text-overall `claude-haiku-4-5-20251001` **rank 129, 1415 ±3** (129,278 votes). WebDev `claude-haiku-4-5-20251001` **rank 104 (spread 99–106), 1329 ±5** (27,785 votes). Sources: https://lmarena.ai/leaderboard/text , https://lmarena.ai/leaderboard/code/webdev

### `claude-opus-4-8` (context)

- Identity/release: Claude Opus 4.8, released **May 28, 2026**; status Active (**legacy** — Anthropic recommends Opus 5); retirement not sooner than May 28, 2027. Source: https://platform.claude.com/docs/en/models/opus-4-8/overview (read 2026-09-16).
- Context window: **1M tokens**; max output **128K** (300K on Batch API beta). Reliable knowledge cutoff Jan 2026, training cutoff Jan 2026. Source: same page.
- API price per 1M: **$5 in / $25 out**; cache read **$0.50** ($6.25/$10 writes). Batch 50% off. Source: https://platform.claude.com/docs/en/about-claude/pricing (read 2026-09-16).
- Supported thinking/effort: **adaptive, default `high`**; `xhigh` and `max` available (guidance: start at `xhigh` for coding/agentic). Source: https://platform.claude.com/docs/en/build-with-claude/effort (read 2026-09-16).
- Artificial Analysis (v4.3, max effort, read 2026-09-16): Intelligence Index **42** (#28/199); output speed **56.1 tok/s** (#105); price $5/$25, 90% cache discount; cost per Index task $4.08. Page carries a deprecated-model banner pointing at Opus 5. Coding Index: **not listed**. Source: https://artificialanalysis.ai/models/claude-opus-4-8/
- DesignArena (scraped 2026-09-16, https://www.designarena.ai/leaderboard/code): overall **not listed** (outside rendered top-20 slice); General Purpose **#40, 1256**; Landing Page **#41, 1269**; Dashboard **#45, 1252**; Productivity **#30, 1269**; UI Components **#40, 1270**.
- lmarena.ai (read 2026-09-16): text-overall `claude-opus-4-8-high` **rank 21, 1481 ±4** (52,535 votes), `claude-opus-4-8` **rank 35, 1473 ±4** (53,446 votes). WebDev `claude-opus-4-8-high` **rank 24, 1559 +7/-7** (13,787 votes), `claude-opus-4-8` **rank 30, 1539 +6/-6** (12,654 votes). Sources: https://lmarena.ai/leaderboard/text , https://lmarena.ai/leaderboard/code/webdev

## Plans and limits

Plan identification (all read 2026-09-16):

- **Pro $20/month** (≥5x the free-service usage per session), **Max 5x $100/month** (5x Pro usage), **Max 20x $200/month** (20x Pro usage). Mobile pricing may vary; Max is monthly-only. Sources: https://support.claude.com/en/articles/8325606-what-is-the-pro-plan , https://support.claude.com/en/articles/11049741-what-is-the-max-plan
- The Pro plan does **not** include API usage through the Claude Console — Console API is paid separately. Source: https://support.claude.com/en/articles/8325606-what-is-the-pro-plan

What counts against the limit:

- Session usage varies with message length, file-attachment size, conversation length, tool use (Research, web search), **model choice, effort level**, and artifact creation/usage. Project content is cached and reused portions don't recount. Sources: https://support.claude.com/en/articles/9797557-usage-limit-best-practices , https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan
- Claude Code (terminal and IDE: VS Code, Cursor/forks, JetBrains) on Pro/Max shares **one unified subscription and the same usage limits** as Claude chat. If `ANTHROPIC_API_KEY` is set, Code bills to the API key instead of the plan. Sources: https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan
- Usage credits (opt-in prepay) bill **at standard API rates** and cover both Claude conversations and Claude Code terminal usage once plan limits are hit; session limits still reset every five hours. Spend caps and auto-reload are configurable; daily redemption limit $2000. Source: https://support.claude.com/en/articles/12429409-manage-usage-credits-for-paid-claude-plans

Reset windows:

- **5-hour session window** on Pro and both Max tiers; **weekly usage limit across all models** resetting at a **fixed account-specific time** (unchanged by subscription start); next reset visible in Settings > Usage. Anthropic may additionally apply weekly/monthly caps or model/feature caps at its discretion. Sources: https://support.claude.com/en/articles/8325606-what-is-the-pro-plan , https://support.claude.com/en/articles/11049741-what-is-the-max-plan
- The Usage page shows **current session, weekly limits (split "for Opus only and all other models")**, and usage-credit consumption. Source: https://support.claude.com/en/articles/9797557-usage-limit-best-practices

Per-model / per-effort differences:

- **Fable gating** (verbatim mechanics): on Max / premium Team seats / premium seat-based Enterprise seats, Fable 5 and 5.1 are plan-included up to **50% of weekly usage limits** ("draw from your plan's regular weekly usage limits and use them faster than other Claude models"); past that, usage credits or switch models. On Pro / standard Team / standard seat-based Enterprise, both Fable models run on **usage credits from the start** (standard API rates). Usage-based Enterprise and the Claude API bill Fable at standard API rates. The Fable 5 50%-promo for other plans ended Jul 19, 2026 at 11:59:59 PM PT; Fable 5.1 was never in it. Source: https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan
- Access minimums: Fable 5 needs Claude Code ≥ 2.1.170; Fable 5.1 needs ≥ 2.1.255. Source: same page.
- Effort is the cost lever: higher effort spends more tokens (thinking included); Opus 5 docs recommend `low`/`medium` wherever evals show quality holds, and note effort does not reliably shorten visible response length. Source: https://platform.claude.com/docs/en/build-with-claude/effort

Shared with chat / overage / third-party:

- Plan usage is **shared across Claude (web/desktop/mobile) and Claude Code**; hitting the limit offers: upgrade tier, enable usage credits, buy Console API credits, or wait for reset. Source: https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan
- **Third-party / non-Anthropic clients**: as documented on 2026-09-16, Agent SDK, `claude -p`, and third-party-app usage **still draw from the subscription's usage limits** — the announced June 15, 2026 change (separate monthly Agent SDK credit: Pro $20, Max 5x $100, Max 20x $200, Team standard $20 / premium $100, usage-based Enterprise $20, seat-based Enterprise premium $200; overage to usage credits) is **paused and not in effect**, with a rework promised before anything takes effect. Source: https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan
- Practical consequence for one subscription as the primary ladder: no Anthropic page found authorises a named per-model weekly message count (unlike OpenAI's published 5-hour estimates); capacity is expressed only as 5x/20x multipliers plus the Fable 50%-of-weekly rule and the discretionary-caps clause above.

## Opus 5 vs Fable 5.1 vs Sonnet 5 — cited-numbers comparison

(a) Frontend/design generation. DesignArena overall: Fable 5.1 #6 (1346) ahead of Opus 5 #8 (1338); Sonnet 5 not in the rendered top-20 slice. Task boards: General Purpose Fable 5.1 #2 (1348) > Opus 5 #7 (1318) > Sonnet 5 #37 (1263); Landing Page Fable 5.1 #7 (1332) > Opus 5 #11 (1321) > Sonnet 5 #29 (1289); Dashboard Fable 5.1 #5 (1328) > Opus 5 #12 (1312) > Sonnet 5 #30 (1280); Productivity Fable 5.1 #4 (1318) > Opus 5 #12 (1296) > Sonnet 5 #37 (1261); UI Components reverses — Opus 5 #5 (1361) > Fable 5.1 #12 (1335) > Sonnet 5 #22 (1297). LMArena WebDev agrees: Fable-5.1-max #2 (1758) > Opus-5-max #3 (1687) > Opus-5-high #7 (1660) > Sonnet-5-high #33 (1537). AA Intelligence Index v4.3: Fable 5.1 53 (#1) > Opus 5 51 (#7) > Sonnet 5 38 (#42). All sources read 2026-09-16; board URLs and page URLs as cited per model above.

(b) Routine code edits. No cited source in this report measures routine-edit quality directly (DesignArena is single-shot text→HTML visual preference with no tools, repo context or multi-turn; LMArena text/WebDev are preference votes; AA v4.3 is a 10-eval general composite — see Gaps). On the numbers that do exist: Sonnet 5 is the cheapest/fastest of the three ($2/$10 per 1M, 83.9 tok/s AA, Anthropic "fast" latency) and Anthropic documents `medium` effort as comparable to Sonnet 4.6 at high effort; Opus 5 costs 2.5x Sonnet 5 ($5/$25, 50.0 tok/s, "moderate" latency) with a higher AA index (51 vs 38); Fable 5.1 costs 5x Sonnet 5 ($10/$50, 66.0 tok/s, "slower" latency) with the top AA index (53) but is usage-credits-only from the first message on Pro/standard-team plans and capped at 50% of weekly limits on Max/premium plans. So the cited numbers support Fable 5.1 for the hardest design/agentic work, Opus 5 as the middle rung (notably strongest of the three on UI Components at #5/1361), and Sonnet 5 as the cheap/fast rung — with the routine-edit quality ordering itself unverified by any cited benchmark.

## Gaps

- Artificial Analysis "Coding Index": no per-model Coding Index value appears on any of the six AA model pages read 2026-09-16 (pages report Intelligence Index v4.3, speed, price, verbosity). Recorded as not listed rather than estimated.
- `claude-haiku-4-5` on AA: both https://artificialanalysis.ai/models/claude-haiku-4-5/ and https://artificialanalysis.ai/models/claude-haiku-4-5-20251001/ return HTTP 404 on 2026-09-16 — no AA score, speed, or price verifiable there.
- Unsuffixed LMArena rows: text-overall and WebDev boards list only effort-suffixed Claude variants (`-high`, `-max`, dated snapshots); bare `claude-opus-5`, `claude-sonnet-5`, `claude-fable-5.1` rows are not listed, so the arena numbers above are effort-specific and do not read across to other efforts.
- DesignArena overall ranks for Sonnet 5, Haiku 4.5, Opus 4.8: the overall board page renders only the top ~20 rows (74 content lines; the "Show N More" control did not expand the overall list on 2026-09-16), so exact overall ranks/Elos for these three are unverified; their task-board ranks (full 159–172-row lists) are cited instead.
- DesignArena values drift live: overall Elos scraped 2026-09-16 (e.g. Sol xhigh 1351, Muse Max 1374) differ by 1 point from `docs/research/designarena-2026-09.md` (1352, 1373); ties share ranks (e.g. Opus 5 and Gemini 3.8 Flash both shown at rank 7 on General Purpose).
- SWE-bench / Terminal-Bench standalone per-model scores on AA: not extracted (component charts are JS-rendered); AA Intelligence Index v4.3 does incorporate Terminal-Bench 4.0 among its 10 evals, but only the composite is cited.
- No Anthropic page found publishing per-model weekly message counts or a per-model rate-limit table for plan usage (only 5x/20x multipliers, the Fable 50% rule, and the discretionary-caps clause); burn-rate-per-model on a subscription is therefore not verifiable from primary docs.
- The paused Agent SDK monthly-credit schedule (Pro $20 / Max 5x $100 / Max 20x $200) is documented only as a paused proposal; it MUST NOT be treated as current policy.
- llm-stats.com pages were not fetched for Claude models; no llm-stats scores, TTFT, or blended-cost ranks are cited here.
- Claude Mythos 5 / 5.1 (Glasswing-only) share Fable specs/pricing but are out of scope and unverified beyond the pricing-table rows.

## Sources

- https://platform.claude.com/docs/en/models/overview — lineup, per-model pricing/context/thinking/default-effort snapshot (read 2026-09-16).
- https://platform.claude.com/docs/en/models/opus-5/overview — Opus 5 release/context/pricing/availability (read 2026-09-16).
- https://platform.claude.com/docs/en/models/sonnet-5/overview — Sonnet 5 release/context/pricing/availability (read 2026-09-16).
- https://platform.claude.com/docs/en/models/fable-5-1/overview — Fable 5.1 release/context/pricing/availability (read 2026-09-16).
- https://platform.claude.com/docs/en/models/fable-5/overview — Fable 5 release/context/pricing/legacy status (read 2026-09-16).
- https://platform.claude.com/docs/en/models/opus-4-8/overview — Opus 4.8 release/context/pricing/legacy status (read 2026-09-16).
- https://platform.claude.com/docs/en/models/haiku-4-5/overview — Haiku 4.5 release/context/pricing/availability (read 2026-09-16).
- https://platform.claude.com/docs/en/about-claude/pricing — official per-Mtok input/output/cache-write/cache-read prices, Sonnet 5 pricing note, batch/fast-mode/long-context terms (read 2026-09-16).
- https://platform.claude.com/docs/en/build-with-claude/effort — effort levels, per-model availability, defaults, model-specific guidance (read 2026-09-16).
- https://artificialanalysis.ai/models/claude-opus-5/ — Opus 5 AA scores (read 2026-09-16).
- https://artificialanalysis.ai/models/claude-sonnet-5/ — Sonnet 5 AA scores (read 2026-09-16).
- https://artificialanalysis.ai/models/claude-fable-5-1/ — Fable 5.1 AA scores (read 2026-09-16).
- https://artificialanalysis.ai/models/claude-fable-5/ — Fable 5 AA scores (read 2026-09-16).
- https://artificialanalysis.ai/models/claude-opus-4-8/ — Opus 4.8 AA scores (read 2026-09-16).
- https://artificialanalysis.ai/models/claude-haiku-4-5/ — HTTP 404 on 2026-09-16 (not listed).
- https://artificialanalysis.ai/models/claude-haiku-4-5-20251001/ — HTTP 404 on 2026-09-16 (not listed).
- https://www.designarena.ai/leaderboard/code — overall + General Purpose / Landing Page / Dashboard / Productivity / UI Components boards, scraped via headless Chromium (read 2026-09-16).
- https://lmarena.ai/leaderboard/text — text-overall ranks/ratings/votes snapshot (board dated Sep 13, 2026; read 2026-09-16).
- https://lmarena.ai/leaderboard/code/webdev — WebDev-category ranks/ratings/votes snapshot (board dated Sep 12, 2026; read 2026-09-16).
- https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan — Fable plan gating, 50% weekly rule, credits-only tiers, version minimums (read 2026-09-16).
- https://support.claude.com/en/articles/12429409-manage-usage-credits-for-paid-claude-plans — usage-credits mechanics, API-rate billing, spend controls (read 2026-09-16).
- https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan — third-party/Agent SDK subscription treatment, paused credit (read 2026-09-16).
- https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan — Code/plan shared limits, IDE coverage, API-key override (read 2026-09-16).
- https://support.claude.com/en/articles/8325606-what-is-the-pro-plan — Pro price, 5h + weekly limits, Console API exclusion (read 2026-09-16).
- https://support.claude.com/en/articles/11049741-what-is-the-max-plan — Max 5x/20x prices and multipliers, 5h + weekly limits (read 2026-09-16).
- https://support.claude.com/en/articles/9797557-usage-limit-best-practices — what counts toward limits (model, effort, tools), Opus-only vs other-models weekly split, Usage page (read 2026-09-16).
