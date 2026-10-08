# Pi model ladder

Pi selects models by **role**. `pi/extensions/model-roles` registers each entry
of `pi/model-roles.json` `roles` as a virtual model `role/<name>`, so
`pi/settings.json` (default and `enabledModels`), `pi/web-search.json`
`summaryModel` and `pi/plannotator.json` phases all name a role, not a model.
Before every request the extension walks the role's fallback chain
(`chains`, keyed by exact model like OMP's `retry.fallbackChains`) and picks
the first model that has credentials and is not benched. `/roles` shows the
live chain; `/roles reset` clears the bench. Agents in `pi/agents/` still pin
physical models.

**Claude is the default** (user decision 2026-10-09, `design/decisions.md`
"Pi Claude default"): `role/default` and `role/task` resolve to Sonnet 5.5 and
`role/plan`/`role/slow` to Opus 5.5. Pi reaches Claude only through the
`@gotgenes/pi-anthropic-auth` impersonation extension — see
[Reaching Claude from Pi](#reaching-claude-from-pi). On a box without
`/login anthropic` every Claude rung lacks credentials, so the roles fall
through to their OpenCode Go rungs instead of failing.

**Guardrail:** `muse-spark-*-contributor` is Meta training-eligible and not
zero-data-retention — prompts and completions may be used for training. It
backs `code-worker`, `research`, `sonic`, `public-scout` and `role/sonic`. Any
session that will touch private, client or sensitive material MUST avoid those
and stay on Claude, GLM 5.3 Flash or DeepSeek V4.1 Flash.

## Ladder

| Task / agent | Provider and model | Effort |
| --- | --- | --- |
| Main session (`role/default`) | `anthropic/claude-sonnet-5-5` | medium |
| `builder` implementing an approved UI plan | `anthropic/claude-sonnet-5-5` | medium |
| `Plan` planning a screen or feature | `anthropic/claude-opus-5-5` | high |
| `task`, `workflow` and the unnamed `general-purpose` fallback | `anthropic/claude-sonnet-5-5` | medium |
| `security-reviewer` vulnerability discovery | `anthropic/claude-opus-5-5` | high |
| `Critic` visual review of implemented work | `anthropic/claude-opus-5-5` | medium |
| `code-worker` precisely scoped routine fixes, tests and mechanical refactors | `opencode-go/muse-spark-1.3-contributor` | high |
| `research` primary-source investigation and cited reports | `opencode-go/muse-spark-1.3-contributor` | high |
| `sonic` strictly mechanical updates | `opencode-go/muse-spark-1.3-contributor` | low |
| Optional `public-scout`, public/disposable material only | `opencode-go/muse-spark-1.3-contributor` | minimal |
| `scout`, `Explore` and codebase discovery | `opencode-go/glm-5.3-flash` | low |
| `reviewer`, `adversary` hostile review on a second model lineage | `opencode-go/glm-5.3-flash` | high |

The role table itself (`default`, `task`, `plan`, `slow`, `sonic`,
`adversary`, `smol`, …) lives only in `pi/model-roles.json`; it follows OMP's
`modelRoles` except `default`, which is Sonnet here and Opus in OMP.

Rationale per model:

- **Claude (Sonnet 5.5 / Opus 5.5)** carries the main session, implementers,
  planners and security review, matching OMP's split: Sonnet for doing, Opus
  for planning and judgement. The cost is the impersonation route's ToS and
  breakage risk, accepted by the user.
- **Muse Spark 1.3 Contributor** keeps the cheap, high-volume agents. It is the
  cheapest per request on Go and sits on the largest quota.
- **GLM 5.3 Flash** keeps discovery and the hostile second lineage, so review
  is never Claude checking Claude. It is ZDR on Go.
- **DeepSeek V4.1 Flash** has no pin; it is a chain rung under Sonnet, Haiku
  and GLM.
- **Kimi K3 is not routed at all.** Its ~490 requests/month cap is the scarcest
  on Go and the user judged the cost unjustified — a cost decision, not a
  benchmark finding.

## Fallback

Fallback is automatic for role selections, not for agent pins or physical
`/model` picks. Pi's own retry handles transient errors; after
`failuresBeforeFallback` consecutive failures the model is benched for
`cooldownMinutes` and the next rung answers. Quota, billing and auth errors
bench immediately and trigger one continuation on the next rung, at most
`maxFallbacksPerPrompt` times per prompt. A rung without credentials (the
`openrouter` one, or Claude before `/login anthropic`) is skipped.

Effort support: GLM 5.3 Flash and Kimi K3 accept only low/high/max; medium runs
as high. DeepSeek V4.x Flash accepts low, high and max. Muse Spark 1.3 accepts
`minimal` through `xhigh`. A role selection's effort (`role/plan:high`) beats
the effort written in the role table.

## Scoped models

`settings.json` sets the default (checked against the Main session row):

<!-- routing:current -->
`main` → `anthropic/claude-sonnet-5-5` medium
<!-- routing:end -->

`enabledModels` is the Ctrl+P cycle: `role/default`, `role/task`,
`role/plan`, `role/slow`, `role/sonic`, `role/adversary`, `role/smol` and
`role/tiny`, each with its own effort. It is a quick-switch list, not an access
restriction. Plannotator's planning phase uses `role/plan` high and its
executing phase `role/default` medium (`pi/plannotator.json`).

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

When it is live, Claude is the default model (see the top of this file).
`scripts/check-model-routing.py` allows `anthropic/*` anywhere Pi selects a
model — agent pins, the default, `enabledModels`, `summaryModel` and role
targets, with `role/*` resolved through `pi/model-roles.json` — only while the
package is listed in the tracked `pi/settings.json` `packages[]`. Removing the
package turns every Claude route into a hard check failure rather than a silent
wrong route.

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

OMP remains the Claude harness on the subscription proper. Full evidence and
the ToS/breakage caveats: `docs/research/pi-claude-subscription-2026-10.md`.

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
