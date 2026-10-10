# ChatGPT vs SuperGrok as the supplemental coding subscription (read 2026-10-10)

Decision: keep the Anthropic subscription (Claude Opus/Sonnet for default/plan/task),
drop OpenCode Go and Muse Code, add **exactly one** of ChatGPT (OpenAI) or SuperGrok (xAI)
to cover the omp roles that must not run on Anthropic lineage or that should be cheap:
adversary/reviewer/advisor, scout/smol/tiny/commit, code-worker/sonic, research.

All web pages below were read on 2026-10-10 unless a different date is quoted.
Local probes ran on this checkout on 2026-10-10 (omp v18.8.7). No config was changed,
no login was performed. Anything not verified from a primary source is marked UNVERIFIED.

Boundary: the agent-product comparison (OpenAI "Dots" vs xAI "Grok Bot") is covered
separately; this file uses only the minimum agent-product facts needed for the quota
argument (Grok Bot draws from the SuperGrok weekly pool).

## 1. Harness-support verdict

**Both subscriptions work in omp today. Neither needs a paid API key.**

| Subscription | omp provider id | Auth | Status on this machine |
| --- | --- | --- | --- |
| ChatGPT Plus/Pro (Codex subscription) | `openai-codex` | `omp login` → "ChatGPT Plus/Pro (Codex Subscription)" (OAuth; headless/device variant `openai-codex-device` also exists) | Logged out; also listed in `disabledProviders` in `omp/config.yml`, so its models are hidden until re-enabled |
| SuperGrok (or X Premium+) | `xai-oauth` | `omp login` → "xAI Grok OAuth (SuperGrok or X Premium+)" (OAuth) | Logged out; never configured here |
| xAI API (metered, pay-per-token) | `xai` | `XAI_API_KEY` | Key-based only; not needed for either subscription path |

Local evidence (commands; stdin closed where applicable; nothing mutated):

- `omp login` (menu, read 2026-10-10) lists, among others:
  `1. ChatGPT Plus/Pro (Codex Subscription)`, `12. ChatGPT Plus/Pro (Codex, headless/device)`,
  `13. xAI API`, `14. xAI Grok OAuth (SuperGrok or X Premium+)`.
- `omp auth-broker list` (2026-10-10) confirms provider ids `openai-codex`,
  `openai-codex-device`, `xai`, `xai-oauth` with the same labels.
- `omp models` (2026-10-10) shows only `anthropic (28)`, `muse-code (6)`,
  `opencode-go (46)`, `openrouter (568)` (plus `local`, `web` under `--kind all`).
  `omp models openai-codex` and `omp models xai` both print `No models matching "…"`.
  Logged-out OAuth providers publish no catalog rows — absence from `omp models`
  is an auth state, not a capability gap. (`omp/config.yml` additionally carries
  `disabledProviders: [openai-codex]`, a leftover of the dropped subscription;
  re-adding ChatGPT means removing that line and running `omp login`.)
- Binary strings in `/home/sudaksh/.local/bin/omp` (2026-10-10) confirm both providers
  are first-class: an OAuth module `@oh-my-pi/pi-ai/oauth/xai-oauth`; `xai-oauth`
  billing against `cli-chat-proxy.grok.com/v1/billing`; model-id prefixes `xai/`
  and `xai-oauth/` both accepted; the `openai-codex` provider ships model ids
  `openai-codex/gpt-5.3-codex-spark`, `openai-codex/gpt-5.4-mini`,
  `openai-codex/gpt-5.5`, `openai-codex/gpt-5.6-luna`, `openai-codex/gpt-5.6-sol`.
  GPT-6-era `openai-codex/*` ids are **UNVERIFIED in the omp catalog** (not in the
  binary strings; the catalog is server-driven and this provider is logged out) —
  verify with `omp models openai-codex` after login. OpenAI's canonical model ids
  (`gpt-6.1-sol`, `gpt-6-sol`, `gpt-6-luna`, `gpt-6-astra`) are confirmed at
  https://learn.chatgpt.com/docs/models and https://developers.openai.com/api/docs/pricing
  (both read 2026-10-10); omp convention is `<provider-id>/<model-id>`.
- `~/.omp/agent/models.db`, table `model_cache` (2026-10-10): no rows for
  `openai-codex` or `xai-oauth` (never authenticated); the API-key `xai` provider
  caches 35 models including `grok-4.5`, `grok-4.6`, `grok-4.7`, `grok-build-0.1`,
  `grok-code-fast-1`.
- `omp usage` (2026-10-10) shows accounts only for Anthropic, Muse Code, OpenCode Go —
  no `openai-codex` or `xai-oauth` account, as expected while logged out.
- Subscription-adjacent native CLIs exist for both, but omp needs neither:
  Codex CLI/IDE with ChatGPT sign-in (https://learn.chatgpt.com/docs/models lists
  desktop app, web, CLI, IDE as Codex surfaces); Grok Build CLI (`grok`, browser
  auth on first launch, `XAI_API_KEY` fallback) at https://docs.x.ai/build/overview
  (read 2026-10-10). Grok Build is xAI's coding agent (TUI, headless `-p`, ACP).

Consequences:

- Re-adding ChatGPT = `omp login` (pick the Codex Subscription entry) + drop
  `openai-codex` from `disabledProviders`. No API key, no third-party harness
  terms problem beyond OpenAI's own client rules.
- Adding SuperGrok = `omp login` (pick the Grok OAuth entry). No API key. The same
  login also unlocks Grok's X-search tools in-harness: omp's binary strings state
  that reading X goes through Grok's X tools and needs `xai-oauth` login or
  `XAI_API_KEY` — a small research-role bonus unique to the xAI option.
- xAI API-key (`xai/*`, $2/$6 per 1M for grok-4.6/4.7 under 200k prompt tokens,
  https://docs.x.ai/developers/pricing, read 2026-10-10) is a separate metered
  path; it is not required to consume a SuperGrok subscription in omp.

## 2. Subscription tiers and coding quotas

### 2a. ChatGPT (OpenAI) — primary: https://learn.chatgpt.com/docs/pricing (read 2026-10-10)

Plan cards: Free $0, Go $8/mo, **Plus $20/mo**, **Pro from $100/mo with plans at
$100, $200, $500**, Business $20/user/mo, Enterprise/Edu (contact sales), API Key
(pay-per-token, no cloud features). Codex and ChatGPT Work share one usage pool;
included plan usage is consumed first, then purchased credits (Plus/Pro) or
workspace credits (Business/Enterprise/Edu); extra local chats can run on an API
key at standard API rates. If a limit hits mid-turn, the agent finishes that turn
under fair use, then stops.

Recommended coding models (https://learn.chatgpt.com/docs/models, read 2026-10-10):
**GPT-6.1 Sol** (near-Astra performance at lower cost; rollout covers Plus, Pro,
Business, Enterprise, Edu in desktop app + CLI + web Work; Free/Go excluded),
**GPT-6 Sol**, **GPT-6 Luna** (efficient/high-volume), **GPT-6 Astra** (most capable).
Legacy: GPT-5.5 retires from ChatGPT/Work/Codex on all plans **2026-10-14** (API
unaffected); GPT-5.3-Codex-Spark retired 2026-09-14; gpt-5.4/mini retired from
Codex sign-in 2026-08-31. Model availability also depends on client and rollout.

Reasoning control: Light (= `low` in config/CLI) / Medium / High / Extra High /
Max / Ultra; start Luna at High, Astra at Light/Low. **Luna supports up to Max,
not Ultra.** "Some paid plans omit Astra Extra High." Speed modes: Fast costs
2.5x included usage (2x purchased credits); Ultrafast 8x included / 6x credits,
Pro $500 + eligible Enterprise/Edu only.

Published 5-hour local-message estimates (Plus and Standard Business; **Pro plans
currently have no five-hour limit**; cloud tasks may cost more; weekly limits may
also apply; "estimates are not fixed message limits"):

| Model | Plus / 5h | Credit rate / 1M in / cached / out (Standard) |
| --- | --- | --- |
| GPT-6 Astra | 5–45 | 250 / 25 / 1,250 |
| GPT-6.1 Sol | 15–160 | 50 / 2.5 / 250 |
| GPT-6 Sol | 15–150 | 50 / 5 / 250 |
| GPT-6 Luna | 350–3,000 | 2.5 / 0.25 / 12.5 |
| GPT-5.6 Sol (legacy, promo pricing thru 2026-11-21) | older card: 10–100 | 100 / 10 / 500 |
| GPT-5.6 Terra (legacy) | older card: 25–200 | 50 / 5 / 300 |
| GPT-5.6 Luna (legacy) | older card: 250–2,000 | 5 / 0.5 / 30 |

Credit rates: https://learn.chatgpt.com/docs/pricing token-rates table (read
2026-10-10); 5.6-family rows unchanged from the 2026-09-16 snapshot
(`docs/research/openai-codex-models-2026-09.md`). A typical 5.6-Sol task uses
2–15 credits. Higher effort costs more through tokens, not a separate rate.

### 2b. SuperGrok (xAI) — primary: https://x.ai/pricing, https://x.ai/bot, https://docs.x.ai/grok/faq, https://docs.x.ai/grok/overview (all read 2026-10-10)

Tiers (individual): Free $0; SuperGrok Lite (listed, price not exposed in the
fetchable page — **UNVERIFIED**, third parties report $10/mo); **SuperGrok $30/mo**
(Grok 4.6 model, Grok Bot access, connectors, higher limits, Expert, Imagine);
**SuperGrok Plus $100/mo** (everything in SuperGrok + 1080p video, significantly
higher usage, priority access, early access); SuperGrok Heavy (listed, "highest
usage at the fastest speed … most powerful intelligence", price not exposed in
the fetchable page — **UNVERIFIED**, third parties report $300/mo); plus Business
and Enterprise. Sources: https://x.ai/pricing (tier names, $30/$100, feature
bullets) and https://x.ai/bot (Heavy positioning, "weekly Grok Bot usage included",
Bot available to SuperGrok/Plus/Heavy). grok.com/plans and grok.com/supergrok are
JS-gated (Cloudflare/app shell) and could not be read — Lite/Heavy prices and any
numeric per-tier allowances are therefore UNVERIFIED from primary sources.

Usage mechanics (https://docs.x.ai/grok/faq, read 2026-10-10): since June 2026,
paid plans draw from **one shared weekly usage pool** spendable across any Grok
product (Chat, Imagine, Voice, Build, Bot); different products burn pool at
different compute rates ("a long coding task uses far more" than a chat message);
pool resets weekly (schedule in Settings → Usage); on exhaustion, paid features
pause to free-tier Chat/Voice levels, with options to buy Extra Usage Credits
(from $5 on web, expire after 1 year, priced above the plan's effective rate),
enable Auto Top Up, or upgrade. **No published per-model message counts** — unlike
OpenAI's 5h table, xAI publishes no numeric quota per tier, so effective coding
volume per dollar is UNVERIFIED until metered in practice.

Grok Build note (https://docs.x.ai/build/overview, read 2026-10-10): Grok Build is
the coding agent; `grok-4.7` is the latest model, also callable on the xAI API.
"Grok 4.7 Fast" (2x token rates, 1.5x long-context) is Cursor- and Grok-Build-only,
not on the public API (https://docs.x.ai/developers/pricing, read 2026-10-10).

### 2c. Per-tier quota table (what the money buys for harness coding)

| $/mo | Tier | Best coding model via sub | Published quota shape |
| --- | --- | --- | --- |
| 8 | ChatGPT Go | GPT-6 Luna (desktop only) | Small; Free/Go excluded from 6.1-Sol rollout |
| 10 | OpenCode Go (baseline, being dropped) | GLM-5.3-Flash class | Per-model monthly $ caps ($60 GLM-Flash etc.; see `docs/research/opencode-go-models-2026-09.md`) |
| 20 | ChatGPT Plus | GPT-6.1 Sol | 15–160 local msgs/5h + weekly limits; Luna 350–3,000/5h; credits extend |
| 30 | SuperGrok | Grok 4.7 (Grok 4.6 named on pricing page; 4.7 latest per docs) | Undisclosed weekly pool shared across Chat/Build/Bot/Imagine/Voice; credits extend |
| 100 | ChatGPT Pro ($100 plan) | GPT-6.1 Sol + Astra | **No 5-hour limit**; weekly allowance; credits extend |
| 100 | SuperGrok Plus | Grok 4.7 | Larger undisclosed weekly pool; priority access |
| 200/500 | ChatGPT Pro ($200/$500) | Same + Ultrafast ($500 only) | Larger allowances; Ultrafast 8x burn |
| 300 | SuperGrok Heavy (price UNVERIFIED) | Grok 4.7 (+ multi-agent Heavy config per third parties — UNVERIFIED) | Largest undisclosed pool; dedicated support per x.ai/bot |

API $/M (short context, standard; for quota intuition, not billed on subs):
OpenAI — Astra $10/$50, 6.1-Sol $2/$10, 6-Sol $2/$10, 6-Luna $0.10/$0.50,
5.6-Sol $4/$20, 5.6-Terra $2/$12, 5.6-Luna $0.20/$1.20
(https://developers.openai.com/api/docs/pricing, read 2026-10-10; GPT-6 gen is
cheaper than GPT-5.6 gen at every tier).
xAI — grok-4.7/4.6 $2/$6 (<200k prompt; $4/$12 above), grok-4.5 $2/$6,
grok-4.3 $1.25/$2.50, grok-build-0.1 $1/$2
(https://docs.x.ai/developers/pricing, read 2026-10-10).

## 3. Intelligence per model (coding-relevant, primary leaderboards)

AA = Artificial Analysis Intelligence Index v4.3.2 (10 evals incl. Terminal-Bench
4.0; max-effort variant shown). TB4.0 = AA's independent Terminal-Bench 4.0 run
(mini-swe-agent, pass@1 ×3). Arenas scraped 2026-10-10 via headless Chromium
(WebDev Overall Oct 8 2026, 852,934 votes, 142 models; Text Overall Oct 8 2026,
8.73M votes, 414 models; DesignArena Overall Frontend Text-to-HTML same session).

| Model | AA Index (max effort) | TB 4.0 | WebDev Arena | Text Arena | DesignArena overall | API $/M in/out |
| --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 5.5 (ref; kept sub) | **58** #1/227, $5.98/task, 97 tok/s (https://artificialanalysis.ai/models/claude-opus-5-5) | 59.6% Max/Xhigh (AA eval page) | **#1** 1813 (max) | #2 1507 (high) / #14 1489 (max) | **#1** 1406 | $4/$20 (AA page) |
| Claude Sonnet 5.5 (ref) | **56** (AA eval page headline) | **63.6%** Max (AA eval page, top of board) | #3 1774 (xhigh) | #32 1476 (xhigh) | listed 1312 (Sonnet 5.5) | $2/$10 (arena listing) |
| GPT-6 Astra (max) | **53** #7/227, $3.26/task, 46.9 tok/s (https://artificialanalysis.ai/models/gpt-6-astra) | 59.6% xhigh Sept-vintage (see `docs/research/openai-codex-models-2026-09.md`; fresh per-model TB UNVERIFIED) | #2 1786 | #35 1475 | #2 1385 (xhigh) | $10/$50 |
| GPT-6.1 Sol (max) | **52** #11/227, $0.72/task, 55.6 tok/s (https://artificialanalysis.ai/models/gpt-6-1-sol) | UNVERIFIED per-model | #4 1755 | #21 1484 | GP-board #25 1288 | $2/$10 |
| GPT-6 Sol (max) | **48** #25/227, $1.04/task, 93.5 tok/s (https://artificialanalysis.ai/models/gpt-6-sol) | UNVERIFIED per-model | #8 1688 | — (not in top 60 snapshot) | #19 1298 | $2/$10 |
| GPT-6 Luna (max) | **38** #8/180 class, $0.07/task, 136.9 tok/s (https://artificialanalysis.ai/models/gpt-6-luna) | UNVERIFIED per-model | #34 1581 | — | #43 1258 | $0.10/$0.50 |
| GPT-5.6 Sol (legacy ref) | 47 on v4.3 Sept-vintage (secondary: `docs/research/openai-codex-models-2026-09.md`) | UNVERIFIED fresh | #24 1618 (xhigh, codex-harness) | #20 1485 (xhigh) | #7 1347 (xhigh) | $4/$20 |
| Grok 4.7 (xhigh) | **46** #29/227, $3.74/task, 74.2 tok/s (https://artificialanalysis.ai/models/grok-4-7) | UNVERIFIED per-model | #15 1639 | — | GP-board #1 1345 | $2/$6 |
| Grok 4.6 (high) | **44** #36/227, $1.48/task, 59.5 tok/s (https://artificialanalysis.ai/models/grok-4-6; AA flags 4.6 deprecated, points to 4.7) | UNVERIFIED per-model | #25 1617 | — | #20 1294 | $2/$6 |
| Grok 4.5 | UNVERIFIED on AA this pass | UNVERIFIED | #39 1553 | #51 1466 | #23 1290 | $2/$6 |
| GLM-5.3-Flash (Go baseline ref) | **42**, $0.25/task, 57.5 tok/s (https://artificialanalysis.ai/models/glm-5-3-flash) | UNVERIFIED per-model | #26 1609 | #38 1475 | #25 1288 | $0.15/$0.50 (AA) — arena lists $0.06/$0.20, likely direct-vendor rate |
| Muse Spark 1.3 (dropping ref) | UNVERIFIED on AA this pass (48 on v4.3 Sept-vintage, secondary) | UNVERIFIED | #13 1657 (max) | #9 1494 (max) | #5 1358 (xhigh) / #6 1356 (max) | $1.25/$4.25 std (arena) |

Notes:

- SWE-bench Verified/Pro per-model scores: UNVERIFIED this pass (official board
  https://www.swebench.com/ is JS-rendered and was not scraped; AA no longer
  publishes standalone per-model SWE cells — see Gaps in prior dated docs).
- Frontend-quality context (the reason `openai-codex` was dropped: GPT-5.6 Luna
  DesignArena rank 48 in September): the gap has closed at the top end — Astra
  xhigh is now DesignArena #2 (1385) and GPT-5.6 Sol xhigh #7 (1347) — but Luna
  is still weak (GPT-6 Luna #43, 1258; GPT-5.6 Luna #53, 1241). A ChatGPT
  re-subscribe should therefore route design-sensitive work to Astra/6.1-Sol,
  never to Luna.
- Grok 4.7 leads DesignArena's General Purpose sub-board (1345) but trails the
  OpenAI flagships on WebDev Arena (#15, 1639 vs Astra #2 / 6.1-Sol #4) and AA
  Index (46 vs 52/53).
- Verbosity/cost-per-task (AA): 6.1-Sol $0.72/task is the cheapest path to
  Index-50+ intelligence measured; Astra costs 4.5x more per task ($3.26) for +1
  Index point; Grok 4.7 costs $3.74/task at Index 46 with 240M eval tokens (most
  verbose of the set).

## 4. Cost-vs-intelligence Pareto ($/mo vs best usable coding model + effective quota)

"Effective quota" uses published numbers where they exist; xAI publishes no
per-tier numbers, so its quota cells are qualitative (UNVERIFIED quantitatively).

| $/mo | Option | Best coding model (sub) | Intelligence signal | Effective quota |
| --- | --- | --- | --- | --- |
| 20 | ChatGPT Plus | GPT-6.1 Sol (AA 52; WebDev #4) | 52 | 15–160 msgs/5h, weekly limits, credits extend — published |
| 30 | SuperGrok | Grok 4.7 (AA 46; WebDev #15) | 46 | Undisclosed weekly pool shared with Bot/Imagine/Voice; credits extend |
| 100 | ChatGPT Pro $100 | GPT-6.1 Sol + Astra (AA 53; WebDev #2) | 53 | No 5h limit; larger weekly pool; credits extend — published |
| 100 | SuperGrok Plus | Grok 4.7 | 46 | Larger undisclosed pool; priority access |
| 200–500 | ChatGPT Pro $200/$500 | Same + Ultrafast ($500) | 53 | Largest published allowances |
| 300 | SuperGrok Heavy (price UNVERIFIED) | Grok 4.7 (+Heavy multi-agent — UNVERIFIED) | 46+? | Largest undisclosed pool |

Pareto reading (intelligence per dollar, verifiable quota):

- **Pareto-optimal: ChatGPT Plus $20** — cheapest entry to an Index-50+ coding
  model with published, harness-legible quotas (15–160 Sol msgs/5h; Luna
  350–3,000/5h for cheap roles).
- **Pareto-optimal: ChatGPT Pro $100** — removes the 5h cap entirely and adds
  Astra headroom for the hardest tasks; same price as SuperGrok Plus at higher
  measured intelligence (52/53 vs 46) with published quota mechanics.
- **SuperGrok $30 is strictly dominated on coding-intelligence-per-dollar**
  (46 < 52 at 1.5x the price, undisclosed quota). It becomes Pareto-optimal only
  if the decision values what ChatGPT cannot supply in-harness: the included
  always-on agent product (Grok Bot draws from the same weekly pool —
  sibling comparison), live X-data grounding (omp's X tools require xai creds),
  or a non-OpenAI second lineage with a different failure profile from Claude.
- SuperGrok Plus $100 vs Pro $100 is the same story at 5x the Plus/Pro-base
  outlay: pick Plus only for the Bot/X reasons, not for model intelligence.
- Heavy ($300 UNVERIFIED) cannot be placed on the frontier without a verified
  price or quota; at the reported price it is 15x Plus for the same base model.

## 5. Suitability per omp role (concrete model id + thinking level)

Conventions: ids are `<provider>/<model>` as omp recognises them. `openai-codex/gpt-6*`
and `xai-oauth/grok-*` ids follow the verified provider-prefix rules but the exact
model rows are UNVERIFIED until the provider is logged in — confirm with
`omp models openai-codex` / `omp models xai-oauth` post-login (then delete this
caveat). Verified-today fallbacks are given per row. Thinking levels use omp's
scale (`minimal|low|medium|high|xhigh|max`); catalog support observed today:
`opencode-go/grok-4.6` = minimal,low,medium,high,xhigh;
`opencode-go/gpt-6-luna` = low,medium,high,xhigh,max. Astra has no `none`/minimal
(OpenAI docs list low..max); Luna caps at Max, no Ultra.

Roles keep their current semantics: adversary/reviewer/advisor must be
non-Anthropic lineage with strong reasoning; scout/smol/tiny/commit want cheap,
fast, high-quota; code-worker/sonic do routine edits; research synthesises web
findings (omp supplies `web/parallel` retrieval underneath).

### Option A — ChatGPT subscription (`openai-codex` provider)

| Role | Proposed | Why |
| --- | --- | --- |
| adversary / reviewer / advisor | `openai-codex/gpt-6.1-sol:high` (fallback verified id: `openai-codex/gpt-5.6-sol:high`) | Non-Anthropic lineage; AA 52 near-Astra at 1/5 the API price; OpenAI's pick for repeated complex work. Escalate single hard reviews to Astra (next row). |
| hardest-review escape hatch | `openai-codex/gpt-6-astra:high` (Astra Extra High omitted on some plans — stay at high) | AA 53 / WebDev #2 / DesignArena #2; 5–45 msgs/5h on Plus is enough for rare deep reviews; on Pro $100 no 5h cap. |
| scout / smol / tiny / commit | `openai-codex/gpt-6-luna:low` (fallback verified id: `openai-codex/gpt-5.6-luna:low`) | 350–3,000 msgs/5h on Plus; 2.5/12.5 credits per 1M — the only cheap-role quota in either option that is published and ample. |
| code-worker / sonic | `openai-codex/gpt-6.1-sol:medium` | 15–160 msgs/5h on Plus; medium effort is the documented balance point; Fast mode (2.5x) available if latency binds. |
| research | `openai-codex/gpt-6-astra:medium` (bulk synthesis on `…/gpt-6.1-sol:medium`) | Strongest judgment for cross-source synthesis; retrieval rides omp `web/parallel`, so the model need not browse. |

Plus-vs-Pro note for Option A: on Plus $20 the 5h windows force discipline
(Sol for worker/adversary, Luna for cheap roles, Astra only as escape hatch);
on Pro $100 the 5h cap disappears and the whole table can shift one effort level
up without quota anxiety.

### Option B — SuperGrok subscription (`xai-oauth` provider)

| Role | Proposed | Why |
| --- | --- | --- |
| adversary / reviewer / advisor | `xai-oauth/grok-4.7:high` (working-today fallback, dies with Go: `opencode-go/grok-4.6:high`) | Non-Anthropic lineage; Grok 4.7 xhigh is xAI's strongest measured (AA 46, WebDev #15); the only strong-reasoning non-Claude sub option besides OpenAI. |
| scout / smol / tiny / commit | `xai-oauth/grok-4.7:low` | xAI fields no cheap tier (all Grok 4.x $2/$6 API; no Lite-model price break published), so cheap roles run the same model at `low` effort and short outputs — and every token comes out of the same undisclosed weekly pool. This is the option's weakest cell: no Luna equivalent exists. |
| code-worker / sonic | `xai-oauth/grok-4.7:medium` (alt: `xai-oauth/grok-build-0.1:medium` if the oauth catalog carries it — UNVERIFIED; `grok-build-0.1` exists on the `xai` API-key provider at $1/$2) | 4.7 for general edits; build-0.1 (256k ctx, cheapest xAI coding model) would be the natural worker if exposed to oauth. |
| research | `xai-oauth/grok-4.7:high` | Best xAI synthesizer plus the option's unique edge: live X grounding (omp X tools require xai creds) and real-time web/X search lineage. |

Structural warning for Option B: one model at three efforts means adversary,
worker, and cheap roles all draw from one undisclosed weekly pool across Chat,
Build, and Bot. If Grok Bot (sibling comparison) also runs on the subscription,
Bot usage and harness usage compete for the same pool — size the tier (Plus vs
Heavy) against that combined burn, which cannot be estimated from published
numbers.

## 6. Recommendation (coding-harness view only)

- For pure cost-vs-intelligence in omp: **ChatGPT Plus $20** (verify 6.1-Sol rows
  post-login; 5.6-Sol/Luna ids as verified fallbacks). It restores a published,
  ample cheap-role quota (Luna 350–3,000/5h) that neither SuperGrok nor the
  outgoing Go setup matches with a same-vendor model, and puts an Index-52
  non-Claude reviewer behind every Claude plan. Upgrade to Pro $100 only if the
  5h windows bind or Astra is needed routinely.
- Choose **SuperGrok $30** instead only if the agent-product comparison (sibling)
  favours Grok Bot strongly enough to accept: lower measured coding intelligence
  (46 vs 52), an undisclosed weekly pool shared with the Bot, and no cheap-tier
  model for scout/smol/tiny/commit. Its genuine harness edges are X-grounded
  research and lineage diversity from both Claude and OpenAI.
- Either way, keep design-sensitive generation off Luna-class models (fresh
  DesignArena: Luna #43/53; Astra xhigh #2) and keep Claude Opus 5.5 for
  default/plan/task (AA 58, WebDev #1, DesignArena #1).

## Gaps (UNVERIFIED, in priority order)

1. Exact `openai-codex/gpt-6.1-sol|gpt-6-sol|gpt-6-luna|gpt-6-astra` rows and their
   omp thinking-level support — provider logged out; one `omp models openai-codex`
   after login closes it.
2. Exact `xai-oauth/*` chat-model rows (4.7? 4.6? build-0.1?) and thinking levels —
   one `omp models xai-oauth` after login closes it.
3. SuperGrok Lite/Heavy prices and any numeric per-tier weekly allowances —
   grok.com is Cloudflare/bot-gated; needs a logged-in browser session or sibling
   follow-up, not fetchable here.
4. Per-model SWE-bench Verified/Pro and Terminal-Bench 2.x numbers for GPT-6.1-Sol,
   GPT-6-Sol/Luna, Grok 4.6/4.7 — official boards are JS-rendered and were not
   scraped this pass; AA's TB4.0 cells likewise need a JS scrape per model.
5. Whether `xai-oauth` traffic counts 1:1 against the SuperGrok weekly pool or has
   separate agent-API metering — no primary statement found; meter in practice.

## Sources (all read 2026-10-10)

- https://learn.chatgpt.com/docs/pricing — plans ($8/$20/$100–$500), 5h estimates, credit rates, Fast/Ultrafast multipliers, overage/credits.
- https://learn.chatgpt.com/docs/models — 6.1-Sol rollout, effort scale (Light→Ultra, Luna⊄Ultra), Astra capability, retirements (5.5 on 2026-10-14, Spark 2026-09-14, 5.4 on 2026-08-31).
- https://developers.openai.com/api/docs/pricing — API $/M table (short/long context, batch/flex/fast/ultrafast).
- https://x.ai/pricing — SuperGrok $30 / Plus $100, tier names, feature bullets.
- https://x.ai/bot — Grok Bot availability (SuperGrok/Plus/Heavy), weekly usage included, Heavy positioning.
- https://docs.x.ai/grok/overview — shared weekly allowance statement.
- https://docs.x.ai/grok/faq — weekly pool mechanics, Extra Usage Credits ($5+, 1-yr expiry), Auto Top Up, subscription management.
- https://docs.x.ai/build/overview — Grok Build CLI/TUI/ACP, browser-first auth, grok-4.7 latest.
- https://docs.x.ai/developers/pricing — xAI API $/M (4.7/4.6/4.5/4.3/build-0.1), 4.7-Fast (Cursor/Build only), priority/batch/regional pricing.
- https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index — v4.3.2 composition; Opus 5.5 Max 58 / Sonnet 5.5 Max 56 headlines.
- https://artificialanalysis.ai/evaluations/terminalbench-4-0 — TB4.0 method; Sonnet 5.5 Max 63.6% / Opus 5.5 59.6% headlines.
- https://artificialanalysis.ai/models/gpt-6-astra — Astra Max 53, $3.26/task, 46.9 tok/s.
- https://artificialanalysis.ai/models/gpt-6-1-sol — 6.1-Sol Max 52, $0.72/task, 55.6 tok/s.
- https://artificialanalysis.ai/models/gpt-6-sol — 6-Sol Max 48, $1.04/task, 93.5 tok/s.
- https://artificialanalysis.ai/models/gpt-6-luna — 6-Luna Max 38, $0.07/task, 136.9 tok/s.
- https://artificialanalysis.ai/models/grok-4-7 — 4.7 Xhigh 46, $3.74/task, 74.2 tok/s.
- https://artificialanalysis.ai/models/grok-4-6 — 4.6 High 44, $1.48/task, 59.5 tok/s, deprecated→4.7.
- https://artificialanalysis.ai/models/glm-5-3-flash — Flash 42, $0.25/task, 57.5 tok/s.
- https://artificialanalysis.ai/models/claude-opus-5-5 — Opus 5.5 Max 58, $5.98/task, 97 tok/s.
- https://arena.ai/leaderboard/code/webdev — WebDev Overall snapshot Oct 8 2026 (headless Chromium).
- https://arena.ai/leaderboard/text — Text Overall snapshot Oct 8 2026 (headless Chromium).
- https://www.designarena.ai/leaderboard/code — Overall Frontend + General Purpose snapshot Oct 10 2026 (headless Chromium).
- Local: `omp --help`, `omp models [--kind all] [openai-codex|xai]`, `omp models find codex`,
  `omp login`, `omp auth-broker list`, `omp usage`, `omp/config.yml`
  (`disabledProviders: [openai-codex]`), `~/.omp/agent/models.db` (`model_cache`),
  binary strings of `/home/sudaksh/.local/bin/omp` (provider ids, oauth module,
  billing host, model-id prefixes).
- Secondary/context only (clearly flagged where used): `docs/research/openai-codex-models-2026-09.md`
  (Sept-vintage 5.6-family AA/Coding-Index numbers, retired Spark/5.4 details),
  `docs/research/opencode-go-models-2026-09.md` (Go $10 caps, effort mappings),
  `docs/research/designarena-2026-09.md` (Sept DesignArena baseline incl. Luna rank 48),
  `docs/research/harness-provider-access-2026-09.md` (prior probe method + openai-codex removal note).
