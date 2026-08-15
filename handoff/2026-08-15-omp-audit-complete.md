---
title: OMP Audit — Complete
date: 2026-08-15
tags:
  - omp
  - handoff
  - ollama
  - local-models
status: complete-unpushed
supersedes:
  - "[[2026-08-15-omp-audit-execution-and-local-model]]"
  - "[[2026-08-15-omp-local-model-backout]]"
---

# Handoff — omp audit, done

Branch `omp-audit-followups` off `main`. **Working tree clean. 13 commits.
Nothing pushed. No PR.**

The two earlier handoffs from this session are superseded — both describe
half-finished states that were later resolved. This file is the truth.

> [!success] Nothing is broken or half-done
> `./install.sh` runs green (`linked=50`, exit 0). Local session titles work,
> verified against a real interactive session. The single next action below is
> optional.

## What this was

An audit of the `omp` (Oh My Pi v17.3.4) configuration, then execution of 8 of its
10 items, plus a local-model detour that landed. Full audit reasoning lives at
`~/.claude/plans/audit-my-omp-setup-twinkly-wreath.md`. A plain-English writeup for
a non-technical reader is committed at `docs/2026-08-15-omp-audit.md` — **that doc
predates the Ollama work and does not mention it.**

## The 13 commits

| Commit | What |
|---|---|
| `7c4297a` | Adversary's anchor check points at `grep`, not `read` — its `read` returns no line numbers, `grep` does. Also updated `docs/two-stage-plan-review.md`. |
| `820f917` | `install.sh` says when omp linking is skipped. Decided **not** to track `~/.omp/agent/mcp.json`; rationale in README. |
| `add84b5` | `retry.fallbackChains` reordered by remaining quota — OpenCode Go was at 86% weekly and first in the adversary's chain; now last everywhere. |
| `a8f4301` | `bashInterceptor.enabled: true`. **If an edit ever lands wrong, look here first** — 3 of 11 built-in rules reroute `sed -i`/`perl -i`/`awk -i inplace` to the fuzzy-matching `edit` tool. |
| `6ee3c80` | `display.showTokenUsage: true`. |
| `4beb648` | `prewalk` deliberately left off, reason recorded in-file. |
| `21528d6` | `skills.ignoredSkills` — Claude-Code-only skills no longer load into omp sessions. |
| `2ca5cfd` | `dev.autoqaConsent: denied`; `autolearn.autoContinue: false`; six generated skills moved out. |
| `b96bd4d` | `docs/2026-08-15-omp-audit.md` — reader-facing writeup. |
| `1b17e9d`, `f056a33` | Superseded handoffs from mid-session. |
| `0706cb7` | `omp/models.yml` — local Ollama provider for the tiny role. |
| `c474b30` | `modelRoles.tiny` → `ollama-local/qwen3.5:0.8b`. |
| `8c56c74` | `install.sh` step 3g symlinks `omp/models.yml`. |

## Decisions and why

- **Auto-QA off.** `dev.autoqaConsent: granted` (omp's default, never chosen) was
  auto-POSTing tool-issue reports to `https://qa.omp.sh/v1/grievances`, the upstream
  author's server. **12 reports had already gone**, each carrying a stable install UUID
  plus model-written free text that named internal tooling and local paths. Now
  `denied`. **`dev.autoqa` is deliberately left UNSET** — setting it `true` explicitly
  overrides the denial.
- **`autolearn.enabled` stays true, `autoContinue` goes false.** Six of nine generated
  skills were junk within three days, and they load at provider priority 5 in every
  session (discovery is *not* gated by `autolearn.enabled`). Killing `autoContinue`
  stops the unprompted capture turn; `enabled` preserves deliberate capture.
- **`mcp.json` not tracked.** No secret today, but omp *writes* it, so a future
  `omp mcp add` with an inline `env` key would put a live secret in the working tree.
  Both entries depend on local credential stores, so tracking moves zero working config.
- **0.8B, not 4B, for the tiny role.** A 4B was wired first. Then the machine's specs
  surfaced: **16GB Mac, swap at 10.6GB of 11GB, 13% memory free.** 4GB resident for
  3-6 word titles is the wrong trade. RAM was never checked before recommending it —
  that was the mistake. After backing out: 63% memory free, swap 4.9GB.
- **`ollama-local` is a full custom provider, not `modelOverrides` on omp's built-in
  `ollama`.** The built-in is discovery-backed and its cache went stale — after an
  `ollama rm` it still listed the deleted model. Hence `ollama-local/qwen3.5:0.8b`.
- **Ollama desktop app owns port 11434**, `brew services ollama` stopped. The two
  servers do **not** coexist. The app's login item had to be manually enabled or it
  would not survive reboot.

## Local model facts worth not rediscovering

- **omp fights its own thinking suppression.** A logging proxy in front of Ollama
  captured the real request: omp sends `reasoning_effort:"none"` from `extraBody`, then
  **also sends `preserve_thinking:true` and `chat_template_kwargs:{preserve_thinking:true}`
  of its own.** On the 4B those won and a title took 78s. On the 0.8B they don't. The
  working override (`preserve_thinking:false`) is recorded in `omp/models.yml` in case a
  future omp build regresses.
- Suppression needed **both** `reasoning: false` on the model (stops omp negotiating
  effort) **and** `extraBody.reasoning_effort: none` (switches it off at Ollama).
  `omp models` now shows the thinking column as `-`.
- **A Modelfile cannot turn thinking off.** It must go through the request body.
- **`omp -p` never generates titles.** Title generation only fires on the interactive
  path. Testing with `-p` would "prove" the feature broken when it is fine — verify
  under a PTY.
- `api: openai-completions` — **NOT** `openai-responses`. Wrong one garbles output with
  no clear error.
- Qwen3.5 default context is 4096 tokens. A 3,599-token prompt: 18.9s default vs 4.74s
  at `num_ctx: 8192`. Irrelevant for titles; relevant if you reuse this for articles.

## Corrections the execution made to the audit plan

- **`omp stats` does not hang.** No flags starts a dashboard web server by design.
  `omp stats -s` returns in 1.8s. The plan also blamed the wrong database files.
- **`omp gc` is dry-run by default.** Nothing moves without `--apply`.
- **Real cost:** gemini-3.7-flash, 7 requests, $0.233 = **~3.3¢ per adversary review**
  (plan guessed ~11¢). Lifetime all models: $78.37. OpenRouter promo expires
  **2026-12-31**, after which ~13¢.
- **`qwen3-1.7b` is a dead enum value** — disabled for local inference.

## Verified working

```
title-generator: success  provider:"ollama-local"  id:"qwen3.5:0.8b"
title:"Add retry to deployment webhook handler"
usage: input 199, output 12, cost total 0
```
0.47s warm. `./install.sh` → `linked=50 mirrored=37 skipped=0 copied=0 plugins=9 pruned=0`,
exit 0. All three symlinks resolve into the repo (`models.yml`, `config.yml`,
`agents/adversary.md`). INVARIANT block intact; only `tiny` changed.

## Not done, deliberately

- **`tools.approvalMode: yolo`** — omp auto-approves every tool call including shell
  execution, in every folder. omp's shipped default, never chosen. **Biggest open risk
  in the setup.** `write` mode prompts before `exec`.
- No calendar reminder for the 2026-12-31 promo expiry; no budget cap.
- Vibe mode, `task.isolation.mode`, `prewalk` — untouched on purpose.
- `retry.usageReservePolicy` left at `confirm` — `auto` is undocumented and guessing
  wrong could drain the near-empty OpenCode Go account.
- `omp gc --apply` not run. `omp gc --wal --apply` is the safe subset.

## Loose ends, none urgent

- **The 0.8B is 1.1GB resident, not the ~600MB estimated.** Above the threshold set for
  it. Unloads after 5 min idle. If it feels heavy on 16GB, revert `c474b30`.
- **548MB wasted** at `~/.omp/agent/cache/tiny-models/onnx-community/LFM2-700M-ONNX`.
  Safe to delete.
- **`qwen3.5:4b-mlx` (3.7GB) still on disk** for manual article summarising:
  `ollama run qwen3.5:4b-mlx`. omp does not touch it.
- **Six moved skills sit in a TEMPORARY scratchpad** at
  `/private/tmp/claude-501/-Users-sudakshsoti-dev-agent-config/07af758c-283f-4576-ab4c-b442d94fa7d0/scratchpad/managed-skills-removed/`.
  Restore: `mv <that path>/* ~/.omp/agent/managed-skills/`. Move them somewhere
  permanent or accept losing them.
- **`docs/2026-08-15-omp-audit.md` has no Ollama section.** It stops at the eight audit
  items.
- GUI chat in the Ollama app never verified — needs a human click.

## Editing rules that bit us

- `omp/config.yml` and `omp/models.yml` are **symlinked** into `~/.omp/agent/`; omp
  writes into the working tree. `git checkout omp/config.yml` is the undo.
- **Never `omp config set`** — it rewrites the file and may strip the INVARIANT comment
  block. Hand-edit YAML, verify with `omp config get`.
- **INVARIANT: no `anthropic/` selector anywhere in `retry.fallbackChains`.** A failed
  Claude call must never retry on Claude.
- `git commit -- <path> -m "msg"` **fails** (git reads `-m` as a pathspec after `--`).
  Use `git commit -m "msg" -- <path>`.

## Single next action

Push the branch and open a PR:

```
git push -u origin omp-audit-followups
```

Everything is committed and verified, so this is a review-and-merge, not more work.
While you are in there, consider adding an Ollama section to
`docs/2026-08-15-omp-audit.md` — it is the only stale artefact.
