Status: active

# Cutover: SuperGrok replaces OpenCode Go and Muse Code

User decisions 2026-10-10: keep the Anthropic subscription, use SuperGrok
(three-month deal, OMP provider `xai-oauth`), drop OpenCode Go and Muse Code;
`code-worker` on Claude because the Claude plan is underused; Haiku 5.5 replaces
Haiku 4.5. Evidence: `docs/research/ladder-benchmarks-2026-10.md` (benchmarks,
§5 implications), `docs/research/chatgpt-vs-supergrok-coding-2026-10.md`
(quota mechanics, ChatGPT alternative), `docs/research/dots-vs-grok-bot-2026-10.md`.

Do not cancel Go or Muse until step 5 passes. Muse renews 2026-10-18.

## Design

Facts this ladder is built on (all 2026-10-10):

- **Claude has the headroom.** `omp usage`: Claude 5h 2–3% used, 7-day 4% used.
  Claude takes every role that does not need a second lineage.
- **Grok's pool is small-or-unknown.** One weekly pool shared with Grok
  Chat/Build/Bot, size unpublished. Grok gets only the roles that need a
  non-Claude lineage or its X-search edge: review, research, scout.
- **Grok 4.7 is the only evidenced xAI model.** AA Index 46 (high 46, low 42),
  Terminal-Bench 4.0 37.6%, hallucination 0.29. `grok-build-0.1` has no benchmark
  anywhere; `grok-code-fast-1` is AA 14. Neither is routed.
- **Haiku 5.5 is fast and cheap but 100K in omp.** AA 43 max / 34 medium / 29
  low, 237 tok/s. `omp models anthropic` shows 100K context (the API is 1M with
  a price tier at 100K; omp enforces 100K). Fine for short prompts (commit
  messages, titles, mechanical edits); not for long exploration or as a rung
  under long Sonnet/Opus sessions.
- **Sonnet 5.5 is the best agentic coder per dollar.** TB 4.0 61.8% (#2, max),
  AA run 63.6% (top). `:medium` is AA 41.
- **OpenRouter GLM-5.3-Flash beats DeepSeek V4.1 Flash as the metered backstop.**
  AA 42 vs 39, hallucination 0.28 vs 0.54–0.97, TB 35.8% vs unlisted, $0.15/$0.50
  vs $0.30/$1.20. It is the model the review roles run today, so behaviour is known.
  Both ids probe `ok` through omp. Step-up option: `z-ai/glm-5.3` (AA 45, TB 41.8%)
  for the review chain, at ~8x the per-task cost.
- **Not routed:** Fable 5.1 (AA 53, reachable, but Claude lineage and the same
  weekly pool capped at 50%); Mythos 5.1 (404 on this plan).

Ladder (OMP):

| Role / agent | Primary | Fallback chain (exact-model key) |
| --- | --- | --- |
| `default` role | Opus 5.5 medium | Sonnet high → Grok 4.7 high → OR GLM-5.3-Flash high |
| `plan`/`designer`/`vision`/`security-reviewer` roles; `plan`/`security-reviewer` agents | Opus high | same Opus chain |
| `slow` role | Opus xhigh | same Opus chain |
| `critic` agent | Opus medium | same Opus chain |
| `task` role; `task`/`builder`/`workflow`/`code-worker` agents | Sonnet 5.5 medium | Grok 4.7 medium → OR GLM-5.3-Flash high |
| `adversary`/`reviewer`/`advisor` roles; `adversary`/`reviewer` agents | Grok 4.7 high | OR GLM-5.3-Flash high → Sonnet medium |
| `research` agent | Grok 4.7 high | same Grok chain |
| `scout` agent | Grok 4.7 low | same Grok chain |
| `smol`/`tiny`/`commit` roles | Haiku 5.5 low | Grok 4.7 low → OR GLM-5.3-Flash low |
| `sonic` agent | Haiku 5.5 medium | same Haiku chain |
| `web` role | Parallel | Firecrawl → Exa → DuckDuckGo → public (unchanged) |

Why each non-obvious choice:

- Sonnet's chain drops Haiku: Opus/Sonnet/Haiku share one Anthropic pool, so a
  Haiku rung only helps on a Sonnet-specific outage, and 100K would overflow a
  long `code-worker` session. Grok (500K) is the safe next hop.
- The Grok chain keeps review non-Claude: GLM before Sonnet. `research` and
  `scout` share that chain (chains are keyed by exact model) and pay OpenRouter
  per token while the Grok pool is empty.
- `scout` is on Grok 4.7 low (AA 42, 500K) rather than Haiku: exploration
  accumulates context past 100K. It is the highest-volume Grok role; step 8
  watches it.
- `adversary` stays at `high`, not `xhigh`: AA scores both 46; xhigh costs ~37%
  more per task.
- No Grok model falls back to another Grok model (one pool).

## 0. Gate (run before touching any file)

Already verified 2026-10-10 on this box: `anthropic/claude-haiku-5-5`,
`openrouter/z-ai/glm-5.3-flash`, `openrouter/z-ai/glm-5.3` and
`openrouter/deepseek/deepseek-v4.1-flash` answer `ok` with retry disabled;
GLM and DeepSeek on OpenRouter accept `low,high,max` only. Pi is not installed
on this box (`pi` not on PATH), so Pi steps are verified on a box that has it.

1. `omp login xai-oauth` (device flow: open the printed accounts.x.ai URL, enter
   the code).
2. `omp models xai-oauth`: record ids, effort levels, context. Expect `grok-4.7`.
3. Probe with retry disabled:
   `omp -p --model xai-oauth/grok-4.7:high --config <(printf 'retry:\n  enabled: false\n') "Reply with exactly: ok" </dev/null`
   Repeat with `:low` and `:medium`.
4. `omp usage invalidate --provider xai-oauth && omp usage --provider xai-oauth --json`.
   Grok usage awareness depends on this report (binary read 2026-10-10, omp's
   `xaiOauthUsageProvider`/`xaiOauthRankingStrategy`): omp reads
   `cli-chat-proxy.grok.com/v1/billing` and the reserve check uses limit
   `xai-oauth:credits:1w` ("SuperGrok Weekly Credits"), or
   `xai-oauth:included:1mo` ("SuperGrok Monthly Included") when there is no weekly
   one. Pass condition: one of those ids is present with a `usedFraction`, and
   `metadata.monthlyQuotaAdvisory` is absent. Two cases make omp report
   **unknown** and keep spending Grok without falling back:
   `monthlyQuotaAdvisory: true`, or an `xai-oauth:on-demand` limit that is not
   exhausted (paid on-demand usage is switched on). If on-demand shows up, switch
   it off in the SuperGrok billing settings and re-run this step.
   `skills/overnight-run/scripts/usage-gate.sh --provider xai-oauth` still exits 30
   (it needs `5h` and `7d`), so overnight runs keep their Anthropic worker; do not
   change that gate here.
5. Pi (on a box with Pi): `/login`, pick "xAI (Grok/X subscription)"; record the
   provider prefix Pi shows (expected `xai/`); probe one request. Confirm the
   Anthropic shim knows `anthropic/claude-haiku-5-5`; if not, use
   `claude-haiku-4-5` in Pi only. If Pi has no xAI path, route Pi's Grok roles to
   Sonnet medium and say in `pi/model-ladder.md` that Pi review is same-lineage.

Substitutions: if `grok-4.7` is missing use `grok-4.6` (AA 44, TB 20.3%; weaker on
agentic work). If Grok has no `medium`, use `high`. If `grok-build-0.1` appears,
do not route it; trial it on `commit` only after a week (step 8).

## 1. `omp/config.yml`

OMP strips comments on rewrite; keep rationale out of this file.
`disabledProviders: [openai-codex]` stays.

`modelRoles` (replace lines 8, 9, 11–14):

```yaml
  adversary: xai-oauth/grok-4.7:high
  reviewer: xai-oauth/grok-4.7:high
  advisor: xai-oauth/grok-4.7:high
  smol: anthropic/claude-haiku-5-5:low
  tiny: anthropic/claude-haiku-5-5:low
  commit: anthropic/claude-haiku-5-5:low
```

`task.agentModelOverrides` (replace the six non-Claude lines):

```yaml
    scout: xai-oauth/grok-4.7:low
    sonic: anthropic/claude-haiku-5-5:medium
    adversary: xai-oauth/grok-4.7:high
    reviewer: xai-oauth/grok-4.7:high
    code-worker: anthropic/claude-sonnet-5-5:medium
    research: xai-oauth/grok-4.7:high
```

`retry.fallbackChains` (replace everything above `web:`; `web:` unchanged):

```yaml
    anthropic/claude-opus-5-5:
      - anthropic/claude-sonnet-5-5:high
      - xai-oauth/grok-4.7:high
      - openrouter/z-ai/glm-5.3-flash:high
    anthropic/claude-sonnet-5-5:
      - xai-oauth/grok-4.7:medium
      - openrouter/z-ai/glm-5.3-flash:high
    anthropic/claude-haiku-5-5:
      - xai-oauth/grok-4.7:low
      - openrouter/z-ai/glm-5.3-flash:low
    xai-oauth/grok-4.7:
      - openrouter/z-ai/glm-5.3-flash:high
      - anthropic/claude-sonnet-5-5:medium
    smol:
      - anthropic/claude-haiku-5-5:low
    tiny:
      - anthropic/claude-haiku-5-5:low
    commit:
      - anthropic/claude-haiku-5-5:low
    default:
      - anthropic/claude-sonnet-5-5:medium
      - xai-oauth/grok-4.7:medium
```

`usageAwareFallback`/`usageReservePct`/`usageReservePolicy` stay
`true`/`20`/`auto`. That makes Grok usage-aware with no new keys: before every
turn, and when each subagent starts, omp checks the primary model's provider.
At ≤20% weekly credits left it moves to the next rung in the exact-model chain,
skipping any rung that is itself in reserve or too small for the context. Grok
roles go to OpenRouter GLM-5.3-Flash, then Sonnet; Claude roles skip a Grok rung
that is in reserve.

Optional, only if the Grok apps need more headroom: give Grok its own reserve.
A per-account `reservePct` overrides the global value in that check. Use the
email that gate 4 recorded:

```yaml
auth:
  accountPolicies:
    - provider: xai-oauth
      account:
        email: <email from gate 4>
      reservePct: 35
```

## 2. OMP agent frontmatter

`check-model-routing.py` fails on frontmatter that drifts from the override.

- `omp/agents/code-worker.md` → `model: anthropic/claude-sonnet-5-5:medium`
- `omp/agents/research.md` → `model: xai-oauth/grok-4.7:high`

## 3. Pi (prefix assumed `xai/`; correct it from gate 5)

Pi cannot reach OpenRouter (`PI_UNREACHABLE`), so Pi chains end on Claude or Grok.
Claude pins are allowed while `@gotgenes/pi-anthropic-auth` is in
`pi/settings.json` `packages[]` (it is).

`pi/model-roles.json` `roles` (non-Claude entries):

```json
    "sonic": "anthropic/claude-haiku-5-5:medium",
    "adversary": "xai/grok-4.7:high",
    "reviewer": "xai/grok-4.7:high",
    "advisor": "xai/grok-4.7:high",
    "smol": "anthropic/claude-haiku-5-5:low",
    "tiny": "anthropic/claude-haiku-5-5:low",
    "commit": "anthropic/claude-haiku-5-5:low"
```

`pi/model-roles.json` `chains` (replace the whole object):

```json
  "chains": {
    "anthropic/claude-opus-5-5": [
      "anthropic/claude-sonnet-5-5:high",
      "xai/grok-4.7:high"
    ],
    "anthropic/claude-sonnet-5-5": [
      "xai/grok-4.7:medium"
    ],
    "anthropic/claude-haiku-5-5": [
      "xai/grok-4.7:low"
    ],
    "xai/grok-4.7": [
      "anthropic/claude-sonnet-5-5:medium"
    ]
  },
```

`pi/agents/*.md` (`model:` / `thinking:`):

| Agent | model | thinking |
| --- | --- | --- |
| `Explore.md`, `scout.md` | `xai/grok-4.7` | low |
| `adversary.md`, `reviewer.md` | `xai/grok-4.7` | high |
| `code-worker.md` | `anthropic/claude-sonnet-5-5` | medium |
| `research.md` | `xai/grok-4.7` | high |
| `sonic.md` | `anthropic/claude-haiku-5-5` | medium |
| `public-scout.md` | retire: it existed only to keep the training-eligible Muse tier on public material. Grep `public-scout` for callers first. |

Other Pi files:

- `pi/settings.json` `compaction.modelOverrides`: delete the four
  `opencode-go/*` entries; add none (Grok 500K, Haiku 100K: the 800000 reserve
  fits neither).
- `pi/verbosity.json` `models`: delete the three `opencode-go/*` keys.
- `pi/workflows/model-tiers.json`: `"small": "anthropic/claude-haiku-5-5"`.
- `pi/extensions/model-roles/index.ts` line 27 comment example
  `/model opencode-go/...` → `/model xai/...`.

## 4. Docs (correct docs to config, never the reverse)

`AGENTS.md`:

- Routing table: `code-worker` joins the `task` row (Sonnet medium);
  `sonic` → `anthropic/claude-haiku-5-5:medium`; `smol`/`tiny`/`commit` →
  `anthropic/claude-haiku-5-5:low`; `adversary`/`reviewer`/`advisor` →
  `xai-oauth/grok-4.7:high`; `scout` → `xai-oauth/grok-4.7:low`; `research` →
  `xai-oauth/grok-4.7:high`. `disabledProviders` row unchanged.
- Delete the Muse training paragraph.
- Rewrite the `usageAwareFallback` paragraph: it covers both subscriptions. At
  20% left, Claude roles go to their Grok rung and Grok roles go to OpenRouter
  GLM-5.3-Flash. Grok is measured on the SuperGrok weekly credits, or the monthly
  included allowance if there is no weekly one. It fails open (keeps spending)
  when xAI marks the quota advisory or paid on-demand usage is on. Keep the
  `openai-codex` sentence, reworded: no ChatGPT subscription.
- Replace the "Muse Spark requires omp ≥18.1.6" bullet with a SuperGrok bullet
  (deal end date, one unpublished weekly pool shared with Grok Chat/Build/Bot,
  overnight gate cannot use it) and this marker block:

  ```
  <!-- routing:current -->
  `code-worker` → `anthropic/claude-sonnet-5-5` medium
  `research` → `xai-oauth/grok-4.7` high
  `sonic` → `anthropic/claude-haiku-5-5` medium
  <!-- routing:end -->
  ```

- Thinking-level bullet: Go/Muse notes out; add Grok 4.7 (low/medium/high/xhigh,
  cannot disable), Haiku 5.5 (low..max, 100K in omp), OpenRouter GLM/DeepSeek
  (low/high/max only).
- Pi gotcha: delete the Muse sentence; mention the `xai` login.
- Work machine gate paragraph: "OpenCode Go and Muse Code" → "xAI (`xai-oauth`)
  and OpenRouter"; the gate itself is unchanged.

Elsewhere:

- `README.md` lines 34–35: plain OMP runs Claude plus `xai-oauth` (SuperGrok) for
  cross-lineage review, research and discovery; `openai-codex` disabled.
- `pi/model-ladder.md`: ladder rows to match step 3; remove the Muse guardrail and
  the Muse/GLM/DeepSeek/Kimi rationale bullets; add Grok 4.7 (review, research,
  scout; X search) and Haiku 5.5 (cheap roles, sonic; 100K); "fall through to
  their OpenCode Go rungs" → Grok rungs; OpenCode Go link → https://docs.x.ai/grok/faq.
- `design/decisions.md`: add `[stated] SuperGrok (three-month deal) replaces
  OpenCode Go and Muse Code; ChatGPT Plus deferred; code-worker on Sonnet and
  cheap roles on Haiku 5.5 because the Claude plan is underused; Grok carries
  only review, research and scout; OpenRouter GLM-5.3-Flash replaces DeepSeek V4.1
  Flash as the metered backstop. — User, 2026-10-10.` Mark the 2026-10-04
  GLM-chain entry and the 2026-09-16 routing rationale as superseded; cite
  `docs/research/ladder-benchmarks-2026-10.md`.
- `skills/overnight-run/SKILL.md` line 87 example: replace the Go model with an
  Anthropic one; note `xai-oauth` cannot pass the usage gate (no `5h`).

Leave alone: `docs/research/*` (dated history); synthetic `opencode-go`
fixtures in `scripts/test-check-model-routing.py`,
`skills/overnight-run/scripts/test-*.sh` and `fixtures/go-provider-*.json`.

## 5. Verify

1. `python3 scripts/check-model-routing.py` — zero failures.
2. `python3 scripts/lint-skills.py` and `scripts/check.sh`.
3. Grep the live tree (`omp/`, `pi/`, `AGENTS.md`, `README.md`, `skills/`) for
   `opencode-go`, `muse-code`, `muse-spark`, `glm-5.3-flash:` outside
   `openrouter/`, `deepseek`: only the fixtures above remain.
4. Fresh OMP session: a `scout` task, a `reviewer` task, a `code-worker` task, a
   commit message. `omp usage` shows SuperGrok credits and Claude moving.
5. Pi box: `/roles` shows the new chains; one `role/adversary` request answers.

## 6. Commit

Check `git diff` for OMP/Pi rewrites of `omp/config.yml` and `pi/settings.json`
before committing. No agent co-author line.

## 7. Cancel

After step 5 passes: cancel OpenCode Go and Muse Code (Everyday Usage, renews
2026-10-18). Remove their credentials on each box: the `muse-code` and
`opencode-go` entries OMP stores (`omp auth-broker list` for the removal
command) and `opencode-go` in `~/.pi/agent/auth.json`.

## 8. Watch the pool (first two weeks), then delete this plan

- Fallback is automatic at 35% Grok credits left (20% for Claude). Grok Build
  (CLI 1.0.50, signed in on the homelab box 2026-10-10) bills the same weekly
  pool through the same `cli-chat-proxy.grok.com` endpoint, so heavy Grok Build
  days push omp's Grok roles into reserve sooner. After a week, check
  `omp usage --provider xai-oauth`
  and the OpenRouter bill. If Grok keeps hitting reserve and OpenRouter spend
  grows, move roles to Claude by hand in this order, re-running step 5.1 after
  each: `scout` →
  `anthropic/claude-sonnet-5-5:low` (AA 36, 1M context; Haiku's 100K is too small
  for exploration); then `research` → `anthropic/claude-sonnet-5-5:high`. Review
  roles stay on Grok last.
- If `grok-build-0.1` is in the catalog, trial it on `commit` for a week before
  any wider use (no published benchmarks). Weak signal against it: Grok Build's
  own model list (`~/.grok/models_cache.json`) offers only `grok-4.7`,
  `grok-4.7-build-fast` (2x price), `grok-4.6` and `grok-4.5`.
- Put the deal's end date in `AGENTS.md`'s SuperGrok bullet. About two weeks
  before it, decide renew vs ChatGPT Plus (`docs/research/chatgpt-vs-supergrok-coding-2026-10.md`
  §5 Option A).
- Delete this plan once steps 0–7 are done and the pool check holds.
