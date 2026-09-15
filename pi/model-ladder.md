# Pi model ladder

Use OpenCode Go for bounded discovery, routine implementation and second-lineage
review. Reserve Codex Luna for the main coding session and Codex Sol for anything
that judges pixels, plus difficult architecture and security decisions.

| Task / agent | Provider and model | Effort |
| --- | --- | --- |
| Main session | `openai-codex/gpt-5.6-luna` | high |
| `builder` implementing an approved UI plan | `openai-codex/gpt-5.6-sol` | medium |
| `code-worker` precisely scoped routine fixes, tests and mechanical refactors | `opencode-go/deepseek-v4.1-flash` | high |
| `scout`, `Explore` and private codebase discovery | `opencode-go/glm-5.3-flash` | low |
| `research` primary-source investigation and cited reports | `opencode-go/muse-spark-1.3-contributor` | high |
| unnamed `general-purpose` fallback | `openai-codex/gpt-5.6-luna` | medium |
| `workflow` coordinating multi-part implementation | `openai-codex/gpt-5.6-sol` | medium |
| `Plan` and `Critic` planning and visual review | `openai-codex/gpt-5.6-sol` | high |
| `reviewer` adversarial review of plans and diffs on a second model lineage | `opencode-go/glm-5.3-flash` | high |
| Difficult bugs, architecture or security-sensitive decisions | Explicit `openai-codex/gpt-5.6-sol` override | xhigh |
| Optional `public-scout`, public/disposable material only | `opencode-go/muse-spark-1.3-contributor` | minimal |

Luna sits within 5 points of Sol on the Coding Agent Index at 1/20 the Pro-plan
credit rate, but ranks 34-48 on every DesignArena board; Sol at medium matches
Sol at xhigh there, so `builder` runs Sol medium and a design-heavy main session
switches with `/model` rather than paying Sol on every coding turn.
`muse-spark-*-contributor` is Meta's training-eligible tier (prompts and
completions are used for training), so it serves only public material:
`research` and `public-scout`. Private-code discovery runs on GLM 5.3 Flash,
which is zero-data-retention on Go.
DeepSeek V4.1 Flash's $60/month Go cap is a promotion ending 2026-09-20 (then
$15, i.e. $3 per 5 hours); if `code-worker` throttles, move it to
`openai-codex/gpt-5.6-luna` medium.
Escalate repeated failed approaches instead of allowing an extended retry loop.
GLM 5.3 Flash and Kimi K3 accept only low, high and max thinking; medium runs as
high. DeepSeek V4.x Flash accepts low, high and max (minimal→low, medium and
xhigh→high). OpenAI models accept none/low/medium/high/xhigh/max; `minimal` is
not a real level on any provider here.
Model overrides on agent calls take precedence over agent defaults; these files
do not implement automatic escalation or quota-based routing.

## Scoped models

`settings.json` sets `enabledModels` to Luna high, DeepSeek V4.1 Flash high,
Sol high and Muse Spark 1.3 xhigh, in that order.
This is the Ctrl+P quick-switch list, not an access restriction or an
agent-routing table.
Pi deduplicates scoped entries by provider/model ID; multiple effort presets for
the same model do not create multiple cycle entries.
Use `/thinking` to lower effort for disposable work, or set it explicitly on an
agent call.
Terra and authenticated Go models remain selectable through `/model` or explicit
agent overrides.

`~/.pi/agent/settings.json` and the files in `~/.pi/agent/agents/` link to this repository's Pi configuration.
No installation or copy step is needed for edits to existing linked files.
Restart Pi to load the updated configuration.
Resumed sessions may restore their previously selected model and effort.

## Evidence and limits

The ladder was re-based on 16 September 2026 against Artificial Analysis Intelligence Index v4.3, the Coding Agent Index, LMArena text/WebDev, DesignArena, OpenAI's Codex credit rate card and the OpenCode Go usage-limit table. Full citations: `docs/research/openai-codex-models-2026-09.md`, `docs/research/opencode-go-models-2026-09.md`, `docs/research/designarena-2026-09.md`.
Arena and DesignArena scores are single-shot generations and do not measure tool use, repository grounding or multi-turn editing; harness experience overrides them.
Provider message estimates are not fixed limits or controlled comparisons between models.

- [Artificial Analysis methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking)
- [OpenCode Go usage limits](https://opencode.ai/docs/go/#usage-limits)
- [ChatGPT and Codex pricing](https://learn.chatgpt.com/docs/pricing)
