# Pi model ladder

Pi runs entirely on OpenCode Go, and the only credential is an OpenCode Go API
key: the `openai-codex`, `anthropic` and `openrouter` credentials were removed
from `~/.pi/agent/auth.json` on 2026-09-16. Pi is therefore a Go-only harness.
Restoring a Claude path requires re-adding a credential first (see below).
`docs/research/harness-provider-access-2026-09.md` holds the probe evidence.
Claude 5x work belongs in OMP, whose routing is in `omp/config.yml`.

The default ladder is deliberately Muse-heavy: Muse Spark 1.3 Contributor anchors
nearly everything because it is the strongest model on Go (Artificial Analysis
Intelligence Index 48) and the cheapest per request, and it sits on the largest,
least-used quota ($60/month cap, ~226.6k est. requests/month, 220.8 tok/s,
$0.10/$0.20 rates). The previous restriction of Muse to public material only is
lifted by user decision: Pi runs disposable personal work containing no private
information, and the user explicitly accepted Meta's training-eligible tier for
that work.

**Guardrail:** `muse-spark-*-contributor` is Meta training-eligible and not
zero-data-retention — prompts and completions may be used for training. Any
session that will touch private, client or sensitive material MUST be routed to
GLM 5.3 Flash or DeepSeek V4.1 Flash (both ZDR on Go) via an agent override or
Ctrl+P before the work starts.

## Ladder

| Task / agent | Provider and model | Effort |
| --- | --- | --- |
| Main session, `builder` implementing an approved UI plan | `opencode-go/muse-spark-1.3-contributor` | xhigh |
| `Plan` planning a screen or feature | `opencode-go/muse-spark-1.3-contributor` | high |
| `code-worker` precisely scoped routine fixes, tests and mechanical refactors | `opencode-go/muse-spark-1.3-contributor` | high |
| `workflow` coordinating multi-part implementation | `opencode-go/muse-spark-1.3-contributor` | high |
| unnamed `general-purpose` fallback | `opencode-go/muse-spark-1.3-contributor` | high |
| `research` primary-source investigation and cited reports | `opencode-go/muse-spark-1.3-contributor` | high |
| `scout`, `Explore` and codebase discovery | `opencode-go/muse-spark-1.3-contributor` | minimal |
| Optional `public-scout`, public/disposable material only | `opencode-go/muse-spark-1.3-contributor` | minimal |
| `reviewer` adversarial review of plans and diffs on a second model lineage | `opencode-go/glm-5.3-flash` | high |
| `Critic` visual review of implemented work | `opencode-go/glm-5.3-flash` | high |
| Manual fallback when Muse or GLM throttles (Ctrl+P) | `opencode-go/deepseek-v4.1-flash` | high |
| Anything that needs Claude judgement or Claude-grade frontend work | run it in OMP | — |

Rationale per model:

- **Muse Spark 1.3 Contributor** carries the main session, all implementer/planner
  agents and all discovery. At ~$0.0003/request at `minimal` effort it is the
  cheapest discovery on Go, and at `xhigh` it was the strongest UI implementer
  available on Go once the privacy constraint lifted (LMArena WebDev muse-max
  rank 8 / 1652; muse xhigh rank 12 / 1623 — both above DeepSeek V4.1's 1614).
  Educational note: the `contributor` tier means Meta trains on this traffic.
- **GLM 5.3 Flash** keeps the review/discovery second lineage and reviews
  Meta-lineage output. Its own permanent $60/month cap means a Muse 5-hour
  exhaustion still leaves a working second lineage. GLM is ZDR, so `Critic` and
  `reviewer` are the only agents that may touch private or sensitive material on
  a non-Muse model if a private-material session slips through.
- **Kimi K3 is not routed at all.** Its ~490 requests/month cap is the scarcest
  on Go and the user judged the cost unjustified ("can't afford it") — this is a
  cost decision, not a benchmark finding. The Go key still covers Kimi, so it
  stays probeable; to use it again, re-add it to `enabledModels` and pin it on an
  agent.
- **DeepSeek V4.1 Flash has no agent pin.** It is the manual quota fallback: its
  promoted $60/month cap ends 2026-09-20, after which it is $15/month (≈$3 per
  5-hour window), too tight for daily pinned use.

## Manual quota fallback

Pi implements no automatic fallback chains. Quota rules:

- If Muse Spark throttles (its 5-hour window is $12), switch the main session to
  `opencode-go/glm-5.3-flash` high or `opencode-go/deepseek-v4.1-flash` high via
  Ctrl+P.
- If GLM throttles, use DeepSeek V4.1 Flash.
- Escalate repeated failed approaches instead of allowing an extended retry loop.

Effort support: GLM 5.3 Flash and Kimi K3 accept only low/high/max; medium runs
as high. DeepSeek V4.x Flash accepts low, high and max (minimal→low, medium and
xhigh→high). Muse Spark 1.3 accepts all levels, `minimal` through `xhigh`,
natively.
Model overrides on agent calls take precedence over agent defaults; these files
do not implement automatic escalation or quota-based routing.

## Scoped models

`settings.json` sets `defaultProvider`/`defaultModel` to
`opencode-go`/`muse-spark-1.3-contributor` at `xhigh`, and `enabledModels` to
Muse Spark 1.3 Contributor xhigh, GLM 5.3 Flash high and DeepSeek V4.1 Flash
high, in that order (most-used first).
This is the Ctrl+P quick-switch list, not an access restriction or an
agent-routing table.
Pi deduplicates scoped entries by provider/model ID; multiple effort presets for
the same model do not create multiple cycle entries.
Use `/thinking` to change effort for the current session, or set it explicitly
on an agent call.
The GLM cycle entry pins `:high` so switching away from Muse never sends Muse's
`xhigh` to a model that only accepts low/high/max.
Other authenticated Go models remain selectable through `/model` or explicit
agent overrides. No non-Go providers remain reachable: their credentials were
removed from `~/.pi/agent/auth.json` on 2026-09-16.

## Restoring a Claude path in Pi

Both options require **re-adding the credential first** (it was removed on
2026-09-16; each is restorable via `/connect` or a fresh OAuth login), and then:

- buy extra usage at `claude.ai/settings/usage`; a working `anthropic` OAuth
  credential then works from Pi, metered against that balance rather than the
  plan — note that without extra usage Anthropic rejects the login outright
  (HTTP 400, "Third-party apps now draw from your extra usage");
- or add a live OpenRouter API key and route `anthropic/claude-sonnet-5` or
  `anthropic/claude-opus-5` through `openrouter`, metered per token.

Until then, treat OMP as the Claude harness and Pi as the flat-rate harness.

`~/.pi/agent/settings.json` and the files in `~/.pi/agent/agents/` link to this repository's Pi configuration.
No installation or copy step is needed for edits to existing linked files.
Restart Pi to load the updated configuration.
Resumed sessions may restore their previously selected model and effort.

## Evidence and limits

The ladder was re-based on 16 September 2026 against Artificial Analysis
Intelligence Index v4.3, the Coding Agent Index, LMArena text/WebDev,
DesignArena, the OpenCode Go usage-limit table and the local provider probes
(GLM, DeepSeek, Kimi, Luna probed 2026-09-16; Muse Spark 1.3 contributor probed
from Pi the same day). Full citations:
`docs/research/opencode-go-models-2026-09.md`,
`docs/research/designarena-2026-09.md`,
`docs/research/anthropic-models-2026-09.md`,
`docs/research/harness-provider-access-2026-09.md`.
Arena and DesignArena scores are single-shot generations and do not measure tool
use, repository grounding or multi-turn editing; harness experience overrides
them.
Provider message estimates are not fixed limits or controlled comparisons
between models.
The Muse-unrestricted decision and the Kimi removal are user cost/privacy
decisions, not benchmark findings.

- [Artificial Analysis methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking)
- [OpenCode Go usage limits](https://opencode.ai/docs/go/#usage-limits)
