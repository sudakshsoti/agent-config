# AGENTS.md

This file is the project instructions for *this checkout*. The shared,
harness-neutral preferences that install into OMP and Pi live in
`global-agents.md` — do not confuse the two.

## What this repo installs

`./install.sh` writes to exactly three places:

| Destination | Source | Delivery |
| --- | --- | --- |
| `~/.agents/skills/` | `skills/`, `vendor/` | symlink per skill; both OMP and Pi read this one root |
| `~/.omp/agent/` + `~/.config/omp/` | `omp/`, `global-agents.md` | symlink per file; OMP writes through the links |
| `~/.pi/agent/` | `pi/`, `global-agents.md` | symlink per file; Pi writes through the links |

`pi/web-search.json` is the one **merge**, not a link: the live file is also
pi-web-access's credential store, so only repo-owned keys are pushed.

- Skills are linked **once**, into `~/.agents/skills`. Never also link
  `~/.pi/agent/skills` — a skill discovered in two roots is listed twice and
  burns double its share of the context budget.
- A skill, agent, prompt or config edit is live immediately, because
  everything is a symlink. There is no sync step in either direction.
- OMP and Pi rewrite some of their own config, and the write follows the link
  into this checkout. **Check `git diff` before committing** after changing a
  setting interactively — `pi/settings.json` and `omp/config.yml` are the usual
  suspects.
- `./install.sh --prune` clears managed links that are no longer declared. It
  only removes symlinks pointing into this checkout and copies carrying the
  `.agent-config-managed` marker; unmarked real files and directories are left
  alone with a warning.
- `./install.sh --skills-only=name,other-name` links only the named repo-owned
  skills into `~/.agents/skills`, with no config writes and no external fetches.
- `--no-external` skips the external git fetch; relinking still runs, so an
  offline re-run repairs links from what is already cloned.
- `install.sh` refuses paths matching `*/.git/worktrees/*` or `*/worktrees/*`
  unless `--force`, because symlinks bake in an absolute path that vanishes with
  an ephemeral worktree.

## Ownership

`~/dev/agent-config` owns agent behaviour; `~/dev/dotfiles` owns the machine.
Secrets belong in dotfiles (1Password + age), never here.

| Path | Owner | Notes |
| --- | --- | --- |
| `skills/`, `plugins.txt` | agent-config | source-only; no packaged artifact |
| `global-agents.md` | agent-config | linked to `~/.omp/agent/AGENTS.md` and `~/.pi/agent/AGENTS.md` |
| `omp/config.yml`, `lsp.yml`, `keybindings.yml`, `themes/`, `agents/`, `overlays/` | agent-config | OMP writes through the links |
| `pi/settings.json`, `subagents.json`, `pi-fff.json`, `keybindings.json`, `prompts/`, `themes/`, `extensions/`, `agents/` | agent-config | Pi writes through the links |
| `pi/web-search.json` | **shared** | merged: credentials and unmanaged keys stay machine-local |
| `~/.omp/agent/mcp.json`, `~/.omp/agent/extensions/`, `~/.pi/agent/auth.json`, `~/.pi/agent/models-store.json`, `~/.pi/agent/sessions/`, `~/.pi/agent/npm/` | **neither** | credentials or runtime state; untracked |
| `~/.local/bin/omp-*-overlay`, `~/.zshrc`, Brewfile, fonts | **dotfiles** | chezmoi |
| `scripts/` | agent-config | checks and installer helpers, referenced from `check.sh` |

## Skills

- Repo-owned skills live in `skills/<name>/SKILL.md` and are editable here.
  Third-party sources are `external` lines in `plugins.txt`, cloned into the
  ignored `vendor/` and vendored **by reference only**.
- `name` must equal the directory, be lowercase kebab-case, and contain no
  `claude` or `anthropic`. A multi-line `description` must use a block scalar
  (`|` or `>-`); a bare unquoted multi-line description containing a colon-space
  parses as a nested mapping and the skill fails to load.
- `python3 scripts/lint-skills.py` enforces all of that **and** that the bullet
  list in `skills/README.md` matches the source directories. Adding or renaming
  a skill without editing that list is a failure, not drift to be noticed later.
- Never `npx skills add`. Its machine-local `~/.agents/.skill-lock.json` has no
  restore command and is invisible to this repo.
- Name the skills you want on an `external` line. A bare repo imports every
  skill it ships and can silently consume the shared context budget.
- Every entry in `~/.agents/skills` must be a symlink. Audit non-links with:
  `for d in ~/.agents/skills/*/; do [ -L "${d%/}" ] || echo "${d%/}"; done`
- `codebase-memory` is repo-owned in `skills/codebase-memory/`; its MCP server is
  separate and does not supply the skill.

## Gotchas

- In the current Pi package layout, `pi-playwright`'s `pw.js` expects an
  uninstalled package-local CLI; the working hoisted executable is
  `~/.pi/agent/npm/node_modules/.bin/playwright-cli`. Use `--browser=chromium`
  for the installed browser instead of assuming system Chrome exists.
- macOS has no GNU `timeout`; use Python `subprocess.run(..., timeout=...)` or a
  background process plus `kill`.
- The pre-commit hook formats staged source in the working tree. After each
  commit, inspect `git status` and separate unrelated formatter changes.
- **Current plain OMP routing is authoritative in `omp/config.yml`:** `default`/`task` → `openai-codex/gpt-5.6-luna:high`; `plan`/`slow` → `gpt-5.6-sol:medium`; `designer`/`vision` → `gpt-5.6-sol:high`; `adversary`/`reviewer`/`security-reviewer`/`advisor` → `opencode-go/glm-5.3-flash:high`; `scout` → `opencode-go/deepseek-v4-flash:low`; `usageAwareFallback: false`; `codeMode: "off"`. Overlays differ.
- Non-interactive `omp -p` from a persistent kernel needs closed stdin (`stdin=DEVNULL` or `</dev/null`); otherwise it waits at `readPipedInput`.
- `omp` is the binary, not a restoring wrapper. Overlays are passed per session with `--config`; never add persistent apply/restore state.
- Thinking levels are model-specific: `deepseek-v4-flash`, `glm-5.3-flash`, and `kimi-k3` expose only low/high/max; `medium` silently runs as high.
- OMP rewrites `omp/config.yml` and removes comments while preserving values; keep rationale in `design/decisions.md` or here, never in that file.
- A bare `omp -p --model <id>` can hide model failures behind fallback. Probe with retry disabled: `omp -p --model <id> --config <(printf 'retry:\n  enabled: false\n') "Reply with exactly: ok"`.
- `retry.fallbackChains` specificity is exact model → provider key → role → default. `provider/*` is a chain key, not a rung; as a rung it preserves the model id and can build an invalid gateway id.
- OMP loads `~/.omp/.env` at startup; an existing process variable wins. After `op inject`, restart OMP. `omp token <provider>` shows the key actually used.
- Muse Spark requires `/v1/responses` and omp ≥18.1.6; the installed omp is 18.1.14. Pi's catalogue has `api: openai-responses` at `https://opencode.ai/zen/go/v1`. No plain-OMP role currently uses Muse Spark; `omp/overlays/go-overlay.yml` may.
- Pi has no OMP-style `modelRoles` or `fallbackChains`; per-job models are in `pi/agents/*.md` frontmatter. Its default is `openai-codex/gpt-5.6-luna`, and it has no Anthropic subscription model. Pi routing: main/builder → Luna high; code-worker → DeepSeek V4.1 Flash high for precisely scoped routine implementation; scout/Explore → Muse Spark 1.3 minimal for low-stakes read-only discovery; research → Muse Spark 1.3 high for primary-source investigation; workflow → Sol medium; Plan/Critic → Sol high. Use Luna medium when discovery needs stronger judgement or involves sensitive code. Sol xhigh is an explicit escalation; Go is optional, not the default implementation budget.
- Pi's `enabledModels` is the Ctrl+P cycle list, not an access restriction. It deduplicates by provider/model ID, retaining the first effort preset; use `/thinking` or explicit agent thinking overrides rather than duplicate scoped entries.
- On pi-web-access 0.23.0 in this setup, `summaryModel` must be a bare `provider/id`: a `:high`-style suffix matches nothing and silently drops the override. Tested `opencode-go/muse-spark-1.3-contributor` and `opencode-go/deepseek-v4.1-flash` resolve but return empty responses; `openai-codex/gpt-5.6-luna` produces a real summary. With no `summaryModel`, `workflow: "auto-summary"` degrades to a deterministic snippet list because neither preferred summary model is enabled.
- Pi's OpenCode Go/OpenRouter credentials are API keys in untracked `~/.pi/agent/auth.json`; `openai-codex` uses OAuth. Never add an `anthropic/*` subscription model to Pi: Anthropic rejects third-party subscription OAuth (`earendil-works/pi#3372`).
- `~/.omp/stats.db` stopped recording around 2026-09-02 19:04; use live `model_perf` in `~/.omp/agent/agent.db` for served-model evidence.
- Another process may push to the active feature branch between local commits. Fetch before pushing; if the remote advanced, preserve unrelated dirty files, rebase, then restore them.
- `npm ci` restores the ignored `node_modules/` (it carries `pi-token-speed`, consumed by `pi/settings.json`). Never commit it.
