# Pi model ladder: research-backed proposal

Research date: 2026-09-08.

## Recommendation

Use Pi as a manual ladder, not an automatic router.
Keep `gpt-5.6-luna` at `high` as the daily driver; change model only when the work crosses a clear boundary.
This preserves the Codex subscription for visual implementation and uses OpenCode Go for short, low-judgement work.

| Rung | Model and effort | Use it for | Do not use it for |
| --- | --- | --- | --- |
| 1 — scout | `opencode-go/deepseek-v4-flash` at `low` | Locate files, trace one flow, inspect a log, answer a bounded factual question. | Architecture, review, visual judgement, edits. |
| 2 — daily builder | `openai-codex/gpt-5.6-luna` at `high` | Most UX implementation: build a component, inspect its local render or screenshot, make a focussed multi-file change, test and iterate. | Product direction that is still ambiguous; a final release decision. |
| 3 — contained hard problem | `openai-codex/gpt-5.6-terra` at `medium` | Debug a stubborn but bounded failure, implement a well-specified feature, review a single change set. | Open-ended research, broad design direction, repetitive work. |
| 4 — design-critical pass | `openai-codex/gpt-5.6-sol` at `xhigh` | Turn a settled visual brief into a plan; assess screenshots across breakpoints; resolve interaction, accessibility, hierarchy or information-architecture trade-offs; final pre-ship critique. | First-pass file scouting or mechanical edits. |
| 5 — cheap bulk helper | `opencode-go/muse-spark-1.3-contributor` at `minimal` | Mechanical changes with explicit acceptance criteria: rename, format, test data, repetitive migration, small isolated fix. | Exploration, visual work, reviews, or work where it must notice what is missing. |
| Escape hatch | OpenRouter, manually selected | A necessary model/provider is unavailable from Codex or Go, or you need an independent second opinion on a design-critical problem. | Automatic recovery from an ordinary Pi failure. |

This matches the current Pi model list in `pi/settings.json`: Luna, Terra, Sol, DeepSeek Flash and Muse Spark are already enabled. The existing `scout` agent is correctly pinned to DeepSeek at `low`.

## How to move up the ladder

Start at the lowest rung that can see the relevant evidence.
Move up once, not repeatedly, when any of these are true:

- You need to compare screenshots, mobile and desktop states, or type and spacing decisions.
- The task changes more than one user journey or has unclear product behaviour.
- The first attempt fails because the agent did not form a workable plan, not because of a simple implementation mistake.
- The work will be expensive to undo: public copy, data handling, authentication, payments, destructive migration, or a release decision.

At `Sol xhigh`, supply the visual evidence and ask for a written decision before edits.
At `Luna high`, ask it to implement that decision and inspect the result.
This separates taste from execution, which matters more for visual product work than shaving a few seconds off each task.

## Effort rules

OpenAI's current guidance is to begin at the default effort and raise it only when deeper planning or analysis is needed; higher effort takes longer and uses more tokens.
The mapping above follows that rule: `low` for factual scouts, `medium` for a bounded task, `high` for normal agentic builds, and `xhigh` only for consequential judgement.

Pi can save a per-model effort preference through `modelThinkingLevels`, so the practical setup is one remembered effort per rung rather than changing the level on every task.

## OpenCode Go controls

OpenCode Go is a $10/month service with five-hour, weekly and monthly value limits; request volume varies by model cost.
Its documentation also says Pi is a validated client that sends session information, helping routing and prompt caching.
Use it for the two narrow roles above, rather than treating Go as a free replacement for the strongest Codex work.

The Go catalogue changes, so verify a proposed new Go model in Pi's `/models` before adding it to the ladder.

## OpenRouter: safety and cost policy

1. Do not configure OpenRouter as Pi's default or automatic failure path. Pi retries the same model; it does not have cross-model fallback chains. A failed Pi task should prompt a conscious model choice.
2. Use a separate OpenRouter key with a small hard monthly limit and no auto-top-up. Treat it as a paid exception budget, not spare subscription capacity.
3. Before choosing a paid model, name the reason in the prompt: independent review, long context, vision comparison, or provider outage. If there is no reason, go back to Luna or Sol.
4. For private repositories, enable OpenRouter's data-collection denial and Zero Data Retention (ZDR) where the chosen model has an eligible endpoint. ZDR may exclude providers, and it does not cover third-party tools such as web search.
5. If you ever use OpenRouter model fallbacks, cap the list at one primary plus one approved alternative and record the final returned model. OpenRouter can fall back on rate limits, downtime, moderation and context errors, so an invisible fallback can change both quality and spend.

## Sources

- [OpenAI: model choices and reasoning effort](https://learn.chatgpt.com/docs/models) — current descriptions for Sol, Terra and Luna; higher effort is for deeper analysis and costs more time/tokens.
- [Pi settings](https://pi.dev/docs/latest/settings) — startup model, per-model thinking levels and available effort values.
- [OpenCode Go](https://opencode.ai/docs/go) — available catalogue, Pi validation, session/prompt-cache guidance and current usage limits.
- [OpenRouter model fallbacks](https://openrouter.ai/docs/guides/routing/model-fallbacks) — fallbacks can trigger on rate limits, downtime, moderation and context errors.
- [OpenRouter ZDR](https://openrouter.ai/docs/guides/features/zdr) — ZDR enforcement and its third-party-tool limitation.
- [OpenRouter provider routing](https://openrouter.ai/docs/guides/routing/provider-selection) — routing preferences and hard price caps.

## What this deliberately does not decide

This is a role and effort policy, not a configuration change.
Before changing `pi/settings.json`, choose the OpenRouter monthly limit and whether an independent critique should use a specific paid OpenRouter model.
