# Pi model ladder

Pi's ladder runs on OpenCode Go, and the only credential it holds today is an
OpenCode Go API key: the `openai-codex`, `anthropic` and `openrouter`
credentials were removed from `~/.pi/agent/auth.json` on 2026-09-16. Pi is
therefore a Go-only harness in practice. A Claude path exists again in principle
through the `@gotgenes/pi-anthropic-auth` extension (installed 2026-10-02), but
it stays inert until `/login anthropic` re-adds the credential — see
[Reaching Claude from Pi](#reaching-claude-from-pi) below.
`docs/research/harness-provider-access-2026-09.md` holds the original probe
evidence and `docs/research/pi-claude-subscription-2026-10.md` the newer
findings. Claude 5x work belongs in OMP by default, whose routing is in
`omp/config.yml`.

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
| Main session | `opencode-go/muse-spark-1.3-contributor` | xhigh |
| `builder` implementing an approved UI plan | `anthropic/claude-opus-5-5` | high |
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

Anything that needs Claude judgement or Claude-grade frontend work runs in OMP,
not in this ladder.

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

`settings.json` sets the default (checked against the Main session row):

<!-- routing:current -->
`main` → `opencode-go/muse-spark-1.3-contributor` xhigh
<!-- routing:end -->

`settings.json` sets `enabledModels` to
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
agent overrides. The OpenRouter key is dead and was removed from
`~/.pi/agent/auth.json` on 2026-09-16.

## Reaching Claude from Pi

Pi reaches Claude only through the `@gotgenes/pi-anthropic-auth` extension
(installed 2026-10-02, requires Pi ≥ 0.86.0; this box runs Pi 1.0.0). It
de-fingerprints Pi's system prompt and injects Claude Code's billing header,
which is what stops Anthropic classifying the request as third-party traffic
and billing it against extra usage instead of the plan.

**It does not work until the credential exists.** `~/.pi/agent/auth.json` holds
only `opencode-go`, because the `anthropic` OAuth credential was removed on
2026-09-16. Run `/login anthropic` in Pi; it is an interactive browser flow and
is per box, like every other login in this repo.

When it is live, Claude is a **manual escalation, not a ladder rung**, and
`builder` is its one deliberate consumer — the UI implementer, where Claude's
frontend judgement beats Muse Spark and the fragile route earns its keep. It
runs at `high`, not `xhigh`: Claude thinking is the scarce plan resource.

- Pin it explicitly on an agent (`model: anthropic/claude-opus-5-5`).
  `scripts/check-model-routing.py` permits this only while the package is
  listed in the tracked `pi/settings.json` `packages[]`, so removing the package also reverts the pin to a hard failure
  rather than a silent wrong route.
- Never set it as `defaultProvider`, an `enabledModels` cycle entry, or
  `web-search.json` `summaryModel`. The check rejects all three unconditionally,
  because the extension impersonates Claude Code and must not become the face of
  the harness.
- Never put it in a fallback: Pi has no fallback chains, and a silent Claude
  route is exactly the failure mode the check exists to prevent.

Two halves must both hold, and either can rot silently:

1. the repo-owned `pi/extensions/anthropic-prompt-shim/` extension removes the
   prompt line Anthropic's classifier keys on;
2. `@gotgenes/pi-anthropic-auth` supplies the billing header.

Run `./scripts/check-claude-path.py` after every `pi update`; it reports Pi
version against the shim's floor, the installed package, the credential, whether
the installed Pi still builds the trigger line, and whether any agent pins
Claude while a prerequisite is unmet. It exits 0 with findings rather than
gating `check.sh`, because a missing credential is normal on a fresh box.

The other options remain:

- buy extra usage at `claude.ai/settings/usage` for a metered path that needs no
  extension, billed per token rather than against the plan;
- or add a live OpenRouter key and route `anthropic/claude-sonnet-5-5` through
  `openrouter`, also metered per token.

OMP remains the Claude harness on the subscription proper; Pi is the flat-rate
harness by default. Full evidence and the ToS/breakage caveats:
`docs/research/pi-claude-subscription-2026-10.md`.

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
