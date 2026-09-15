# Pi model ladder

Pi runs entirely on OpenCode Go. It has no Claude path: the Anthropic
subscription rejects third-party clients (HTTP 400, "Third-party apps now draw
from your extra usage") and the stored OpenRouter key is dead (HTTP 401, "User
not found"). Probe evidence:
`docs/research/harness-provider-access-2026-09.md`. Claude 5x work belongs in
OMP, whose routing is in `omp/config.yml`.

Within Go: DeepSeek V4.1 Flash is the main session (fast, 1M context, ZDR,
DesignArena rank 7 overall — ahead of every OpenAI model available here), Kimi K3
is the design specialist (DesignArena rank 1 overall, 1388, but the lowest Go cap
at $15/month and only ~35 tok/s), GLM 5.3 Flash is bounded discovery and
second-lineage review, and Muse Spark 1.3 Contributor serves public material
only.

| Task / agent | Provider and model | Effort |
| --- | --- | --- |
| Main session | `opencode-go/deepseek-v4.1-flash` | high |
| `builder` implementing an approved UI plan | `opencode-go/kimi-k3` | high |
| `Critic` visual review | `opencode-go/kimi-k3` | high |
| `Plan` planning a screen or feature | `opencode-go/deepseek-v4.1-flash` | high |
| `code-worker` precisely scoped routine fixes, tests and mechanical refactors | `opencode-go/deepseek-v4.1-flash` | high |
| unnamed `general-purpose` fallback | `opencode-go/deepseek-v4.1-flash` | high |
| `workflow` coordinating multi-part implementation | `opencode-go/deepseek-v4.1-flash` | high |
| `scout`, `Explore` and private codebase discovery | `opencode-go/glm-5.3-flash` | low |
| `reviewer` adversarial review of plans and diffs on a second model lineage | `opencode-go/glm-5.3-flash` | high |
| `research` primary-source investigation and cited reports | `opencode-go/muse-spark-1.3-contributor` | high |
| Optional `public-scout`, public/disposable material only | `opencode-go/muse-spark-1.3-contributor` | minimal |
| Anything that needs Claude judgement or Claude-grade frontend work | run it in OMP | — |

`muse-spark-*-contributor` is Meta's training-eligible tier (prompts and
completions are used for training), so it serves only public material:
`research` and `public-scout`. Private-code discovery runs on GLM 5.3 Flash and
private implementation on DeepSeek V4.1 Flash, both zero-data-retention on Go.
Kimi K3's $15/month cap is roughly 490 requests; it is a design specialist, not a
default. If `builder` exhausts it, fall back to
`opencode-go/deepseek-v4.1-flash` high rather than a Luna-class model.
DeepSeek V4.1 Flash's $60/month Go cap is a promotion ending 2026-09-20 (then
$15, i.e. $3 per 5 hours); if the main session throttles after that, move it and
`code-worker` to `opencode-go/glm-5.3-flash` high.
Escalate repeated failed approaches instead of allowing an extended retry loop.
GLM 5.3 Flash and Kimi K3 accept only low/high/max thinking; medium runs as high.
DeepSeek V4.x Flash accepts low, high and max (minimal→low, medium and
xhigh→high). `minimal` is not a real level on any provider still routed here.
Model overrides on agent calls take precedence over agent defaults; these files
do not implement automatic escalation or quota-based routing.

## Scoped models

`settings.json` sets `defaultProvider`/`defaultModel` to
`opencode-go`/`deepseek-v4.1-flash` at `high`, and `enabledModels` to DeepSeek
V4.1 Flash high, Kimi K3 high, GLM 5.3 Flash high and Muse Spark 1.3 xhigh, in
that order.
This is the Ctrl+P quick-switch list, not an access restriction or an
agent-routing table.
Pi deduplicates scoped entries by provider/model ID; multiple effort presets for
the same model do not create multiple cycle entries.
Use `/thinking` to lower effort for disposable work, or set it explicitly on an
agent call.
Other authenticated Go models remain selectable through `/model` or explicit
agent overrides. `anthropic/*` and `openrouter/*` entries appear in `/model` but
fail at request time until the extra-usage balance or the OpenRouter key is
restored.

## Restoring a Claude path in Pi

Two independent options, neither applied here because both cost money outside
this repository's control:

- buy extra usage at `claude.ai/settings/usage`; the existing `anthropic` OAuth
  credential then works from Pi, metered against that balance rather than the
  plan;
- replace the dead OpenRouter API key in `~/.pi/agent/auth.json` (machine-local,
  never tracked) and route `anthropic/claude-sonnet-5` or
  `anthropic/claude-opus-5` through `openrouter`, metered per token.

Until then, treat OMP as the Claude harness and Pi as the flat-rate harness.

`~/.pi/agent/settings.json` and the files in `~/.pi/agent/agents/` link to this repository's Pi configuration.
No installation or copy step is needed for edits to existing linked files.
Restart Pi to load the updated configuration.
Resumed sessions may restore their previously selected model and effort.

## Evidence and limits

The ladder was re-based on 16 September 2026 against Artificial Analysis Intelligence Index v4.3, the Coding Agent Index, LMArena text/WebDev, DesignArena, the OpenCode Go usage-limit table and the local provider probes. Full citations: `docs/research/opencode-go-models-2026-09.md`, `docs/research/designarena-2026-09.md`, `docs/research/anthropic-models-2026-09.md`, `docs/research/harness-provider-access-2026-09.md`.
Arena and DesignArena scores are single-shot generations and do not measure tool use, repository grounding or multi-turn editing; harness experience overrides them.
Provider message estimates are not fixed limits or controlled comparisons between models.

- [Artificial Analysis methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking)
- [OpenCode Go usage limits](https://opencode.ai/docs/go/#usage-limits)
