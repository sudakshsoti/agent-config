---
title: OMP Audit — Local Model Backout and Half-Wired State
date: 2026-08-15
tags:
  - omp
  - handoff
  - ollama
  - local-models
status: blocked-dirty-tree
supersedes: "[[2026-08-15-omp-audit-execution-and-local-model]]"
---

# Handoff — omp audit done, local model wiring backed out mid-flight

Branch: `omp-audit-followups` off `main`. **Nothing pushed. No PR.**

> [!danger] Read this first
> The working tree is **dirty and broken**. Uncommitted edits point omp's `tiny`
> model role at `ollama-local/qwen3.5-4b-omp` — **a model that no longer exists**.
> It was deleted during a backout. Do not run `./install.sh` or start an omp
> session expecting titles to work until this is resolved.

## Current state

```
 M install.sh
 M omp/config.yml      <- modelRoles.tiny = ollama-local/qwen3.5-4b-omp (DELETED MODEL)
?? omp/models.yml      <- untracked, defines the ollama provider
```

Ten commits are clean and good. The dirty files above are the **abandoned 4B wiring**.

`ollama list` shows only `qwen3.5:4b-mlx` (4.0GB). The derivative `qwen3.5-4b-omp`
was removed. `qwen3.5:0.8b` was **never pulled** — a subagent was mid-redirect when
the session ended.

## The ten good commits

| Commit | What |
|---|---|
| `7c4297a` | Adversary's anchor check points at `grep`, not `read`. Its `read` returns no line numbers; `grep` does. Also updated `docs/two-stage-plan-review.md`. |
| `820f917` | `install.sh` says when omp linking is skipped. Decided **not** to track `~/.omp/agent/mcp.json`; rationale in README. |
| `add84b5` | `retry.fallbackChains` reordered by remaining quota — OpenCode Go was at 86% weekly and first in the adversary's chain; now last everywhere. |
| `a8f4301` | `bashInterceptor.enabled: true`. **If an edit ever lands wrong, look here first** — 3 of 11 rules reroute `sed -i`/`perl -i`/`awk -i inplace` to the fuzzy-matching `edit` tool. |
| `6ee3c80` | `display.showTokenUsage: true`. |
| `4beb648` | `prewalk` deliberately left off, reason in-file. |
| `21528d6` | `skills.ignoredSkills` — Claude-Code-only skills no longer load into omp. |
| `2ca5cfd` | `dev.autoqaConsent: denied`; `autolearn.autoContinue: false`; six generated skills moved out. |
| `b96bd4d` | `docs/2026-08-15-omp-audit.md` — reader-facing writeup. |
| `1b17e9d` | Earlier handoff. **Now stale** — it still describes wiring the 4B. |

Full audit reasoning: `~/.claude/plans/audit-my-omp-setup-twinkly-wreath.md`.

## Why the local model was backed out

A 4B was wired for omp session titles. Then the machine's actual specs surfaced:
**16GB Mac, swap at 10.6GB of 11GB, 13% memory free.** A 4GB model resident for
3-6 word titles is the wrong trade on that hardware. RAM was never checked before
recommending it — that was the mistake.

Force-killed the model runners: **13% → 79% memory free**, swap 10.6GB → 6.7GB,
macOS shrank the swapfile 11GB → 8GB. Ollama server (PID 4334) and app (512) remain,
idle, holding no model.

**User's instruction: stop the 4B, keep only the `tiny` role, nothing else.**
The 4B stays on disk for manual article summarising via `ollama run qwen3.5:4b-mlx`.

## Local model facts worth not rediscovering

- Ollama 0.32.13, **desktop app owns port 11434**. `brew services ollama` is stopped —
  the two servers do **not** coexist (starting the formula under the app gives
  `brew services` `error 1`). The app's login item had to be manually enabled or it
  would not survive reboot.
- **Thinking is on by default and it is brutal.** A 4-word title took **158 seconds**
  and 5,812 reasoning tokens. `"reasoning_effort": "none"` in the request body drops it
  to ~0.25s. Confirmed NOT working: `"think": false` (hangs), `chat_template_kwargs`
  `enable_thinking: false` (still thinks, leaks a literal `</think>` into content),
  `"reasoning_effort": "low"` (hangs). **A Modelfile cannot turn thinking off** — this
  must go through the request body.
- Default context is 4096 tokens. A 3,599-token prompt: 18.9s default vs 4.74s at
  `num_ctx: 8192`.
- `api: openai-completions` — **NOT** `openai-responses`. Wrong one garbles output with
  no clear error.
- Model files live at `~/.ollama/models` (3.7GB). Derivatives share blobs and cost no
  extra disk.

## Corrections the execution made to the audit

- **`omp stats` does not hang.** No flags starts a dashboard web server by design.
  `omp stats -s` returns in 1.8s. The plan also blamed the wrong database files.
- **`omp gc` is dry-run by default.** Nothing moves without `--apply`.
- **Real cost:** gemini-3.7-flash, 7 requests, $0.233 = **~3.3¢ per adversary review**
  (plan guessed ~11¢). Lifetime all models: $78.37. OpenRouter promo expires
  **2026-12-31**, after which ~13¢.
- **`qwen3-1.7b` is a dead enum value** — disabled for local inference.

## Not done, deliberately

- **`tools.approvalMode: yolo`** — omp auto-approves every tool call including shell
  execution, in every folder. omp's shipped default, never chosen. **Biggest open risk.**
- No calendar reminder for the 2026-12-31 promo expiry; no budget cap.
- Vibe mode, `task.isolation.mode`, `prewalk` — all untouched on purpose.
- `retry.usageReservePolicy` left at `confirm` — `auto` is undocumented and guessing
  wrong could drain the near-empty OpenCode Go account.
- `omp gc --apply` not run. `omp gc --wal --apply` is the safe subset.

## Loose ends

- **548MB wasted** at `~/.omp/agent/cache/tiny-models/onnx-community/LFM2-700M-ONNX`.
  Safe to delete.
- **Six moved skills sit in a TEMPORARY scratchpad** at
  `/private/tmp/claude-501/-Users-sudakshsoti-dev-agent-config/07af758c-283f-4576-ab4c-b442d94fa7d0/scratchpad/managed-skills-removed/`.
  Restore: `mv <that path>/* ~/.omp/agent/managed-skills/`. Move them somewhere
  permanent or accept losing them.
- `docs/2026-08-15-omp-audit.md` predates all Ollama work and needs a section.
- GUI chat never verified — needs a human click in the Ollama app.

## Editing rules that bit us

- `omp/config.yml` is **symlinked** to `~/.omp/agent/config.yml`; omp writes into the
  working tree. `git checkout omp/config.yml` is the undo.
- **Never `omp config set`** — it rewrites the file and may strip the INVARIANT comment
  block. Hand-edit YAML, verify with `omp config get`.
- **INVARIANT: no `anthropic/` selector in `retry.fallbackChains`.**
- `git commit -- <path> -m "msg"` **fails** (git reads `-m` as a pathspec). Use
  `git commit -m "msg" -- <path>`.

## Single next action

Decide the dirty tree, then act:

**Option A (recommended, matches the user's "tiny role only"):** keep the local wiring
but shrink the model. `ollama pull qwen3.5:0.8b` (~600MB), fix `omp/config.yml` so
`modelRoles.tiny` names that real model, keep `omp/models.yml` and the `install.sh`
step, then commit the three files. Prove it with a timed
`omp -p "say hi in exactly two words"` producing a title in under a second, and report
`ollama ps` resident size — **if it exceeds ~1GB, stop and reconsider on a 16GB box.**

**Option B:** abandon local models entirely.
`git checkout -- install.sh omp/config.yml && rm omp/models.yml`. Ten commits stay,
tree goes clean, `tiny` returns to `openai-codex/gpt-5.6-luna:low`.

Do **not** leave it as-is. The current tree points at a deleted model.
