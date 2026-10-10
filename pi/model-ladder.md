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
through to their Grok rungs instead of failing.

Grok (`xai`) needs its own `/login` → "xAI (Grok/X subscription)" per box;
`grok-4.7` is listed from Pi 1.1.0. Without it the Grok roles fall back to
Sonnet (review becomes Claude checking Claude), and the Grok-pinned agents
(`scout`, `Explore`, `reviewer`, `adversary`, `research`) fail, because agent
pins do not fall back.

## Ladder

| Task / agent | Provider and model | Effort |
| --- | --- | --- |
| Main session (`role/default`) | `anthropic/claude-sonnet-5-5` | medium |
| `builder` implementing an approved UI plan | `anthropic/claude-sonnet-5-5` | medium |
| `Plan` planning a screen or feature | `anthropic/claude-opus-5-5` | high |
| `task`, `workflow` and the unnamed `general-purpose` fallback | `anthropic/claude-sonnet-5-5` | medium |
| `security-reviewer` vulnerability discovery | `anthropic/claude-opus-5-5` | high |
| `Critic` visual review of implemented work | `anthropic/claude-opus-5-5` | medium |
| `code-worker` precisely scoped routine fixes, tests and mechanical refactors | `anthropic/claude-sonnet-5-5` | medium |
| `research` primary-source investigation and cited reports | `xai/grok-4.7` | high |
| `sonic` strictly mechanical updates | `anthropic/claude-haiku-5-5` | medium |
| `scout`, `Explore` and codebase discovery | `xai/grok-4.7` | low |
| `reviewer`, `adversary` hostile review on a second model lineage | `xai/grok-4.7` | high |

The role table itself (`default`, `task`, `plan`, `slow`, `sonic`,
`adversary`, `smol`, …) lives only in `pi/model-roles.json`; it follows OMP's
`modelRoles` except `default`, which is Sonnet here and Opus in OMP.

Rationale per model:

- **Claude (Sonnet 5.5 / Opus 5.5)** carries the main session, implementers,
  planners and security review, matching OMP's split: Sonnet for doing, Opus
  for planning and judgement. The cost is the impersonation route's ToS and
  breakage risk, accepted by the user.
- **Grok 4.7** (SuperGrok subscription) keeps the hostile second lineage, so
  review is never Claude checking Claude, plus `research` (X search) and
  discovery. Its weekly pool is shared with Grok Chat/Build/Bot and unpublished,
  so nothing else runs on it. It has a 500K context window.
- **Haiku 5.5** carries `sonic` and the cheap roles (`smol`, `tiny`, `commit`).
  Its context is 100K, so it never backs exploration or a long session.
- No OpenRouter rung: Pi cannot reach OpenRouter, so every chain ends on Claude
  or Grok.

## Fallback

Fallback is automatic for role selections, not for agent pins or physical
`/model` picks. Pi's own retry handles transient errors; after
`failuresBeforeFallback` consecutive failures the model is benched for
`cooldownMinutes` and the next rung answers. Quota, billing and auth errors
bench immediately and trigger one continuation on the next rung, at most
`maxFallbacksPerPrompt` times per prompt. A rung without credentials (Claude
before `/login anthropic`, Grok before the xAI login) is skipped.

Effort support: Grok 4.7 accepts `minimal` through `xhigh`; Haiku 5.5, Sonnet
5.5 and Opus 5.5 accept `low` through `max`. A role selection's effort
(`role/plan:high`) beats the effort written in the role table.

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

**It does not work until the credential exists.** Run `/login anthropic` in Pi;
it is an interactive browser flow and is per box, like every other login in
this repo.

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

The ladder was re-based on 10 October 2026 against the Artificial Analysis
Intelligence Index, the official Terminal-Bench 4.0 board, LMArena text/WebDev
and DesignArena, with local OMP probes of `claude-haiku-5-5`, `grok-4.7` and
the OpenRouter rungs the same day. Full citations:
`docs/research/ladder-benchmarks-2026-10.md`,
`docs/research/chatgpt-vs-supergrok-coding-2026-10.md`.
Arena and DesignArena scores are single-shot generations and do not measure tool
use, repository grounding or multi-turn editing; harness experience overrides
them.
Choosing SuperGrok over ChatGPT Plus, and keeping `code-worker` on Claude, are
user decisions (2026-10-10), not benchmark findings.

- [Artificial Analysis methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking)
- [xAI Grok FAQ](https://docs.x.ai/grok/faq)
