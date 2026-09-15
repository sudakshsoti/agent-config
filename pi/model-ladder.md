# Pi model ladder

Use OpenCode Go aggressively for bounded discovery, routine implementation and
first-pass review. Reserve Codex for sustained implementation, visual judgement,
or difficult architecture and security decisions.

| Task / agent | Provider and model | Effort |
| --- | --- | --- |
| Main session; `builder` implementing an approved UI plan | `openai-codex/gpt-5.6-luna` | high |
| `code-worker` precisely scoped routine fixes, tests and mechanical refactors | `opencode-go/muse-spark-1.3-contributor` | xhigh |
| `scout`, `Explore` and private codebase discovery | `opencode-go/muse-spark-1.3-contributor` | xhigh |
| `research` primary-source investigation and cited reports | `opencode-go/muse-spark-1.3-contributor` | xhigh |
| unnamed `general-purpose` fallback | `openai-codex/gpt-5.6-luna` | medium |
| `workflow` coordinating multi-part implementation | `openai-codex/gpt-5.6-sol` | medium |
| `Plan` and `Critic` planning and visual review | `openai-codex/gpt-5.6-sol` | high |
| `reviewer` adversarial review of plans and diffs on a second model lineage | `opencode-go/muse-spark-1.3-contributor` | xhigh |
| Difficult bugs, architecture or security-sensitive decisions | Explicit `openai-codex/gpt-5.6-sol` override | xhigh |
| Optional `public-scout`, public/disposable material only | `opencode-go/muse-spark-1.3-contributor` | minimal |

Use Muse xhigh for bounded work where a deeper pass improves completeness:
repository exploration, routine code-worker changes, cited research and
first-pass review. Keep public disposable lookups minimal.
Use Luna for the main implementation session and builder. Use Sol for visual
critique, workflow coordination and difficult architecture or security work.
Keep at least one independent review path when the implementation itself runs
on Muse.
Escalate repeated failed approaches instead of allowing an extended retry loop.
GLM 5.3 Flash exposes only low, high and max thinking; medium silently runs as high.
DeepSeek V4.1 Flash exposes only high and max thinking, so it is not used for
minimal-effort scouting.
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

The ladder was informed by Artificial Analysis Intelligence Index v4.3 API data and provider usage documentation checked on 9 September 2026.
Benchmark scores do not measure visual-design judgement or accepted changes per unit of subscription quota.
Provider message estimates are not fixed limits or controlled comparisons between models.

- [Artificial Analysis methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking)
- [OpenCode Go usage limits](https://opencode.ai/docs/go/#usage-limits)
- [OpenAI Work and Codex usage guidance](https://help.openai.com/en/articles/20001516)
