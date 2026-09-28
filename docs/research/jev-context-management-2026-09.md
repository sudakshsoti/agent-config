# Jev (TypeSafe System One) — identity, quota, and use in OMP / Claude Code (2026-09-28)

All pages read 2026-09-28 unless noted. Every claim carries its source URL or a
local probe transcript. "Not listed / not found" means absent on that date, not zero.
Marking: anything not directly observed is tagged **[INFERENCE]**.

## Summary

- **Jev 1.13 is not a chat model.** It is TypeSafe AI's "System One" structured-decision
  model: unstructured `state` in, typed probabilistic decisions out (`noul` yes/no,
  `choice`, `score`). It generates no text and, by construction, cannot hallucinate
  strings. Sources: https://typesafe.ai/blog/introducing-system-one-models-and-jev,
  https://docs.typesafe.ai/introduction.
- **Jev cannot do context compaction or summarization.** Compaction is a text-generation
  task; Jev has no string output. Both local probes confirm it is unreachable as a chat
  model from OMP (see §Probes).
- **Jev is a Zen model, not a Go model.** It lives under the `opencode-zen` provider as
  `jev-1.13` / `jev-1.13-free` (own endpoint `https://opencode.ai/zen/v1/systemone`),
  and is **absent from the Go model/usage-limit tables** — so it draws on neither the
  $60/month GLM cap nor any Go pool. It bills to the Zen pay-as-you-go balance:
  **$0.042 / 1M input tokens, output free**. Source: https://opencode.ai/docs/zen/
  (Endpoints, Jev, Pricing); https://opencode.ai/docs/go (no Jev row, read 2026-09-28).
- Realistic uses are **decision gates around** the context pipeline, not the pipeline
  itself: permission auto-approval (documented recipe for OpenCode, Claude Code, Codex,
  Cursor), routers/triagers, and judges/verifiers. Source:
  https://openrouter.ai/docs/cookbook/coding-agents/auto-approve-permission-prompts-with-jev.
- Privacy: Zen docs state all Zen models are US-hosted, zero-retention, no training,
  with a named exception list that **does not include paid `jev-1.13`**; `jev-1.13-free`
  gets only a "limited time" note with no data-use statement — treat the free tier as
  unverified. Source: https://opencode.ai/docs/zen/ (Privacy).

## 1. What Jev is

- Vendor/release: TypeSafe AI, founded by Diogo Almeida (ex-OpenAI, RLHF/ChatGPT
  methods work); Jev announced **Sep 15, 2026**, early access. "System One" is a nod to
  Kahneman's fast System 1 thinking; "Jev" to William Stanley Jevons.
  Source: https://typesafe.ai/blog/introducing-system-one-models-and-jev.
- Architecture/training: new stack with "Reinforcement Learning for Calibrated
  Decisions (RLCD)"; parallel (non-autoregressive) sampler; outputs are type-safe
  structured values with calibrated probabilities/confidence. Claimed 70–500 ms
  end-to-end latency, ~40–200x faster than frontier LLMs on "System One shaped"
  queries. Source: same blog post.
- API primitives (https://docs.typesafe.ai/introduction): three question types,
  mixable in one call, evaluated in parallel against the same `state` —
  `Choice` (pick from list → `choice`, `probabilities`, `confidence`),
  `Score` (numeric → `score`, `confidence`), `Noul` (yes/no → probability).
- Limits: **64,000-token context, 0 output limit** (no reasoning, no tool calls,
  structured-output capable) per the models.dev Jev page, whose OpenCode Zen rows read
  `jev-1.13` 64K @ $0.04/$0.00 and `jev-1.13-free` 64K @ $0.00/$0.00.
  Source: https://models.dev/models/typesafe/jev-latest (read 2026-09-28; third-party
  catalog, not vendor). `omp models` shows `-` across both Jev rows (no catalog data)
  and https://opencode.ai/data/unknown/jev-1-13 reports Context **Unknown**. Rate
  limits and max state size remain unverified. Jev supports up to 255-cardinality
  choices via two-stage scoring (blog "Wikiracing" nuance).
- Adoption signal only: OpenCode usage-data page ranks `jev-1.13` **#37** (~9.7B tokens,
  10K users, 247K sessions, $0.00 spend — i.e. overwhelmingly the free tier).
  Source: https://opencode.ai/data/unknown/jev-1-13.

## 2. Quota / pricing: which pool it draws on

- **Not Go.** The Go usage-limit and estimated-request tables (read 2026-09-28) contain
  no Jev row; Go endpoints are `/v1/chat/completions`, `/v1/responses`, `/v1/messages`
  only. Jev's endpoint is `https://opencode.ai/zen/v1/systemone` with no AI-SDK package.
  Source: https://opencode.ai/docs/go, https://opencode.ai/docs/zen/ (Endpoints).
 - **Zen pay-as-you-go:** `Jev 1.13` $0.042 input / Free output / no cached-read column;
  `Jev 1.13 Free` Free/Free (limited time). The Zen console Models tab renders these as
  `$0.04` in / `$0.00` out and `$0.00` / `$0.00` (display rounding), text-only modality,
  with both toggles **ON** in workspace `wrk_01KZ1J1X89JE8SVAASS798JH71` — user-supplied
  OpenCode console screenshot, 2026-09-28 — confirming workspace model-access
  enablement per the Zen "Model access" admin control. Zen bills per request against
  workspace balance (auto-reload $20 when below $5; optional monthly caps).
  Source: https://opencode.ai/docs/zen/ (Pricing, Auto-reload, Monthly limits).
- Worked example from the primary recipe: a 400-token state cost **$0.0000168**
  (captured 2026-09-21). At that size, $1 buys ~60K decisions.
  Source: OpenRouter cookbook §3.
- Consequence for this repo's routing: Jev spend touches **neither** the Go $60/month
  GLM cap **nor** the Muse Code subscription window **nor** the Anthropic plan — it is
  a third, micropayment pool. **[INFERENCE]**: at ~$0.000017/decision it is ~2 orders
  of magnitude cheaper per call than any chat-model gate, which is exactly why the
  permission-approval use case fits.

## 3. Probes (local, 2026-09-28, omp 18.3.5)

1. `omp models` — Jev appears **only** under `opencode-zen (109)`:
   `jev-1.13` and `jev-1.13-free`, both `-` context / `-` max-out / `-` thinking /
   no-images. There is no `opencode-go/jev-*`.
2. `omp -p --model opencode-go/jev-1.13 …` → `Model "opencode-go/jev-1.13" not found`
   (wrong provider; expected).
3. `omp -p --model opencode-zen/jev-1.13-free …` (retry disabled) → **
   `403 OpenCode's free tier can only be used from within OpenCode
   (type=FreeTierError)`**. The free tier is fenced to the OpenCode client; OMP
   cannot use it regardless of config.
4. `omp -p --model opencode-zen/jev-1.13 …` (retry disabled) → **
   `400 Model does not support this protocol. (type=ModelProtocolUnsupported)`**.
   OMP sends a chat session; Jev speaks only the SystemOne Decisions protocol, so no
   role, agent, `smol`, or `compaction.remoteEndpoint` setting can route chat traffic
   to it. An `opencode-zen/jev-1.13:low`-style selector would fail the same way
   **[INFERENCE — same protocol mismatch]**.
 5. `omp -p --model opencode/jev-1.13 …` (retry disabled) → `Model
   "opencode/jev-1.13" not found`. OMP exposes **no `opencode` provider** (provider
   list: `anthropic`, `muse-code`, `opencode-go`, `opencode-zen`, `openrouter`);
   the `opencode/<model-id>` form is OpenCode-client config syntax
   (https://opencode.ai/docs/zen/), while OMP addresses the same Zen back end as
   `opencode-zen/<model-id>`.

## 4. Using Jev in OMP for context compaction/management

Short answer: **Jev cannot be the summarizer.** OMP compaction's LLM-backed methods
all need generated text:

- Method chain (`omp://compaction.md`, also `omp config list`): `remote` =
  provider-native server compaction (OpenAI Responses `/compact`, Anthropic
  `compact-2026-01-12` beta — same-model session only); `snapcompact` = local
  deterministic bitmap archival (no model at all); `handoff`/`soft` = LLM summary via
  the live session's model pipeline (`completeSimple` oneshot). Local override in this
  checkout is `methodOrder: [snapcompact, remote, soft]`.
- `compaction.remoteEndpoint` accepts only two wire shapes: a custom omp summarizer
  (`{systemPrompt, prompt}` → `{summary}`) or an OpenAI-compatible
  `/chat/completions` endpoint (`{model, messages}` → `choices[0].message.content`).
  Jev's `/v1/systemone` `{model, state, questions}` → `{answers}` shape matches
  neither, and the probe proves the gateway rejects chat-protocol calls to Jev.
- Triggers/thresholds worth knowing when tuning instead: `compaction.thresholdPercent`
  / `thresholdTokens` (`-1` = reserve-based default), `keepRecentTokens` (20000),
  `midTurnEnabled`, `asyncEnabled` (speculative background summarization),
  `task.agentCompactionThresholdOverrides`, plus `session_before_compact` /
  `session.compacting` / `session_compact` extension hooks
  (`session_before_compact` may cancel or supply a full custom compaction payload).
  Source: `omp://compaction.md`, `omp://settings.md` (§context-compaction-and-memory).

What Jev *can* do around OMP context management (all **[INFERENCE]**, none
implemented here):

- **Pre-compaction triage via `session_before_compact`**: an extension could POST
  candidate regions (e.g. "is this tool result referenced later?") to the SystemOne
  endpoint as `noul` questions and prune/protect regions before the real summarizer
  runs. Cheap (fractions of a cent per compaction) and off the chat-model path.
- **Memory/sharpening judge**: `score`/`noul` over candidate notebook entries
  (`context_notes` experimental mode) or `memories` rollouts — "does this fact still
  hold / is it load-bearing?" — with the threshold, not a prompt, as the bar.
- **Exact config snippet** (compaction tuning only — Jev appears nowhere in it;
  do not add a Jev rung to any role/chain, it fails closed per probe 4):

```yaml
compaction:
  methodOrder: [snapcompact, remote, soft]
  thresholdPercent: 80
  keepRecentTokens: 20000
```

## 5. Using Jev in Claude Code

Claude Code compaction is internal to Anthropic models and Jev cannot participate in
it — same protocol reason as OMP. Realistic options, strongest first:

1. **PermissionRequest hook auto-approval (documented recipe).** Claude Code runs
   `PermissionRequest` hooks only when it is about to prompt; the hook reads
   `{cwd, tool_name, tool_input.command, tool_input.description}` on stdin and prints
   `{"hookSpecificOutput": {"hookEventName": "PermissionRequest",
   "decision": {"behavior": "allow"}}}` for one-shot approval, else exits 0 silently
   (prompt appears as before). Static `RISKY` denylist is evaluated *before* Jev and
   is the security boundary; Jev answers `reversible` + `serves_task` nouls at
   threshold 0.9; deny rules in settings still win over hook allow. Register in
   `.claude/settings.json` with `matcher: Bash`, `timeout: 15`. Full code:
   OpenRouter cookbook §§1–3 + "Auto-approve Claude Code permission prompts".
   Note the cookbook's Codex caveat (hook env may lack `OPENROUTER_API_KEY`;
   project `.env` workaround) — verify env inheritance on this machine before
   relying on it **[INFERENCE — environment-specific]**.
2. **`/compact [instructions]` custom instructions.** The `/compact` command accepts
   free-text focus instructions that the summarizer turns into structured sections
   (anthropics/claude-code#13572). Jev cannot write these, but a `choice` call could
   *select* which canned focus template to pass — marginal value, listed for
   completeness.
3. **PreCompact hook: persist state, not summarize.** `PreCompact` fires before
   compaction, `PostCompact` after (hook lifecycle: code.claude.com/docs/en/hooks).
   A hook cannot replace the summarizer; it can snapshot working state to disk/memory
   so a lossy summary stays recoverable. Jev's role, if any: score *what* to snapshot.
4. **External summarizer via `ANTHROPIC_BASE_URL` proxy to a chat model: not Jev,
   and risky.** Pointing Claude Code at a third-party Anthropic-compatible endpoint
   breaks the subscription path — cf. this repo's own evidence that the Anthropic
   subscription rejects third-party clients with HTTP 400 "Third-party apps now draw
   from your extra usage" (`docs/research/harness-provider-access-2026-09.md`).
   Do not route a Claude Code session at Jev or any proxy expecting chat; it fails
   the same way probe 4 did.

## 6. Other use cases fitting this repo's routing

| Use case | Jev primitive | Fit vs current routing |
|---|---|---|
| Shell-permission auto-approval (OMP `--hook`/extension, Pi hooks) | 2× `noul` @ 0.9 | Best fit; documented recipe + `jevvy` OpenCode plugin precedent. Offloads the highest-frequency interruption class from every role at ~$0.00002/decision on the Zen micropayment pool. |
| Subagent/task triage + routing (scout → worker) | `choice` over labels | Good fit; replaces a `smol`-class chat call (GLM Go cap) with a faster/cheaper specialized call. Keeping `scout` on GLM preserves zero-retention for discovery; Jev sees only the routed state. |
| Reviewer second-opinion / policy gates (reviewer, security-reviewer, commit) | `noul` ("contains secret?", "reversible?", "serves task?") | Good fit as a *first-pass filter*, not a replacement: Jev returns probabilities, never rationale or patches. Keep the GLM second-lineage pass for anything needing text. |
| Verdict/judge over LLM outputs (advisor notes, ttsr judge) | `score` + confidence | Plausible; calibrated confidence is Jev's differentiator vs asking a chat model "how confident are you". Unproven against this repo's workloads. |
 | Map-reduce over big logs/session history | batched `noul`/`score` | Vendor's stated sweet spot (parallel eval, no context-rot across questions). Bounded by the 64K context (models.dev) — chunk state accordingly; rate limits still unverified. |
| Anything needing text out (summaries, commit messages, code, reviews) | — | **No fit.** Route stays: `smol`/`tiny`/`commit` → GLM 5.3 Flash (Go cap); mechanical → Muse Spark Contributor; decisions/judgment → Opus/Sonnet per AGENTS.md. |

Tradeoff summary: Jev wins on **cost/latency per binary decision** and loses on
**generality** (no text) and **quota isolation complexity** (third pool on Zen
balance with auto-reload — set a workspace monthly cap). It complements, never
replaces, the GLM↔Muse↔Claude ladder in AGENTS.md.

## 7. Data / training policy for the Jev tier

- Zen Privacy (https://opencode.ai/docs/zen/, read 2026-09-28): "All our models are
  hosted in the US. Our providers follow a zero-retention policy and do not use your
  data for model training, **with the following exceptions**" — the exception list
  (free-period models, OpenAI/Anthropic 30-day retention, Muse Contributor training)
  **does not name paid `jev-1.13`**, so paid Jev is covered by the zero-retention /
  no-training statement as written.
 - `jev-1.13-free` is listed only as "available on OpenCode for a limited time" with
  **no data-use sentence** — unlike sibling free rows that explicitly state
  zero-retention (Space Bunny, LongCat 2.5) or training use (Big Pickle, MiMo frees).
  House pattern matters here: Zen's convention is that free-period models carry an
  explicit "During its free period, collected data may be used to improve the model"
  exception (see quoted Privacy section in
  https://github.com/anomalyco/opencode/issues/7479), and community reports describe
  free models as "offered for free in exchange for your usage data … probably used to
  train or improve models" (same issue — non-authoritative, not OpenCode staff).
  Jev Free currently has neither an exception nor a clearance: treat it as
  **likely training-eligible until stated otherwise** — do not send client/sensitive
  material through it **[INFERENCE — caution, not evidence]**.
- Either way, Jev-bound state is a *selected excerpt* (commands + task text), never the
  full session — structurally less exposure than routing a session to a chat model.
  For sensitive sessions, paid tier + minimal state + workspace monthly cap is the
  defensible combination **[INFERENCE — recommendation]**.

## Gaps

 - Rate limits and max state size: unverified (models.dev gives 64K context but no
  state-size or rate-limit figures). Verify at https://docs.typesafe.ai/ before
  building map-reduce or large-state triage.
 - Whether Zen-side `jev-1.13` honors the same zero-retention terms TypeSafe offers
  direct customers: unverified beyond the Zen Privacy paragraph quoted above.
 - No probe of the SystemOne endpoint itself was possible (needs `OPENCODE_API_KEY`
  with Zen balance; the `jev-1.13-free` 403 shows this checkout's key path cannot
  reach even the free tier outside OpenCode). The paid-tier curl in the Zen docs'
  Jev section is the reference call.
 - OMP `session_before_compact` extension sketch and Claude Code hook wiring are
  designs, not implementations — no code was added (out of scope for research).

## Sources

- https://typesafe.ai/blog/introducing-system-one-models-and-jev — vendor announcement,
  identity, speed/cost claims, use cases (read 2026-09-28).
- https://docs.typesafe.ai/introduction — primitives (Choice/Score/Noul), parallel eval,
  atomic-question guidance (read 2026-09-28).
- https://opencode.ai/docs/zen/ — Endpoints (incl. `/v1/systemone`), Jev section with
  curl reference, Pricing ($0.042/M in, free out; free tier), Privacy, pay-as-you-go
  mechanics (read 2026-09-28).
- https://opencode.ai/docs/go — Go model/usage-limit/endpoint tables; Jev absent
  (read 2026-09-28).
- https://openrouter.ai/docs/cookbook/coding-agents/auto-approve-permission-prompts-with-jev —
  shared risk-list + Jev approval design, captured scores/costs, OpenCode plugin,
  Claude Code / Codex / Cursor hook wiring (read 2026-09-28).
- https://openrouter.ai/typesafe/jev-1.13 — model listing, price meta (read 2026-09-28).
- https://opencode.ai/data/unknown/jev-1-13 — usage rank/volume, Unknown context
  (read 2026-09-28).
- https://code.claude.com/docs/en/hooks — PreCompact/PostCompact/PermissionRequest
  lifecycle (read 2026-09-28).
- `omp://compaction.md`, `omp://settings.md` — OMP compaction methods, remoteEndpoint
  wire formats, hooks, thresholds (read 2026-09-28 via harness docs).
- `docs/research/harness-provider-access-2026-09.md` — Anthropic subscription rejects
  third-party clients (HTTP 400 extra-usage rule).
- `docs/research/opencode-go-models-2026-09.md` — Go caps/pools baseline (2026-09-16).
 - Local probes: `omp models` (jev under `opencode-zen` only; no `opencode` provider
  exists in OMP); five retry-disabled `omp -p` probes — `opencode-go/jev-1.13` and
  `opencode/jev-1.13` not found, `opencode-zen/jev-1.13-free` 403 FreeTierError,
  `opencode-zen/jev-1.13` 400 ModelProtocolUnsupported (2026-09-28, omp 18.3.5).
 - https://models.dev/models/typesafe/jev-latest — 64K context / 0 output, Zen rows
  `jev-1.13` $0.04/$0.00 and `jev-1.13-free` $0.00/$0.00 (third-party catalog, read
  2026-09-28).
 - https://github.com/anomalyco/opencode/issues/7479 — Zen free-model data-use
  convention ("During its free period, collected data may be used to improve the
  model") plus non-authoritative community reports (read 2026-09-28).
 - User-supplied OpenCode console screenshot, 2026-09-28
  (`opencode.ai/console/wrk_01KZ1J1X89JE8SVAASS798JH71/models`) — Jev 1.13 $0.04 in /
  $0.00 out, Jev 1.13 Free $0.00/$0.00, text-only modality, both workspace toggles ON.
