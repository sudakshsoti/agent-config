# Jev-based compaction plugins: effective or gimmick? (2026-09-28)

Builds on `docs/research/jev-context-management-2026-09.md` (Jev identity, quota,
probes — not repeated here except where load-bearing). All repo reads, probes, and
issue checks done 2026-09-28 unless noted. Anything not directly observed is tagged
**[INFERENCE]**.

## Verdict up front

**Effective mechanism, narrow job — not a gimmick, but not a replacement for
built-in compaction either.** The three plugins do one thing well: use Jev's
`noul` decisions to *extractively* prune stale tool outputs while leaving every
word of user/assistant text verbatim. On a real session from this machine I
measured **54.1% character reduction for $0.000268 and 1.3 s** (§8), and an
independent recall probe at **75% recall with 0 permanent losses** (§8) —
squarely inside the authors' claimed 63–75%. The mechanism is real and the
numbers reproduce.

But "compaction" here means something much smaller than what OMP / Pi / Claude
Code mean by it:

- Jev **cannot summarize** (no text output — see the companion note §1). It only
  votes keep/drop on tool calls and results. Anything text-heavy compresses **0%**.
- What it removes, your built-ins already attack cheaper: OMP's `shake` prunes
  tool output mechanically with no network call, and `snapcompact` archives the
  region **verbatim** (deterministic, no model, no recall loss).
- Its costs land exactly where this setup is most sensitive: **prompt-cache
  invalidation** on an Opus-5 main model, plus a third-party data hop per pass.

**Recommendation for this setup (OMP 18.3.5, `methodOrder: [snapcompact,
remote, soft]`, threshold 70%, Opus-5 main): do not install any of the three.**
The current chain already covers both failure modes Jev addresses (stale tool
output via `shake`; full-region archiving via verbatim `snapcompact`; semantic
compression via server-side/LLM summary). Revisit only if tool-output-heavy
sessions routinely overflow *despite* shake — and then trial the OMP plugin's
continuous `context` path on OpenRouter with spill on, threshold 0.2, call
records kept, while watching cache-hit rates. Details in §10.

## 1. What the three plugins actually do

All three share one core (`tamaratran/fast-jev-compaction`, vendored/ported into
the other two) and one algorithm:

1. Pair every `tool_use` with its `tool_result` by id. Pin the first message and
   the newest N messages (default 6) — never touched.
   Source: `fast-jev` README "How it works" §§1–2 (cloned 2026-09-28).
2. Build a `state` = whole conversation, oldest first, with every tool result
   replaced by a short note (`ok, 4213 chars (omitted)`). Fit it into
   `maxStateTokens` (default 25k) in escalating stages: truncate tool inputs
   (1000→200→60 chars), abridge long texts head+tail oldest-first, collapse old
   messages to `[… N chars omitted …]`, shrink old calls to one line, drop old
   call-less messages. Tokens are *estimated* from character counts (no
   tokenizer), calibrated to land above Jev's reported counts.
   Source: same README §§2–3.
3. Ask Jev **two `noul` questions per non-pinned call**: should the *call* stay
   (knowing it happened still matters), should the *result* stay verbatim
   (contents still needed, re-running won't do). Batch into as many requests as
   needed to stay under `maxRequestTokens` (default 30k, under Jev's 32k request
   limit); the full state is resent with every request.
   Source: same README §§4–5; `src/compact.ts` `questionsFor`, `batchCalls` (read).
4. Decide per call against `keepThreshold` (0.5 default upstream): keep both /
   keep call + truncate result to `truncateHeadChars` (300) + note / drop call
   with result. Rebuild the message list; never leave a result without its call.
   Source: same README §6.

Integration differs per host:

| Plugin | Host integration | Default posture |
|---|---|---|
| `tamaratran/fast-jev-compaction` 0.2.0 | Claude Code **function hook** (`session.compact` transcript → pruned messages; falls back to built-in summary on error or reduction < `minReductionRatio` 0.25). Also a `turn.complete` hook that requests compaction at 60% context | Opt-in via plugin install + `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1` |
| `jerryfane/omp-jev-compaction` 0.1.0 | OMP: (a) per-request **`context`** reduction (session on disk untouched; one bad call costs one turn), on by default after `omp plugin install`, threshold **0.2**, 150k-char floor; (b) **`session_before_compact`** replacing the compaction summary with verbatim retained history when savings ≥ `minReduction` 0.25 | On-by-default after install; `OMP_JEV_CONTEXT=0` disables |
| `joelhooks/pi-fast-jev-compaction` | Pi 0.85.1 extension: proactive `turn_end` pruning at 60% context with 8k-token cooldown; decisions in append-only `fast-jev-decisions` ledger entries; filters only model-bound context, never rewrites JSONL; explicit XState machine `idle→deciding→applied\|fallback\|failed`; `/fast-jev` commands | `enabled` flag in `fastJevCompaction` settings |

Sources: `fast-jev` root + `hooks/README.md`; `omp-jev` README (full, cloned
2026-09-28); `pi-jev` README (full, cloned 2026-09-28).

Critical asymmetry the READMEs state plainly: in OMP, **omp prunes tool output
*before* `session_before_compact` runs**, so the region handed to the hook is
usually already `shake`-reduced to markers like `[shaken ~516 tokens —
recover: artifact://6]` or holds no tool calls at all — "the hook then declines
and omp compacts normally… the continuous `context` path is the one that pays."
Source: `omp-jev` README "The two integration points". In other words, on this
machine's config the OMP compaction-hook half is near-dead code by the author's
own account; only the per-request path does work.

## 2. Author-measured numbers (not independently verified except §8)

From `omp-jev` README + scripts (all author-measured, single-machine, small-N):

- **Reduction:** 53.6–55% byte reduction at thresholds 0.3/0.5/0.7 (byte-identical
  output across those thresholds); an earlier unsafe mode reached 96% by deleting
  63 of 66 steps — the reason safe mode (drop outputs, keep call records) is now
  default. At threshold 0.2 safe vs unsafe differ by <0.4 pts, "so the safety is
  nearly free."
- **Recall** (`scripts/recall.ts`, 8 planted facts, chat-model judge):
  full context 100% → reduced **63–75%**; with spill parking on, misses are
  recoverable: **0 permanent losses** across both thresholds tested.
- **Sticky prefix** (cache design, §5): replaying a real 16,198-message session,
  40 requests → **3 rewrites, 37 reuses** (one rewrite per 13.3 requests),
  **0 prefix breaks** across 39 checks.
- **Cache guard:** 14 live sessions — thirteen at 98–100% cache hits
  ($0.05–$0.40/req), one at 6% ($2.87). Replay skips the 13 cheap ones, reduces
  the full-price one: "protecting $1.81 per request round while capturing $2.61."
- **Jev cost/latency on OpenRouter:** ~430 ms per decision request, $0.0000198
  for 472 input tokens (≈ $0.042/M — matches the Zen price in the companion
  note). Per-pass cost "about $0.0005".
- **Live suite** (`tests/live.test.ts`, needs a key) asserts a genuinely stale
  40k-char read is dropped while every word of user text survives — i.e. the one
  end-to-end behavioral test is author-run, not in CI.

`fast-jev` and `pi-jev` publish no recall/reduction numbers of their own; `pi-jev`
records per-run `cacheRead`/`cacheWrite` token counts in ledger entries "so you
can compute cache-write deltas across runs and evaluate the tradeoff" — i.e. the
cache tradeoff is left to the operator to measure. Source: `pi-jev` README "Cost".

## 3. What the built-ins do (the comparison baseline)

**OMP 18.3.5** (this machine: `methodOrder: [snapcompact, remote, soft]`,
`thresholdPercent: 70`, `keepRecentTokens: 20000`, `asyncEnabled: true`;
observed via `omp config list --json`, 2026-09-28):

- `shake` — inline local reduction *before* any model call: replaces eligible
  tool results / large fenced blocks with recoverable `artifact://` references,
  protected recent window, minimum-savings threshold. No network, no model.
- `snapcompact` — local deterministic archival: discarded history serialized and
  printed onto model-aware PNG frames; persisted under
  `CompactionEntry.preserveData.snapcompact`; **verbatim**, no summarizer;
  rationale cites "200k-token evals in `packages/snapcompact` where bitmap
  frames preserved QA recall at lower billed-token cost than raw text."
- `remote` — provider-native server compaction (Anthropic `compact-2026-01-12`
  beta on supported lines incl. Opus 4.6+: same system prompt/tools/history, so
  **it reads the prompt cache the last turn wrote**; plain-text summary stored
  so later compactions by any provider can build on it) or OpenAI lanes.
- `soft`/`handoff` — LLM summary through the live session pipeline
  (`completeSimple` oneshot).
- Around all of it: pre-compaction `pruneToolOutputs` (protect newest 40k tool
  tokens, ≥20k savings required), `dropUseless` elision, `supersedeReads`
  blanking, speculative async compaction that hides summarization latency, and
  the `session_before_compact` / `session.compacting` / `session_compact` hook
  surface.
  Source: `omp://compaction.md` (read 2026-09-28).

**Pi 0.85.1** (`pi.dev/docs/latest/compaction`, read 2026-09-28): threshold =
`contextWindow − reserveTokens` (16,384 default); cut at `keepRecentTokens`
(default 20k); LLM structured summary (Goal / Constraints / Progress / Key
Decisions / Next Steps / Critical Context) with cumulative file lists; tool
results truncated to 2000 chars in summarizer input; "summarization requests
disable prompt-cache writes because these one-off prompts are unlikely to be
reused"; `session_before_compact` lets extensions cancel or supply the full
payload — the seam the Pi Jev extension uses as fallback.

**Claude Code 2.1.283** (`code.claude.com/docs/en/how-claude-code-works`,
`context-window`, `commands`; read 2026-09-28): auto-compaction "clears older
tool outputs first, then summarizes the conversation if needed. Your requests
and key code snippets are preserved"; `/compact [focus]` and CLAUDE.md "Compact
Instructions" steer what survives; `/autocompact [auto|<tokens>]` sets the
window; subagents keep research tool calls out of the main window entirely;
thrashing guard stops auto-compacting after a few attempts instead of looping.
`PreCompact`/`PostCompact` hooks can snapshot state but cannot replace the
summarizer (companion note §5).

Net: every built-in already does *lossy semantic compression of everything
including text* (summary) and/or *mechanical tool-output elision* (shake,
Claude's clear-outputs-first). Jev adds exactly one thing: **semantic judgment
over which tool outputs are stale, with verbatim retention of the rest.**

## 4. Head-to-head on the concrete axes

**Information retained (recall).** Jev wins *exactness*, loses *coverage*.
Kept regions are byte-verbatim — file paths, error codes, commands survive by
construction, whereas a summary can paraphrase them away. But dropped regions
are gone from context (25–37% question-recall loss in §2/§8), and Jev can only
ever vote on tool calls/results: a 100k-char text discussion compresses 0%.
Built-in summaries compress text too and carry structured sections plus
cumulative file lists; `snapcompact` keeps the region verbatim with no judgment
call at all. The spill-file mechanism (`~/.omp/jev-spill/<hash>.txt` + pointer
in the replacement text) converts permanent loss into "one `read` to recover" —
measured 0 permanent misses — but recovery depends on the agent noticing the
pointer and spending a tool call, which is unquantified **[INFERENCE]**.
Sources: `omp-jev` README "Dropped output is recoverable"; §8 below.

**Token reduction.** ~54% chars on tool-output-heavy windows (mine, §8),
53–61% (author); 0% on text-only spans (my 60k-char probe: 4 calls, 0% saved —
the reducer correctly did nothing). The `minReductionRatio` 0.25 gate means
small wins are declined in the hook paths — good. Built-ins reduce on every
compaction regardless of composition. **[INFERENCE]**: Jev's savings distribution
is bimodal (big on log-heavy sessions, nil on discussion-heavy ones) while
summaries save steadily; which wins depends on session shape, unmeasured
head-to-head by any party.

**Prompt-cache cost impact — the sharpest edge.** Every reduction rewrites the
conversation prefix, invalidating the provider prefix cache from the first
edited message. The three projects handle this with very different maturity:

- `omp-jev`: most sophisticated — **sticky decisions** (rewrite only after +40%
  growth *and* ≥15 requests, or every 40; byte-identical prefix between
  rewrites) plus a **cache guard** (non-sticky path skips sessions ≥80% cache
  reads). Both explicitly priced in README numbers (§2).
- `pi-jev`: honest warning, no mitigation — "Every ledger edit invalidates the
  provider's prompt cache from the first edited message onward. The proactive
  `turn_end` trigger repeats this every `cooldownTokens` of context growth…
  If cache writes dominate spend, increase `cooldownTokens`."
- `fast-jev` (Claude hook): one-shot at compaction time, so cache impact is no
  worse than any compaction; but its own `turn.complete` prompter fires at 60%
  and issue #103 documents it triggering a full built-in summary as early as
  60% — *increasing* billed summarization, the opposite of its goal.

For this setup (Opus-5 main where caching "matters," per the brief) the calculus
from my bench: one pass cost $0.000268 in Jev fees and removed 13,985 est.
tokens ≈ **$0.21 of Opus input per request** (~780× gross). But that arithmetic
ignores the cache-write delta on the *next* requests after a rewrite — the
dominant term on cache-served sessions, which is exactly why the author built
sticky+guard. Treat the 780× as ceiling, not profit **[INFERENCE]**.
Sources: `omp-jev` README "Sticky…", "The cache guard"; `pi-jev` README "Cost";
`fast-jev` #103; §8.

**Latency.** ~430 ms–1.3 s per pass (author 430 ms/decision-request; mine 1282
ms for a 30-call window in 1 request); questions batched, requests concurrent.
Cheaper than an LLM summary (which also bills output tokens), and OMP's async
speculative compaction already hides summarization latency on the built-in path.
No blocking issue found, assuming timeouts hold (10 s default; all paths fail
open — see below).

**Failure modes (observed, not hypothetical).**

- *Dropped facts*: 25% recall loss at 0.2 in my probe; 25–37% author range. Load-
  bearing facts echoed in assistant/user text survive (text is never touched) —
  the recall script's load-bearing probes pass partly via that second route.
- *Re-running tools*: safe mode keeps the call record so the agent *can* re-run;
  each re-run re-bills the tool's full output at main-model prices, which can
  exceed what pruning saved. Unquantified anywhere **[INFERENCE — watch
  re-run rate in any trial]**.
- *Pairing bugs*: fast-jev guarantees no result without its call by
  construction; omp-jev survived a live `use.tool.length` crash from mapping
  OMP's `toolCall/id/arguments` vs `toolCallId/toolName` split (fixed; regression
  test present); Pi 0.87's new `system` message role crashes the 0.85.1-targeted
  adapter (`message.toolResults is not iterable` → silent fallback; open issue
  `joelhooks/pi-fast-jev-compaction#2`).
- *Decision-cache collision*: `CachingAsker` keyed only on window-local
  `call_t1`/`result_t1` reused unrelated windows' verdicts (open issue
  `jerryfane/omp-jev-compaction#2`, fix PR #3 still open). The tree I cloned
  already scopes keys by state digest + stable per-call identity
  (`src/context.ts:62–101`, `src/vendor/fast-jev/compact.ts:137–143`) and all 61
  offline tests pass — but the upstream issue being open means version-to-version
  behavior here needs checking, not assuming.
- *Endpoint blocking*: real Claude Code transcripts trip Cloudflare WAF in front
  of `api.typesafe.ai` → HTTP 403 HTML → silent fallback to built-in summary,
  "so on typical sessions the plugin never reaches Jev" (open issue
  `tamaratran/fast-jev-compaction#97`). The omp-jev OpenRouter path sidesteps
  that host, but alpha-endpoint availability is its own risk (below).
- *Hook-scope bugs*: `session.compact` ignores `trigger`/`agentId` (precompute
  dispatches billed to Jev; subagent transcripts re-scored; `turn.complete`
  fires on subagent/aborted turns; in-flight guard can race) — open issue #107
  with a user patch. Fallback-to-built-in fires on manual `/compact` too, where
  nothing requires shrinking (#103, fix proposed: `builtinFallback` option).
- *Vendor-documented Jev weaknesses* (`docs.typesafe.ai/model-jaggedness/jev-1.13`,
  reviewed 2026-09-17): literal reading (answers the question written, not the
  one meant); no counting/math/dates; multi-hop indirection costs accuracy; and
  most pointedly — **"accuracy falls as the state grows with content unrelated
  to the decision… Jev suffers from context rot."** A whole-conversation state
  with dozens of questions is precisely the shape the vendor warns against; the
  plugins' state-fitting stages and 25k cap are mitigations, not cures.
  Adversarial content also moves answers — tool outputs are untrusted input
  steering keep/drop votes, worth a thought in hostile-output sessions
  **[INFERENCE]**.

**Data exposure.** Per pass the plugins ship: tool names + inputs + surrounding
message text (omp-jev replaces *outputs* with size notes first; fast-jev with a
one-line note). That is narrower than sending a session to a chat summarizer,
but it is still a *new* third party (TypeSafe direct) or a new surface on an
existing one (OpenRouter alpha). Plus `~/.omp/jev-spill/` persists dropped
payloads on shared-machine disk. The omp-jev README's own caution: "On a shared
machine that is one more place your work travels to." No training/retention
terms for the OpenRouter Decisions alpha path were found in this pass
(unverified — the companion note covers Zen privacy only).

**Maintenance risk.** `fast-jev`: 7,018 stars / 91 open issues (GitHub API,
2026-09-28; created 2026-09-17 — meteoric, and issue velocity matches: Cloudflare
WAF, hook-scope, fallback-scope, and a "does selection beat head+tail?"
benchmark (#99: an independent replay found local selectors *don't* beat plain
head+tail cuts — a caution flag for the whole approach, though it tested local
models, not Jev). Claude **function hooks are early-access** (2.1.274+,
`CLAUDE_CODE_ENABLE_FUNCTION_HOOKS`, generated `.d.ts` must be regenerated per
Claude upgrade — stated in `hooks/README.md` "Scope and caveat"). `omp-jev`: 9
stars, 3 issues; manifest settings "not wired up yet" (env vars only); OpenRouter
path "explicitly alpha upstream and may move" (`OMP_JEV_BASE_URL` escape hatch
provided). `pi-jev`: 13 stars, 2 issues; pinned to Pi 0.85.1, already broken by
Pi 0.87 system messages. Single-maintainer hobby surface on all three
**[INFERENCE from star/issue counts and explicit alpha/early-access labels]**.

## 5. How it overlaps with what OMP already does (the crux for this machine)

| Need | Built-in (current chain) | Jev plugin adds |
|---|---|---|
| Drop stale tool output early | `shake` + `pruneToolOutputs` + `dropUseless` + `supersedeReads`: mechanical, free, cache-aware timing | *Semantic* keep/drop per output (keeps load-bearing, drops stale regardless of age) |
| Survive full-region compaction losslessly | `snapcompact`: verbatim image archive, deterministic, no network | Nothing (Jev is lossy by design) |
| Semantic compression incl. text | `remote` server-side (reads prompt cache!) / `soft` LLM summary | Nothing (no text out) |
|....|...|...|

The one genuinely uncovered cell is *semantic* tool-output triage. Its value is
bounded above by what `shake` already reclaims for free, and its price is recall
loss + rewrite churn on the cache path. The author's own measurement that the
`session_before_compact` half "is useful only when raw results survive into the
region" plus this machine's shake-first pipeline means: of the two OMP
integration points, only continuous `context` reduction would ever fire here —
the per-request path with the worst cache-churn profile, which is why sticky
mode exists. If shake is already keeping sessions under the 70% threshold,
Jev has nothing left to bill **[INFERENCE]**.

## 6. Pi and Claude Code specifically

- **Pi 0.85.1** (installed version matches the extension's target — no version
  skew today): built-in threshold compaction + `session_before_compact` fallback
  seam make the extension safe to try (fails open to Pi summary). But its
  proactive `turn_end` trigger invalidates prompt cache every 8k tokens of
  growth with no sticky equivalent, and Pi 0.87 already breaks the adapter.
  Same verdict as OMP: try only if Pi sessions overflow despite built-in; prefer
  raising `keepRecentTokens`/tuning reserve first.
- **Claude Code 2.1.283**: built-in already "clears older tool outputs first,
  then summarizes," and `/compact` focus instructions + CLAUDE.md Compact
  Instructions give steering without a plugin. The Jev hook additionally needs
  early-access function hooks + a TypeSafe key, carries the WAF-403 failure
  (direct endpoint), the #107 scope bugs, and the #103 early-summary problem.
  The documented `PermissionRequest` Jev recipe (companion note §5) is a better
  Jev-on-Claude-Code spend: binary approval decisions are Jev's home turf;
  compaction is not.

## 7. Gimmick test

A gimmick would be: no independent mechanism, numbers that don't reproduce, or
no advantage over the default. None holds: the mechanism (calibrated `noul`
triage + verbatim rebuild + spill recovery) is distinct from summarization; my
two live probes landed inside the author's claimed ranges (§8); and on
tool-output-heavy windows it removes real tokens for ~$0.0003. The honest
framing is "a selective pre-filter for tool output," not "compaction." The
repos' own issues (#99's head+tail parity question, #100's unanswered "is it
accurate?", the recall gap) show the authors know the boundary. **Effective
tool, oversold category.**

## 8. Empirical checks run for this report (spend <$0.01 of the $0.50 cap)

Sandbox: clones under `/tmp/jev` (no plugin installed into omp/pi/claude, no
config edited — per contract). Key: existing `OPENROUTER_API_KEY`.

1. **Offline suites** (after `npm install` in each clone): `omp-jev` **61
   passed, 2 live skipped** (`vitest run`); `fast-jev` **29 passed**; `pi-jev`
   not run (npm `devEngines` pin `11.16.0` vs installed `11.9.0` blocks even
   `npm test` — itself a small maintenance-risk data point).
2. **Reduction bench** (`omp-jev/scripts/bench.ts`, OpenRouter
   `typesafe/jev-1.13`, `THRESHOLDS=0.2`, budget 250k chars) on this repo's
   session `-dev-agent-config/2026-08-30…01a05440` (cwd verified
   `/Users/sudakshsoti/dev/agent-config`; OQGA-cwd sessions excluded):
   **103,361 → 47,421 chars (−54.1%), 25,840 → 11,855 est. tokens, 30 calls /
   2 kept / 19 results dropped / 0 calls dropped, 1 Jev request, 6,381 input
   tokens, $0.000268, 1,282 ms.** Saved-value at list prices: $0.2098 (Opus
   $15/M), $0.0175, $0.0042. A 60k-char text-heavy probe saved 0% (4 calls) —
   correct no-op. Report at `/tmp/jev-bench.json`.
3. **Recall probe** (`scripts/recall.ts`, threshold `0.2`, answer model default
   `google/gemini-3.8-flash` via OpenRouter): full context **100%** (8/8) →
   reduced **75%** (6/8), **2 recoverable misses, 0 permanent** (spill files at
   `/tmp/jev-recall-spill` contained both), `charsSavedPct` 61.5%. Matches the
   author's 63–75% / 0-permanent claim. Full log at `/tmp/jev-recall.json`.

## 9. Gaps / unverified

- No head-to-head Jev-vs-`shake` or Jev-vs-summary recall measurement exists
  (author, upstream, or mine) — the comparison that would settle marginal value.
- Cache-*write* cost of sticky rewrites on Opus unmeasured; author's dollar
  figures are replay valuations, not billed deltas.
- Re-run rate after drops (the hidden cost of safe mode) unmeasured.
- OpenRouter Decisions alpha pricing/retention/training terms and rate limits:
  not found this pass; endpoint billed $0.000268/6.4k tokens in §8 (≈$0.042/M,
  consistent with Zen Jev pricing).
- `fast-jev` issue counts/star velocity taken from the GitHub API as observed;
  no judgment on legitimacy.
- Pi extension's live behavior not exercised (offline suite blocked by npm
  engine pin; no Pi session bench run).

## 10. Concrete recommendation

1. **Don't install** `omp-jev-compaction` (either path), `pi-fast-jev-compaction`,
   or `fast-jev-compaction` on this machine today. The OMP chain
   (`shake` → `snapcompact` → `remote` server-side → `soft`, 70% threshold,
   20k keepRecent) dominates on every axis that matters here: verbatim safety
   (snapcompact), cache affinity (server-side reads the cache), zero added
   vendors, zero added daemons.
2. **If** tool-output-heavy OMP sessions start overflowing despite shake, trial
   *only* the continuous `context` path, on OpenRouter (`typesafe/jev-1.13`),
   with: spill on (default), `OMP_JEV_KEEP_THRESHOLD=0.2`,
   `OMP_JEV_ALLOW_DROPPING_CALLS` unset (keep call records),
   `OMP_JEV_MIN_CHARS=150000` (default floor), sticky on (default). Watch for two
   weeks: `grep "jev context" ~/.omp/logs/…` reduction lines, prompt-cache hit
   rates, and any re-run loops on dropped outputs. Kill criterion: no overflow
   reduction or visible re-run churn → `OMP_JEV_CONTEXT=0`.
3. **Never** put Jev in the summarizer seat (`compaction.remoteEndpoint`,
   customOY compaction payloads that need prose) — protocol mismatch, fails
   closed (companion note probes 4–5).
4. Better Jev spends for this repo, if any: permission-approval gates and
   reviewer second-opinion filters (binary decisions, documented recipes,
   ~$0.00002/call) — see companion note §6 — not context management.

## Sources

- Repos (cloned 2026-09-28, read + tested): `tamaratran/fast-jev-compaction`
  (root + `hooks/README.md`, `src/compact.ts`, 29 tests pass),
  `jerryfane/omp-jev-compaction` (README, `src/context.ts`, `src/hook.ts`,
  `src/map.ts`, `scripts/{bench,recall,churn,huge,dist}.ts`, 61 tests pass),
  `joelhooks/pi-fast-jev-compaction` (README; suite blocked by npm engine pin).
- GitHub API 2026-09-28: fast-jev 7,018 stars / 91 open issues (created
  2026-09-17); omp-jev 9 stars / 3 issues (#2 open cache-key collision, #3 open
  fix PR, #7 open local-model port, #1/#4–#6 closed); pi-jev 13 stars / 2 issues
  (#2 open Pi-0.87 system-message crash). Notable upstream: fast-jev #97 (WAF
  403), #99 (head+tail parity bench), #100 (accuracy), #103 (fallback scope),
  #107 (hook trigger/agentId scope).
- Vendor/docs: `docs.typesafe.ai/introduction` (primitives, parallel eval),
  `docs.typesafe.ai/model-jaggedness/jev-1.13` (failure modes, context rot),
  `docs.typesafe.ai/llms.txt` (page index); `openrouter.ai/docs/cookbook/
  coding-agents/auto-approve-permission-prompts-with-jev` (Decisions endpoint
  shape, $0.0000168/400-token reference, risk-list-first design);
  `pi.dev/docs/latest/compaction` (threshold, 20k keepRecent, cache-write
  disabling, extension seam); `code.claude.com/docs/en/{how-claude-code-works,
  context-window, commands}` (clear-outputs-first, `/compact` focus,
  `/autocompact`, thrashing guard).
- Local: `omp://compaction.md` + `omp config list --json` (methodOrder,
  thresholds, shake/snapcompact/remote semantics); live probes §8
  (`/tmp/jev-bench.json`, `/tmp/jev-recall.json`); OpenRouter key balance
  endpoint ($13.69 remaining of $15 — total probe spend <$0.01, within cap).
- Prior: `docs/research/jev-context-management-2026-09.md` (Jev identity,
  protocol probes, quota pools, permission-hook recipe).
