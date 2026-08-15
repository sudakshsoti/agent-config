---
title: OMP Audit Execution and Local Model Wiring
date: 2026-08-15
tags:
  - omp
  - handoff
  - local-models
  - ollama
status: in-progress
---

# Handoff — OMP audit execution + local model wiring

Branch: `omp-audit-followups` (off `main`). **Nothing pushed. No PR open.**

## What this was

An audit of the `omp` (Oh My Pi v17.3.4) configuration, then execution of 8 of its
10 items. Plan lives at
`~/.claude/plans/audit-my-omp-setup-twinkly-wreath.md`. A reader-facing writeup of
the whole thing is committed at `docs/2026-08-15-omp-audit.md` — that doc is the
better starting point for *why*; this file is the state.

Mid-run the scope grew: the user chose to run **Qwen3.5 4B locally via Ollama**,
both for omp's session titles and for ad-hoc article summarising.

## Committed — 9 commits, all verified by their workers

| Commit | What |
|---|---|
| `7c4297a` | Adversary's anchor check points at `grep`, not `read`. Its `read` returns no line numbers (no `edit` tool in session, `readLineNumbers: false`); `grep` does. Also updated `docs/two-stage-plan-review.md`. |
| `820f917` | `install.sh` now says when omp linking is skipped. Decided **not** to track `~/.omp/agent/mcp.json`; rationale in README "Secrets policy". |
| `add84b5` | `retry.fallbackChains` reordered by remaining quota. OpenCode Go was at 86% weekly and was first in the adversary's chain; now last everywhere. |
| `a8f4301` | `bashInterceptor.enabled: true`. Caveat comment in-file: 3 of 11 built-in rules reroute `sed -i`/`perl -i`/`awk -i inplace` to the fuzzy-matching `edit` tool. **Look here first if an edit lands wrong.** |
| `6ee3c80` | `display.showTokenUsage: true`. |
| `4beb648` | `prewalk` deliberately left **off**, reason recorded in-file. |
| `21528d6` | `skills.ignoredSkills` — Claude-Code-only skills no longer load into omp sessions. |
| `2ca5cfd` | `dev.autoqaConsent: denied`; `autolearn.autoContinue: false`; six auto-generated skills moved out. |
| `b96bd4d` | `docs/2026-08-15-omp-audit.md` — ELI12 writeup. |

## Decisions and why

- **`mcp.json` not tracked.** No secret in it today, but omp *writes* that file, so a
  future `omp mcp add` with an inline `env` key would put a live secret in the working
  tree. `sync.sh`'s strip-on-copy approach doesn't transfer to a symlinked file. And
  both entries depend on local credential stores, so tracking it moves zero working
  config. Documented in README so a future session doesn't "helpfully" track it.
- **`autolearn.enabled` stays true, `autoContinue` goes false.** Six of nine generated
  skills were junk within three days, and they load at provider priority 5 in every
  session (discovery is *not* gated by `autolearn.enabled`). Killing `autoContinue`
  stops the unprompted capture turn; leaving `enabled` on preserves deliberate capture.
- **`dev.autoqa` deliberately left UNSET.** Setting it to `true` explicitly overrides
  the `denied` consent. The denial only binds while the key is absent.
- **Ollama desktop app owns port 11434**, `brew services ollama` stopped. The two
  servers do not coexist — starting the formula service under the app put brew into
  `error 1`. The app's login item was disabled on install and had to be enabled
  manually, or it would not have survived a reboot.
- **`retry.usageReservePolicy` left at `confirm`.** A worker refused to guess between
  `auto` and `fail-closed`; the values are undocumented and guessing wrong could drain
  the near-empty OpenCode Go account.

## Corrections the execution made to the audit

- **`omp stats` does not hang.** With no flags it starts a dashboard web server and
  stays foreground by design. `omp stats -s` returns in 1.8s. The plan also blamed the
  wrong database files — it reads `~/.omp/stats.db`, not the agent-dir DBs.
- **`omp gc` is dry-run by default.** Nothing moves without `--apply`.
- **Real cost number:** gemini-3.7-flash, 7 requests, $0.233 = **~3.3¢ per adversary
  review** (the plan guessed ~11¢). Lifetime spend all models: $78.37. OpenRouter promo
  expires **2026-12-31**, after which a review is ~13¢.
- **`qwen3-1.7b` is a dead enum value** — `omp tiny-models list` shows it disabled for
  local inference (onnxruntime-node can't run that export's RotaryEmbedding updates).

## Local model — measured, and the numbers matter

Installed: Ollama 0.32.13 (MLX engine, default on Apple Silicon since v0.30),
model **`qwen3.5:4b-mlx`**, 3.7GB at `~/.ollama/models`.

Two findings that any wiring MUST handle:

1. **Thinking is on by default and it is brutal.** A 4-word title took **158 seconds**
   and 5,812 reasoning tokens. `"reasoning_effort": "none"` in the request body drops
   it to **~0.25s**. Confirmed NOT working: `"think": false` (hangs), `chat_template_kwargs`
   `enable_thinking: false` (still thinks, leaks a literal `</think>` into content),
   `"reasoning_effort": "low"` (hangs). Only `"none"`.
2. **Default context is 4096 tokens.** A 3,599-token prompt: 18.9s at default, **4.74s**
   at `num_ctx: 8192`.

Throughput: 36 tok/s generation, ~21,500 tok/s prompt processing. Titles 0.22–0.32s warm.

## Current state — IN FLIGHT, verify before trusting

A subagent was still running the omp wiring when this handoff was written. As of that
moment: **9 commits, clean tree, `omp/models.yml` does not exist, `modelRoles.tiny` is
still `openai-codex/gpt-5.6-luna:low`.**

That worker may have landed commits after this file was written. **Run
`git log --oneline main..HEAD` first** and reconcile against the table above.

It was briefed to produce three commits:
1. `omp/models.yml` — Ollama provider, `api: openai-completions` (**NOT** `openai-responses`;
   the wrong one garbles output with no clear error), `cost` all zeros, thinking
   suppressed via `compat.extraBody`, context raised past 4096.
2. `omp/config.yml` — `modelRoles.tiny: ollama/qwen3.5:4b-mlx`. Leave `providers.tinyModel`
   and `providers.autoThinkingModel` at `online`; per `docs/local-models.md` the online
   path prefers the `tiny` role, which is how this routes locally without touching the
   closed enums.
3. `install.sh` — symlink `omp/models.yml` to `~/.omp/agent/models.yml`.

## Not done, deliberately

- **Item 1, `tools.approvalMode: yolo`** — omp auto-approves every tool call including
  shell execution, in every folder. omp's shipped default, never a choice. **Biggest
  open risk.** `write` mode prompts before `exec`.
- **Item 2** — no calendar reminder for the 2026-12-31 promo expiry, no budget cap.
- **Vibe mode / `task.isolation.mode`** — untouched.
- **`omp gc --apply`** — not run. Dry run: 0 sessions archived, 4 blobs (701KB), 2.7MB
  WAL. `omp gc --wal --apply` is the safe subset.

## Loose ends

- **548MB of wasted download** at `~/.omp/agent/cache/tiny-models/onnx-community/LFM2-700M-ONNX`
  — an LFM2-700M fetched before the switch to Qwen3.5. Safe to delete.
- **Six moved skills sit in a TEMPORARY scratchpad** at
  `/private/tmp/claude-501/-Users-sudakshsoti-dev-agent-config/07af758c-283f-4576-ab4c-b442d94fa7d0/scratchpad/managed-skills-removed/`.
  Restore: `mv <that path>/* ~/.omp/agent/managed-skills/`. Scratchpads are temporary —
  move them somewhere permanent or accept losing them.
- **`docs/2026-08-15-omp-audit.md` predates the Ollama work** and needs a section on it.
- **GUI chat unverified.** The Ollama app is running and its server answers, but sending
  a message in the GUI needs a human click. Its DB shows 0 chats.

## Editing rules that bit us

- `omp/config.yml` is **symlinked** to `~/.omp/agent/config.yml`. omp writes into the
  working tree. `git checkout omp/config.yml` is the undo.
- **Never `omp config set`** — it rewrites the file and may strip the INVARIANT comment
  block at the top. Hand-edit the YAML, verify with `omp config get`.
- **INVARIANT: no `anthropic/` selector anywhere in `retry.fallbackChains`.** A failed
  Claude call must never retry on Claude.
- `git commit -- <path> -m "msg"` **fails** — git reads `-m` as a pathspec after `--`.
  Use `git commit -m "msg" -- <path>`.

## Single next action

Run `git log --oneline main..HEAD`. If the three wiring commits are absent or partial,
finish the wiring per the brief above and prove it with a timed `omp -p "say hi in
exactly two words"` that generates a title in under a second from the local model.
