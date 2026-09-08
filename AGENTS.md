# AGENTS.md

`CLAUDE.md` is `@AGENTS.md`; this file is the shared guide for every harness.

## What actually reaches Codex

- Skills live in `~/.agents/skills`, the shared cross-agent root. Editing a `SKILL.md` is live; rerun `./install.sh` only to add, rename, or delete one. Deletion requires `./install.sh --prune`; a plain run leaves dangling links and the retired skill in Codex's catalogue.
- **Never install skills into `~/.codex/skills`.** Codex scans both roots, so duplicates consume the 2% budget. `install.sh` removes marked `.agent-config-managed` copies there. Verify with `codex exec "list skill names"`; each name must appear once.
- Codex has no per-skill `skillOverrides`; `~/.codex/config.toml` only has `[plugins.<name>] enabled = true/false`. Every `skills/` description therefore counts for Codex.

## Claude-only — do not edit these as Codex

`agents/`, `settings.json`, `claude-powerline.json`, `plugins.txt`, `dist/`.

## Which repo owns what

`~/dev/agent-config` owns agent behaviour; `~/dev/dotfiles` owns the machine. Secrets belong in dotfiles (1Password + age), never agent-config. This table is duplicated in both repos; change both copies together.

| Path | Owner | Delivery |
| --- | --- | --- |
| `~/.claude/CLAUDE.md`, `skills/`, `agents/` | agent-config | `install.sh` symlinks; edits are live |
| `~/.claude/settings.json` | agent-config | copy-if-absent; `./sync.sh` pulls the live file back |
| `~/.claude/plugins/claude-hud/config.json` | **dotfiles** | chezmoi; exception under `~/.claude/` |
| `~/.agents/skills/` | agent-config | `install.sh` symlinks; Codex, opencode, omp, and pi read it |
| `~/.codex/AGENTS.md`, `~/.omp/agent/AGENTS.md`, `~/.config/opencode/AGENTS.md`, `~/.pi/agent/AGENTS.md` | agent-config | symlinks to `global-agents.md` |
| `~/.codex/config.toml` | **shared** | dotfiles writes it; agent-config merges non-secret keys; check both |
| `~/.omp/agent/config.yml`, `lsp.yml`, `keybindings.yml`, `themes/`, `agents/` | agent-config | `install.sh` symlinks; omp writes through links |
| `~/.pi/agent/settings.json`, `subagents.json`, `pi-fff.json`, `themes/`, `extensions/`, `agents/` | agent-config | `install.sh` symlinks; pi writes through links |
| `~/.config/omp/*.yml`, `*.tpl` | agent-config (`omp/overlays/`) | session-only `--config` overlays; no restore state |
| `~/.config/opencode/opencode.jsonc`, `~/.zshrc`, `.gitconfig`, Brewfile, fonts, terminal/editor config | **dotfiles** | chezmoi |
| `~/.omp/agent/mcp.json`, `.env`, `~/.claude/settings.local.json`, `~/.pi/agent/auth.json`, `models-store.json`, `sessions/`, `npm/` | **neither** | machine-local, credentials or runtime state; untracked |

- **Never let chezmoi claim an agent-config symlink.** A blind apply replaces it with a stale regular file. `.chezmoiignore` gates `.claude/CLAUDE.md`, `.claude/settings.json`, and `.config/omp`.
- **Never edit agent-config's `settings.json` directly.** It is a snapshot overwritten by `./sync.sh` from `~/.claude/settings.json`; edit the live file, then sync.

## Adding a skill or plugin: pick the lane

| Lane | Declared in | Reaches | Use |
| --- | --- | --- | --- |
| `external <owner/repo> [skill ...]` | `plugins.txt` | Claude, Codex, opencode, omp | Third-party skills; cloned to `vendor/`, materialised, and linked to `~/.claude/skills` and `~/.agents/skills` |
| `marketplace` + `plugin` | `plugins.txt` | Claude only | More than skills and ships `.claude-plugin/marketplace.json` |
| `skills/<name>/` | repo | Claude, Codex, opencode, omp | Repo-owned/editable; requires `dist/<name>.zip` and `scripts/lint-skills.py` |

- **Never `npx skills add`.** Its machine-local `~/.agents/.skill-lock.json` has no restore command and is invisible to this repo.
- A plain skills repo without `.claude-plugin/marketplace.json` is `external`, not a plugin. Plugins are Claude-only; use `external` or `skills/` when other harnesses must see a skill.
- Name requested skills on `external` lines; a bare repo imports every skill and can silently consume prompt budget.
- Every entry in `~/.claude/skills`, `~/.agents/skills`, `~/.config/opencode/skills`, and `~/.pi/agent/skills` must be a symlink. `install.sh` writes only the first two; opencode and pi read `~/.agents/skills`. Audit non-links with:
  `for r in ~/.claude/skills ~/.agents/skills ~/.config/opencode/skills ~/.pi/agent/skills; do [ -d "$r" ] || continue; for d in "$r"/*/; do [ -L "${d%/}" ] || echo "${d%/}"; done; done`
- `install.sh` cannot remove real directories with `--prune`; move them into a declared lane. Baseline's old links were removed by hand on 2026-09-07; disabling a Claude plugin never disables copies in other roots.
- `codebase-memory` is repo-owned in `skills/codebase-memory/`; its MCP server is separate and does not supply the skill.

## Gotchas

- macOS has no GNU `timeout`; use Python `subprocess.run(..., timeout=...)` or a background process plus `kill`.
- The pre-commit hook formats staged source in the working tree. After each commit, inspect `git status` and separate unrelated formatter changes.
- **Current plain OMP routing is authoritative in `omp/config.yml`:** `default`/`task` → `openai-codex/gpt-5.6-luna:high`; `plan`/`slow` → `gpt-5.6-sol:medium`; `designer`/`vision` → `gpt-5.6-sol:high`; `adversary`/`reviewer`/`security-reviewer`/`advisor` → `opencode-go/glm-5.3-flash:high`; `scout` → `opencode-go/deepseek-v4-flash:low`; `usageAwareFallback: false`; `codeMode: "off"`. Overlays differ.
- Non-interactive `omp -p` from a persistent kernel needs closed stdin (`stdin=DEVNULL` or `</dev/null`); otherwise it waits at `readPipedInput`.
- `omp` is the binary, not a restoring wrapper. `ompgo` and `ompcodex` pass session-only `--config` overlays; never add persistent apply/restore state.
- Thinking levels are model-specific: `deepseek-v4-flash`, `glm-5.3-flash`, and `kimi-k3` expose only low/high/max; `medium` silently runs as high.
- omp rewrites `omp/config.yml` and removes comments while preserving values; keep rationale in `docs/`.
- Only `~/.omp/agent/AGENTS.md` survives omp context priority over `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`; all five harness paths must symlink to `global-agents.md`.
- Claude `settings.json` flows live → repo only: `~/.claude/settings.json` is authoritative; `./sync.sh` sanitises and pulls it back. `install.sh` copies it only when the destination is absent.
- `link_into` refuses real non-symlink destinations and prints `SKIP`; `--prune` removes only dangling symlinks. `install.sh` refuses temporary worktrees matching `*/.git/worktrees/*` or `*/worktrees/*` unless `--force`; always install from `~/dev/agent-config`.
- A bare `omp -p --model <id>` can hide model failures behind fallback. Probe with retry disabled: `omp -p --model <id> --config <(printf 'retry:\n  enabled: false\n') "Reply with exactly: ok"`.
- `retry.fallbackChains` specificity is exact model → provider key → role → default. `provider/*` is a chain key, not a rung; as a rung it preserves the model id and can build an invalid gateway id.
- omp loads `~/.omp/.env` at startup; an existing process variable wins. After `op inject`, restart omp. `omp token <provider>` shows the key actually used.
- Muse Spark requires `/v1/responses` and omp ≥18.1.6; the installed omp is 18.1.14. Pi's catalogue has `api: openai-responses` at `https://opencode.ai/zen/go/v1`. No plain-OMP role currently uses Muse Spark; `omp/overlays/go-overlay.yml` may.
- pi has no omp-style `modelRoles` or `fallbackChains`; per-job models are in `pi/agents/*.md` frontmatter. Its default is `openai-codex/gpt-5.6-luna`, and it has no Anthropic subscription model.
- Pi's OpenCode Go/OpenRouter credentials are API keys in untracked `~/.pi/agent/auth.json`; `openai-codex` uses OAuth. Never add an `anthropic/*` subscription model to pi: Anthropic rejects third-party subscription OAuth (`earendil-works/pi#3372`).
- `~/.omp/stats.db` stopped recording around 2026-09-02 19:04; use live `model_perf` in `~/.omp/agent/agent.db` for served-model evidence.
