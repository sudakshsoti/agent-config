# AGENTS.md

This file applies to this checkout. Shared, harness-neutral preferences live in
`global-agents.md` and are installed into OMP and Pi; do not confuse the two.

## What this repo installs

`./install.sh` writes to exactly these destinations:

| Destination | Source | Delivery |
| --- | --- | --- |
| `~/.agents/skills/` | `skills/`, `vendor/` | one symlink per skill; filled only when a shared-root consumer exists |
| `~/.omp/agent/` + `~/.config/omp/` | `omp/`, `global-agents.md` | one symlink per file; OMP writes through links |
| `~/.pi/agent/` | `pi/`, `global-agents.md` | one symlink per file; Pi writes through links |

`pi/web-search.json` is the one **merge**, not a link: it is also
pi-web-access's credential store, so only repo-owned keys are pushed.

- Link skills **once** into `~/.agents/skills`; never also link
  `~/.pi/agent/skills` or skills are discovered twice and consume double the
  context budget. Codex and OpenCode read this shared root natively; this repo
  only checks their directories and writes no config for them.
- Edits are live through symlinks; there is no sync step. OMP and Pi can rewrite
  linked config in this checkout. **Check `git diff` before committing** after
  interactive setting changes; `pi/settings.json` and `omp/config.yml` are the
  usual suspects.
- `--prune` removes only managed links pointing into this checkout and copies
  marked `.agent-config-managed`; unmarked real files/directories are left with
  a warning.
- `--skills-only=name,other-name` links only named repo-owned skills, with no
  config writes or external fetches. It cannot be combined with `--prune`.
- Full, `--skills-only` and `--prune` runs share the
  `shared_root_consumers_present` predicate: one of `~/.omp/agent`,
  `~/.pi/agent`, `~/.codex` or `~/.config/opencode` must exist. With none,
  `~/.agents` is not created and `--prune` skips the shared root.
- `--no-external` skips external git fetches but still relinks existing clones.
- Install refuses paths matching `*/.git/worktrees/*` or `*/worktrees/*`, and
  refuses a linked `git worktree add` checkout when `rev-parse --git-dir` and
  `--git-common-dir` differ. Both guards exit 1 with `linked worktree` and are
  overridden by `--force`; symlinks contain absolute paths that would dangle.
  Git older than 2.31 falls back when `--path-format=absolute` is unavailable;
  if Git cannot answer, only the path guard remains.

## Ownership

`~/dev/agent-config` owns agent behaviour; `~/dev/dotfiles` owns the machine.
Secrets belong in dotfiles (1Password + age), never here.

| Path | Owner | Notes |
| --- | --- | --- |
| `skills/`, `plugins.txt` | agent-config | source-only; no packaged artifact |
| `global-agents.md` | agent-config | linked to `~/.omp/agent/AGENTS.md` and `~/.pi/agent/AGENTS.md` |
| `omp/config.yml`, `lsp.yml`, `keybindings.yml`, `themes/`, `agents/`, `overlays/` | agent-config | OMP writes through links |
| `pi/settings.json`, `subagents.json`, `pi-fff.json`, `keybindings.json`, `prompts/`, `themes/`, `extensions/`, `agents/` | agent-config | Pi writes through links |
| `pi/web-search.json` | **shared** | merged; credentials and unmanaged keys stay machine-local |
| `~/.omp/agent/mcp.json`, `~/.omp/agent/extensions/`, `~/.pi/agent/auth.json`, `~/.pi/agent/models-store.json`, `~/.pi/agent/sessions/`, `~/.pi/agent/npm/` | **neither** | credentials or runtime state; untracked |
| `~/.local/bin/omp-*-overlay`, `~/.zshrc`, Brewfile, fonts | **dotfiles** | chezmoi |
| `scripts/` | agent-config | checks and installer helpers, referenced by `check.sh` |

## Skills

- Repo-owned skills are `skills/<name>/SKILL.md`; `external` lines in
  `plugins.txt` clone third-party sources into ignored `vendor/`, vendored by
  reference only. A bare external repo imports every skill and can consume the
  shared context budget; name only the skills wanted on an `external` line.
- Skill `name` must equal its directory, be lowercase kebab-case, and contain
  neither `claude` nor `anthropic`. Multi-line descriptions require `|` or `>-`;
  an unquoted colon-space can parse as a nested mapping and break loading.
- `python3 scripts/lint-skills.py` enforces these rules and synchronizes the
  `skills/README.md` list, including its sentence stating the count of 34
  repo-owned skills. `python3 scripts/check-manifest.py` (run by `check.sh`)
  rejects malformed `plugins.txt` lines and duplicate external allowlisting;
  `scripts/manifest.py` is the shared parser.
- `scripts/ownership_collisions.py` (tested by `check.sh`) detects chezmoi
  entries claiming install destinations.
- `python3 scripts/audit-local.py [--home DIR] [--dotfiles DIR] [--json]` is an
  opt-in, read-only, offline local drift audit; it exits 0 with findings and is
  not run by `check.sh`.
- Never `npx skills add`: its machine-local `~/.agents/.skill-lock.json` has no
  restore command and is invisible to this repo. Every `~/.agents/skills/*`
  entry must be a symlink; audit with:
  `for d in ~/.agents/skills/*/; do [ -L "${d%/}" ] || echo "${d%/}"; done`
- `codebase-memory` is repo-owned in `skills/codebase-memory/`; its MCP server
  is separate and does not supply the skill.

## Gotchas

- `pi-playwright`'s `pw.js` expects an uninstalled package-local CLI. Use the
  hoisted `~/.pi/agent/npm/node_modules/.bin/playwright-cli` with
  `--browser=chromium`; do not assume system Chrome.
- macOS has no GNU `timeout`; use Python `subprocess.run(..., timeout=...)` or a
  background process plus `kill`.
- The repo-local `.githooks/pre-commit` runs fast checks; `scripts/check.sh` runs
  the full set. After commits, inspect `git status` for unrelated changes.
- **Plain OMP routing is authoritative in `omp/config.yml`:**

  | Roles/settings | Value |
  | --- | --- |
  | `default`/`task` | `openai-codex/gpt-5.6-luna:high` |
  | `plan`/`slow` | `openai-codex/gpt-5.6-sol:medium` |
  | `designer`/`vision` | `openai-codex/gpt-5.6-sol:high` |
  | `adversary`/`reviewer`/`security-reviewer`/`advisor` | `opencode-go/glm-5.3-flash:high` |
  | `scout` | `opencode-go/deepseek-v4-flash:low` |
  | `usageAwareFallback` / `codeMode` | `false` / `"off"` |

  Overlays differ. `omp -p` from a persistent kernel needs closed stdin
  (`stdin=DEVNULL` or `</dev/null`) or it waits at `readPipedInput`.
- `omp` is the binary, not a restoring wrapper; pass overlays per session with
  `--config`, never add persistent apply/restore state. Thinking levels are
  model-specific: `deepseek-v4-flash`, `glm-5.3-flash`, and `kimi-k3` expose
  only low/high/max; `medium` silently runs as high.
- OMP rewrites `omp/config.yml` and removes comments while preserving values;
  keep rationale in `design/decisions.md` or here, never in that file. A bare
  `omp -p --model <id>` can hide failures behind fallback; probe with retry
  disabled:
  `omp -p --model <id> --config <(printf 'retry:\n  enabled: false\n') "Reply with exactly: ok"`
- `retry.fallbackChains` specificity is exact model → provider key → role →
  default. `provider/*` is a chain key, not a rung; as a rung it preserves the
  model id and can build an invalid gateway id. OMP loads `~/.omp/.env` at
  startup and existing process variables win; after `op inject`, restart OMP.
  `omp token <provider>` shows the key actually used.
- Muse Spark requires `/v1/responses` and omp ≥18.1.6; installed omp is 18.1.21.
  Pi's catalogue uses `api: openai-responses` at
  `https://opencode.ai/zen/go/v1`. No plain OMP role uses Muse Spark;
  `omp/overlays/go-overlay.yml` may.
- Pi has no OMP-style `modelRoles` or `fallbackChains`; per-job models are in
  `pi/agents/*.md` frontmatter. Default is `openai-codex/gpt-5.6-luna`.
  Routing: main/builder → Luna high; code-worker → DeepSeek V4.1 Flash high
  for precise routine work; scout/Explore → Muse Spark 1.3 minimal; research →
  Muse Spark 1.3 high; workflow → Sol medium; Plan/Critic → Sol high. Use Luna
  medium for sensitive or judgement-heavy discovery; Sol xhigh is explicit
  escalation; Go is optional, not the default implementation budget.
- Pi `enabledModels` is the Ctrl+P cycle list, not an access restriction. It
  deduplicates by provider/model ID, retaining the first effort preset; use
  `/thinking` or explicit agent thinking overrides instead of duplicate entries.
  OpenCode Go/OpenRouter credentials are API keys in untracked
  `~/.pi/agent/auth.json`; `openai-codex` uses OAuth. Never add an
  `anthropic/*` subscription model to Pi: Anthropic rejects third-party
  subscription OAuth (`earendil-works/pi#3372`).
- Fetch before pushing. If another process advanced the branch, preserve
  unrelated dirty files, rebase, then restore them.
- `scripts/check.sh` bootstraps ignored `node_modules/` with `npm ci` when
  `node_modules/@earendil-works/pi-tui` is missing; it carries `pi-token-speed`,
  consumed by `pi/settings.json`. Never commit `node_modules/`.

## Agent skills

### Issue tracker

Issues live in GitHub Issues and use the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Use `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and
`wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

The previously documented root `CONTEXT.md` and `docs/adr/` are absent in this
checkout; do not assume they exist.
