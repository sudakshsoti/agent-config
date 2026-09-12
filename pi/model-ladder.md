# Pi model ladder

Prioritise ChatGPT/Codex quota for sustained work.
Keep OpenCode Go for occasional, bounded work rather than default implementation.
These are starting defaults, not measured quota savings on this repository.

| Task / agent | Provider and model | Effort |
| --- | --- | --- |
| Main session; `builder` implementing an approved UI plan | `openai-codex/gpt-5.6-luna` | high |
| `code-worker` precisely scoped routine fixes, tests and mechanical refactors | `opencode-go/deepseek-v4.1-flash` | high |
| `scout`, `Explore` and `research` bounded read-only discovery | `opencode-go/muse-spark-1.3-contributor` | minimal |
| unnamed `general-purpose` fallback | `openai-codex/gpt-5.6-luna` | medium |
| `workflow` coordinating multi-part implementation | `openai-codex/gpt-5.6-sol` | medium |
| `Plan` and `Critic` planning and visual review | `openai-codex/gpt-5.6-sol` | high |
| `reviewer` adversarial review of plans and diffs on a second lineage | `opencode-go/glm-5.3-flash` | high |
| Difficult bugs, architecture or security-sensitive decisions | Explicit `openai-codex/gpt-5.6-sol` override | xhigh |
| Optional `public-scout`, public/disposable material only | `opencode-go/muse-spark-1.3-contributor` | minimal |

Use Luna medium for discovery that needs stronger judgement or involves sensitive code.
Use Muse minimal for bounded, low-stakes read-only discovery.
Use Sol medium when implementation still requires substantial technical decisions.
Escalate repeated failed approaches instead of allowing an extended retry loop.
GLM 5.3 Flash exposes only low, high and max thinking; medium silently runs as high.
DeepSeek V4.1 Flash exposes only high and max thinking, so it is not used for minimal-effort scouting.
Model overrides on agent calls take precedence over agent defaults; these files do not implement automatic escalation or quota-based routing.

## Scoped models

`settings.json` sets `enabledModels` to Luna high, DeepSeek V4.1 Flash high, Sol high and Muse Spark 1.3 minimal, in that order.
This is the Ctrl+P quick-switch list, not an access restriction or an agent-routing table.
Pi deduplicates scoped entries by provider/model ID; multiple effort presets for the same model do not create multiple cycle entries.
Use `/thinking` to change effort, or set it explicitly on an agent call.
Terra and authenticated Go models remain selectable through `/model` or explicit agent overrides.

`~/.pi/agent/settings.json` and the files in `~/.pi/agent/agents/` link to this repository's Pi configuration.
No installation or copy step is needed for edits to existing linked files.
Restart Pi to load the updated configuration.
Resumed sessions may restore their previously selected model and effort.

## Evidence and limits

The ladder was informed by Artificial Analysis Intelligence Index v4.3 API data and provider usage documentation checked on 9 September 2026.
Benchmark scores do not measure visual-design judgement or accepted changes per unit of subscription quota.
Provider message estimates are not fixed limits or controlled comparisons between models.

- [Artificial Analysis methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking)
- [OpenCode Go usage limits](https://opencode.ai/docs/go/#usage-limits)
- [OpenAI Work and Codex usage guidance](https://help.openai.com/en/articles/20001516)
