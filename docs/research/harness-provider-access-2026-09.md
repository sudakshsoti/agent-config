# Harness provider access — local probes (2026-09-16)

Local, first-party probes run from this checkout on 2026-09-16 to establish which
providers each installed harness can actually reach. Every row is a real request,
not a catalogue entry: `omp models` and `pi --list-models` list models the
harness *knows*, which is not the same as models it may *call*.

Probe commands (stdin closed; OMP retry disabled so a failure cannot hide behind
a fallback):

```bash
omp -p --model <id> --config <(printf 'retry:\n  enabled: false\n') "Reply with exactly: ok"
pi -p --no-session --no-tools --offline --model <id> "Reply with exactly: ok"
```

## Results

| Harness | Model id | Exit | Observed |
| --- | --- | --- | --- |
| OMP | `anthropic/claude-opus-5` | 0 | `ok` |
| OMP | `anthropic/claude-sonnet-5` | 0 | `ok` |
| OMP | `anthropic/claude-fable-5-1` | 0 | `ok` |
| OMP | `anthropic/claude-haiku-4-5` | 0 | `ok` |
| OMP | `openai-codex/gpt-5.6-luna` | 0 | `ok` (subscription dropped by the user; access is lapsing, not routed any more) |
| Pi | `anthropic/claude-opus-5` | 1 | HTTP 400 `invalid_request_error`: "Third-party apps now draw from your extra usage, not your plan limits. Add more at claude.ai/settings/usage and keep going." |
| Pi | `anthropic/claude-sonnet-5` | 1 | same HTTP 400 |
| Pi | `anthropic/claude-haiku-4-5` | 1 | same HTTP 400 |
| Pi | `openrouter/anthropic/claude-sonnet-5` | 1 | HTTP 401 `authentication_error`: "User not found." |
| Pi | `openrouter/anthropic/claude-opus-5` | 1 | HTTP 401 `authentication_error`: "User not found." |
| Pi | `openai-codex/gpt-5.6-luna` | 0 | `ok` |
| Pi | `opencode-go/glm-5.3-flash` | 0 | `ok` |
| Pi | `opencode-go/deepseek-v4.1-flash` | 0 | `ok` |
| Pi | `opencode-go/kimi-k3` | 0 | `ok` |
| Pi | `opencode-go/gpt-5.6-luna` | 0 | `ok` (Go resells Luna; unaffected by the ChatGPT subscription) |

`pi auth` reports credential types `openai-codex: oauth`, `opencode-go: api_key`,
`openrouter: api_key`, `anthropic: oauth` in `~/.pi/agent/auth.json` (not tracked
here). The Anthropic OAuth credential exists and is *accepted*; the request is
rejected at the plan level, which confirms the standing note about
`earendil-works/pi#3372`: an Anthropic subscription serves Claude Code/OMP but
bills third-party clients against an "extra usage" balance that is empty here.

## Consequences for routing

- Claude 5x is reachable **only from OMP**, where it runs on the subscription.
- Pi has **no** Claude path today: the subscription refuses third-party clients
  and the OpenRouter key is dead. Buying extra usage at
  `claude.ai/settings/usage`, or replacing the OpenRouter key, would restore one.
- Pi therefore routes entirely on OpenCode Go (flat $10/month, per-model monthly
  caps), which is the only fully working paid provider it has left.
- `openai-codex` is removed from routing in both harnesses and disabled in
  `omp/config.yml` so a lapsing account cannot be reached by fallback.
